from __future__ import annotations

import asyncio
import logging
import random
from uuid import UUID
import uuid
from typing import Any

from fastapi import UploadFile
import httpx
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from core.services.base import BaseDbModelService
from core.services.ml_client import MLClient
from core.dto.interview import InterviewSchema, ListInterviewItemSchema
from core.config.config import settings
from infrastructure.errors.base import BadRequestException, NotFoundException
from infrastructure.database.models.models import (
    ChatMessage,
    CodeTask,
    CodeTestResult,
    CodeTestResultStatus,
    Interview,
    InterviewStatus,
    InterviewStep,
    InterviewStepStatus,
    InterviewStepType,
    MessageSender,
)

logger = logging.getLogger(__name__)


class InterviewService(BaseDbModelService[Interview]):
    def __init__(self, session, ml_client: MLClient | None = None):
        """Инициализация сервиса интервью."""
        super().__init__(session)
        self.ml_client = ml_client

    async def create_interview(
        self,
        user_id: UUID,
        job_role_description: str,
        amount_of_tasks: int,
        key_skills: list[str] | None = None,
        preferences: str | None = None,
    ) -> InterviewSchema:
        public_token = str(uuid.uuid4())
        
        interview = Interview(
            user_id=user_id,
            creator_id=user_id,
            job_role_description=job_role_description,
            amount_of_tasks=amount_of_tasks,
            key_skills=key_skills or [],
            preferences=preferences,
            current_step_index=0,
            status=InterviewStatus.IN_PROGRESS,
            public_token=public_token,
        )
        self.session.add(interview)
        await self.session.flush()

        # Вызываем ML API для получения первого шага
        # Используем interview.id как session_id для согласованности
        session_id = str(interview.id)
        
        ml_response = await self.ml_client.start_interview(
            job_title=job_role_description,
            required_skills=key_skills or [],
            amount_of_tasks=amount_of_tasks,
            session_id=session_id,
        )
        
        # ML API возвращает session_id и step
        step_data = ml_response.get("step", {})
        
        await self._process_ml_step(interview, step_data)
        await self.session.commit()
        await self.session.refresh(interview)

        interview = await self.find_interview_by_id(interview.id, None)
        return InterviewSchema.model_validate(interview, from_attributes=True)

    async def _process_ml_step(self, interview: Interview, step_data: dict[str, Any]):
        """Обработка шага от ML сервиса: создание InterviewStep и ChatMessage."""
        step_type = step_data.get("type", "DIALOG")
        question_text = step_data.get("question_text", "")
        ai_feedback = step_data.get("ai_feedback", "")
        
        # Текст сообщения от AI - это вопрос или фидбэк
        message_text = question_text or ai_feedback
        
        if not message_text and step_type == "DIALOG":
             message_text = "Здравствуйте! Готовы начать?"

        # Создаем шаг интервью
        step = InterviewStep(
            interview_id=interview.id,
            type=InterviewStepType(step_type),
            status=InterviewStepStatus.IN_PROGRESS,
            question_text=message_text,
        )
        self.session.add(step)
        
        # Создаем сообщение от AI
        if message_text:
            message = ChatMessage(
                interview_id=interview.id,
                sender=MessageSender.AI,
                text=message_text,
            )
            self.session.add(message)
            
        await self.session.flush()

    async def find_all_user_interviews(
        self,
        user_id: UUID,
    ) -> list[ListInterviewItemSchema]:
        result = await self.session.execute(
            select(
                Interview,
                func.count(InterviewStep.id).label("steps_count"),
                func.count(ChatMessage.id).label("chat_messages_count"),
            )
            .join(InterviewStep, InterviewStep.interview_id == Interview.id)
            .join(ChatMessage, ChatMessage.interview_id == Interview.id)
            .where(Interview.user_id == user_id)
            .group_by(Interview.id)
            .order_by(Interview.created_at.desc())
        )
        interviews = result.all()
        interviews_list = []
        for interview, steps, chat_messages in interviews:
            interview.steps_count = steps
            interview.chat_messages_count = chat_messages
            interviews_list.append(ListInterviewItemSchema.model_validate(interview, from_attributes=True))
        return interviews_list

    async def find_interview_by_token(
        self,
        public_token: str,
    ) -> Interview:
        """Поиск интервью по публичному токену."""
        result = await self.session.execute(
            select(Interview)
            .where(Interview.public_token == public_token)
            .options(
                selectinload(Interview.steps).selectinload(InterviewStep.code_task),
                selectinload(Interview.steps).selectinload(
                    InterviewStep.code_test_results
                ),
                selectinload(Interview.chat_messages),
            )
        )
        interview = result.scalar_one_or_none()
        if not interview:
            raise NotFoundException("Интервью не найдено.")
        return interview

    async def claim_interview(
        self,
        public_token: str,
        user_id: UUID,
    ) -> Interview:
        result = await self.session.execute(
            select(Interview)
            .where(Interview.public_token == public_token)
        )
        interview = result.scalar_one_or_none()
        
        if not interview:
            raise NotFoundException("Интервью не найдено.")
        
        if interview.user_id == user_id:
            raise BadRequestException("Вы уже приняли приглашение.")
        
        interview.user_id = user_id
        await self.session.commit()
        await self.session.refresh(interview)
        
        interview = await self.find_interview_by_id(interview.id, None)
        return InterviewSchema.model_validate(interview, from_attributes=True)

    async def find_interview_by_id(
        self,
        interview_id: UUID,
        user_id: UUID | None = None,
    ) -> Interview:
        query = select(Interview).where(Interview.id == interview_id)
        if user_id:
            query = query.where(or_(Interview.user_id == user_id, Interview.creator_id == user_id))

        result = await self.session.execute(
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
        interview_id: UUID,
        sender: MessageSender,
        text: str,
    ) -> Interview:
        interview = await self.find_interview_by_id(interview_id, None)

        if interview.status in [
            InterviewStatus.COMPLETED,
            InterviewStatus.CANCELLED,
        ]:
            raise BadRequestException(
                "Интервью уже завершено или отменено. Новые сообщения не принимаются."
            )

        # Сохраняем сообщение пользователя
        user_message = ChatMessage(
            interview_id=interview_id,
            sender=sender,
            text=text,
        )
        self.session.add(user_message)
        await self.session.flush()

        # Используем interview.id как session_id (должен совпадать с тем, что был передан при создании)
        session_id = str(interview_id)
        
        # Вызываем ML API для обработки ответа
        ml_response = await self.ml_client.process_message(
            session_id=session_id,
            user_answer=text,
        )
        
        # Обновляем текущий шаг
        await self._update_current_step(interview, ml_response, text)
        
        status = ml_response.get("status", "IN_PROGRESS")
        
        if status != "COMPLETED":
            # Если интервью продолжается - создаем новый шаг
            await self._process_ml_step(interview, ml_response)
            interview.current_step_index += 1
        else:
            # Интервью завершено
            interview.status = InterviewStatus.COMPLETED
            interview.total_score = ml_response.get("score")
            interview.overall_feedback = ml_response.get("ai_feedback") or ml_response.get("feedback")
            
            # Добавляем финальное сообщение от AI (фидбэк)
            final_message_text = ml_response.get("ai_feedback") or ml_response.get("feedback")
            if final_message_text:
                final_message = ChatMessage(
                    interview_id=interview.id,
                    sender=MessageSender.AI,
                    text=final_message_text,
                )
                self.session.add(final_message)

        await self.session.commit()
        return await self.find_interview_by_id(interview_id, None)

    async def _update_current_step(self, interview: Interview, ml_response: dict[str, Any], user_answer: str):
        """Обновляет текущий шаг интервью результатами ответа пользователя."""
        current_step = next(
            (s for s in interview.steps if s.status == InterviewStepStatus.IN_PROGRESS),
            None
        )
        
        if current_step:
            current_step.status = InterviewStepStatus.COMPLETED
            current_step.user_answer = ml_response.get("user_answer", user_answer)
            current_step.feedback = ml_response.get("feedback")
            current_step.score = ml_response.get("score")
            await self.session.flush()

    async def submit_code(
        self,
        interview_id: UUID,
        step_id: UUID,
        user_code: str,
    ) -> Interview:
        interview = await self.find_interview_by_id(interview_id, None)

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
            result = await self.session.execute(
                select(CodeTestResult).where(
                    CodeTestResult.interview_step_id == step_id
                )
            )
            for old_result in result.scalars().all():
                await self.session.delete(old_result)
            await self.session.flush()

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
                self.session.add(test_result)

        await self.session.commit()
        await self.session.refresh(interview)
        return await self.find_interview_by_id(interview_id, None)

    async def _transcribe_audio(self, audio_buffer: bytes) -> str:
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
        interview_id: UUID,
        audio_file: UploadFile,
    ) -> Interview:
        allowed_mime_types = [
            "audio/webm",
            "audio/mpeg",
            "audio/mp3",
            "audio/wav",
            "audio/ogg",
            "audio/m4a",
        ]

        content_type = audio_file.content_type
        audio_bytes = await audio_file.read()

        if not audio_bytes:
            raise BadRequestException("Аудио файл не был загружен.")

        if content_type not in allowed_mime_types:
            raise BadRequestException(
                f"Неподдерживаемый формат аудио: {content_type}. Поддерживаемые форматы: {', '.join(allowed_mime_types)}"
            )

        max_size_bytes = 25 * 1024 * 1024
        if len(audio_bytes) > max_size_bytes:
            raise BadRequestException(
                f"Размер файла превышает максимально допустимый (25MB). Текущий размер: {len(audio_bytes) / 1024 / 1024:.2f}MB"
            )

        interview = await self.find_interview_by_id(interview_id, None)

        if interview.status in [
            InterviewStatus.COMPLETED,
            InterviewStatus.CANCELLED,
        ]:
            raise BadRequestException(
                "Интервью уже завершено или отменено. Новые сообщения не принимаются."
            )

        logger.debug(
            f"Обработка аудио файла для интервью {interview_id}. "
            f"Размер: {len(audio_bytes)} байт, тип: {content_type}"
        )

        transcribed_text = await self._transcribe_audio(audio_bytes)

        if not transcribed_text or not transcribed_text.strip():
            raise BadRequestException(
                "Не удалось распознать речь в аудио. Попробуйте записать еще раз."
            )

        message = ChatMessage(
            interview_id=interview_id,
            sender=MessageSender.USER,
            text=transcribed_text,
        )
        self.session.add(message)
        await self.session.flush()

        await self.session.commit()
        return await self.find_interview_by_id(interview_id, None)
