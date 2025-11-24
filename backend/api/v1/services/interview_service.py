from __future__ import annotations

import asyncio
import logging
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.config import settings
from core.exceptions import BadRequestException, NotFoundException
from db.models import (
    ChatMessage,
    CodeTestResult,
    CodeTestResultStatus,
    Interview,
    InterviewStatus,
    InterviewStep,
    InterviewStepStatus,
    InterviewStepType,
    MessageSender,
)

from api.v1.services.message_service import MessageService

logger = logging.getLogger(__name__)


class InterviewService:
    """Сервис для работы с интервью."""

    def __init__(self) -> None:
        self.message_service = MessageService()

    async def create_interview(
        self,
        db: AsyncSession,
        user_id: UUID,
        job_role_description: str,
        amount_of_tasks: int,
    ) -> Interview:
        """Создание нового интервью."""
        interview = Interview(
            user_id=user_id,
            job_role_description=job_role_description,
            amount_of_tasks=amount_of_tasks,
            current_step_index=0,
            status=InterviewStatus.IN_PROGRESS,
        )
        db.add(interview)
        await db.flush()

        step = InterviewStep(
            interview_id=interview.id,
            type=InterviewStepType.DIALOG,
            status=InterviewStepStatus.IN_PROGRESS,
            question_text="Здравствуйте! Я ваш виртуальный интервьюер. Расскажите, пожалуйста, о себе.",
        )
        db.add(step)
        await db.flush()

        message = ChatMessage(
            interview_id=interview.id,
            sender=MessageSender.AI,
            text="Здравствуйте! Я ваш виртуальный интервьюер. Расскажите, пожалуйста, о себе.",
        )
        db.add(message)
        await db.commit()

        # Перезагружаем интервью с загрузкой всех отношений
        return await self.find_interview_by_id(db, interview.id, None)

    async def find_all_user_interviews(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Interview]:
        """Получение всех интервью пользователя."""
        result = await db.execute(
            select(Interview)
            .where(Interview.user_id == user_id)
            .options(
                selectinload(Interview.steps).selectinload(InterviewStep.code_task),
                selectinload(Interview.steps).selectinload(
                    InterviewStep.code_test_results
                ),
                selectinload(Interview.chat_messages),
            )
            .order_by(Interview.created_at.desc())
        )
        return list(result.scalars().all())

    async def find_interview_by_id(
        self,
        db: AsyncSession,
        interview_id: UUID,
        user_id: UUID | None = None,
    ) -> Interview:
        """Получение интервью по ID."""
        query = select(Interview).where(Interview.id == interview_id)
        if user_id:
            query = query.where(Interview.user_id == user_id)

        result = await db.execute(
            query.options(
                selectinload(Interview.steps).selectinload(InterviewStep.code_task),
                selectinload(Interview.steps).selectinload(
                    InterviewStep.code_test_results
                ),
                selectinload(Interview.chat_messages),
            )
        )
        interview = result.scalar_one_or_none()

        if not interview:
            error_msg = f'Интервью с ID "{interview_id}" не найдено'
            if user_id:
                error_msg += " или не принадлежит пользователю."
            else:
                error_msg += "."
            raise NotFoundException(error_msg)

        return interview

    async def handle_chat_message(
        self,
        db: AsyncSession,
        interview_id: UUID,
        sender: MessageSender,
        text: str,
    ) -> Interview:
        """Сохранение сообщения чата в БД."""
        interview = await self.find_interview_by_id(db, interview_id, None)

        if interview.status in [
            InterviewStatus.COMPLETED,
            InterviewStatus.CANCELLED,
        ]:
            raise BadRequestException(
                "Интервью уже завершено или отменено. Новые сообщения не принимаются."
            )

        await self.message_service.create_chat_message(
            db, str(interview_id), sender, text
        )

        await db.commit()
        db.expire_all()
        return await self.find_interview_by_id(db, interview_id, None)

    async def submit_code(
        self,
        db: AsyncSession,
        interview_id: UUID,
        step_id: UUID,
        user_code: str,
    ) -> Interview:
        """Сохранение кода для шага интервью в БД."""
        interview = await self.find_interview_by_id(db, interview_id, None)

        if interview.status != InterviewStatus.IN_PROGRESS:
            raise BadRequestException(
                "Невозможно отправить код: интервью не в процессе."
            )

        current_step = next((s for s in interview.steps if s.id == step_id), None)

        if not current_step or current_step.type != InterviewStepType.CODE_TASK:
            raise BadRequestException(
                "Текущий шаг не является кодовой задачей или шаг не найден."
            )
        if not current_step.code_task:
            raise BadRequestException("Кодовая задача для текущего шага не определена.")

        current_step.user_code = user_code
        current_step.status = InterviewStepStatus.IN_PROGRESS

        test_cases = current_step.code_task.test_cases
        if isinstance(test_cases, list):
            import random

            result = await db.execute(
                select(CodeTestResult).where(
                    CodeTestResult.interview_step_id == step_id
                )
            )
            for old_result in result.scalars().all():
                await db.delete(old_result)
            await db.flush()

            mock_test_results = [
                CodeTestResult(
                    interview_step_id=step_id,
                    test_id=test_case.get("id", f"test_{i}"),
                    status=(
                        CodeTestResultStatus.PASSED
                        if random.random() > 0.5
                        else CodeTestResultStatus.FAILED
                    ),
                    details=(
                        "Error: division by zero" if random.random() > 0.7 else None
                    ),
                )
                for i, test_case in enumerate(test_cases)
            ]

            for test_result in mock_test_results:
                db.add(test_result)

        await db.commit()
        await db.refresh(interview)
        return await self.find_interview_by_id(db, interview_id, None)

    async def _transcribe_audio(self, audio_buffer: bytes) -> str:
        """Распознавание аудио в текст с помощью AssemblyAI API."""
        api_key = settings.ASSEMBLYAI_API_KEY

        if not api_key:
            raise BadRequestException("ASSEMBLYAI_API_KEY не установлен.")

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                upload_response = await client.post(
                    "https://api.assemblyai.com/v2/upload",
                    content=audio_buffer,
                    headers={
                        "Authorization": api_key,
                        "Content-Type": "application/octet-stream",
                    },
                )
                upload_response.raise_for_status()
                upload_url = upload_response.json()["upload_url"]

                transcript_response = await client.post(
                    "https://api.assemblyai.com/v2/transcript",
                    json={"audio_url": upload_url, "language_code": "ru"},
                    headers={
                        "Authorization": api_key,
                        "Content-Type": "application/json",
                    },
                )
                transcript_response.raise_for_status()
                transcript_id = transcript_response.json()["id"]

                transcript: str | None = None
                attempts = 0
                max_attempts = 30

                while not transcript and attempts < max_attempts:
                    await asyncio.sleep(1)

                    status_response = await client.get(
                        f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                        headers={"Authorization": api_key},
                    )
                    status_response.raise_for_status()
                    status_data = status_response.json()

                    if status_data["status"] == "completed":
                        transcript = status_data["text"]
                    elif status_data["status"] == "error":
                        raise RuntimeError(status_data.get("error", "Unknown error"))

                    attempts += 1

                if not transcript:
                    raise BadRequestException(
                        "Транскрипция заняла слишком много времени."
                    )

                return transcript.strip()

        except Exception as e:
            logger.error(f"AssemblyAI API error: {str(e)}", exc_info=True)
            raise BadRequestException(
                "Ошибка при распознавании через AssemblyAI."
            ) from e

    async def handle_audio_message(
        self,
        db: AsyncSession,
        interview_id: UUID,
        audio_file: bytes,
        content_type: str,
    ) -> Interview:
        """Обработка аудио сообщения: транскрипция и сохранение в БД."""
        allowed_mime_types = [
            "audio/webm",
            "audio/mpeg",
            "audio/mp3",
            "audio/wav",
            "audio/ogg",
            "audio/m4a",
        ]

        if not audio_file:
            raise BadRequestException("Аудио файл не был загружен.")

        if content_type not in allowed_mime_types:
            raise BadRequestException(
                f"Неподдерживаемый формат аудио: {content_type}. Поддерживаемые форматы: {', '.join(allowed_mime_types)}"
            )

        max_size_bytes = 25 * 1024 * 1024
        if len(audio_file) > max_size_bytes:
            raise BadRequestException(
                f"Размер файла превышает максимально допустимый (25MB). Текущий размер: {len(audio_file) / 1024 / 1024:.2f}MB"
            )

        interview = await self.find_interview_by_id(db, interview_id, None)

        if interview.status in [
            InterviewStatus.COMPLETED,
            InterviewStatus.CANCELLED,
        ]:
            raise BadRequestException(
                "Интервью уже завершено или отменено. Новые сообщения не принимаются."
            )

        logger.debug(
            f"Обработка аудио файла для интервью {interview_id}. Размер: {len(audio_file)} байт, тип: {content_type}"
        )

        transcribed_text = await self._transcribe_audio(audio_file)

        if not transcribed_text or not transcribed_text.strip():
            raise BadRequestException(
                "Не удалось распознать речь в аудио. Попробуйте записать еще раз."
            )

        await self.message_service.create_chat_message(
            db, str(interview_id), MessageSender.USER, transcribed_text
        )

        await db.commit()
        # Очищаем кэш сессии, чтобы получить свежие данные из БД
        db.expire_all()
        # Перезагружаем интервью с актуальными данными
        return await self.find_interview_by_id(db, interview_id, None)
