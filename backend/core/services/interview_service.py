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
from core.services.judge0_client import Judge0Client
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
    def __init__(self, session, ml_client: MLClient | None = None, judge0_client: Judge0Client | None = None):
        """Инициализация сервиса интервью."""
        super().__init__(session)
        self.ml_client = ml_client
        self.judge0_client = judge0_client

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

        # Вызываем ML API ТОЛЬКО для получения первого next_step
        session_id = str(interview.id)

        ml_response = await self.ml_client.start_interview(
            job_title=job_role_description,
            required_skills=key_skills or [],
            amount_of_tasks=amount_of_tasks,
            session_id=session_id,
        )
        
        # Получаем next_step и сохраняем его
        next_step_data = ml_response.get("next_step", ml_response.get("step", {}))
        interview.pending_next_step = next_step_data
        
        # Создаем первый шаг из pending_next_step
        await self._create_step_from_pending_next_step(interview)
        
        await self.session.commit()
        await self.session.refresh(interview)

        interview = await self.find_interview_by_id(interview.id, None)
        return InterviewSchema.model_validate(interview, from_attributes=True)

    async def _create_step_from_pending_next_step(self, interview: Interview):
        """
        Создает шаг из сохраненного pending_next_step.
        Это значит, что ML УЖЕ сказал нам, что делать, и мы НЕ вызываем его снова.
        """
        if not interview.pending_next_step:
            logger.error("No pending_next_step found")
            return
            
        step_data = interview.pending_next_step
        step_type = step_data.get("type")
        
        # Если next_step пустой или нет типа - не создаем шаг
        if not step_type:
            logger.info("Empty next_step - no new step created")
            interview.pending_next_step = None
            await self.session.flush()
            return
        
        question_text = step_data.get("question_text", "")
        ai_feedback = step_data.get("ai_feedback", "")
        
        message_text = question_text or ai_feedback
        
        # Дефолтное сообщение ТОЛЬКО для первого шага
        if not message_text and step_type == "DIALOG" and interview.current_step_index == 0:
             message_text = "Здравствуйте! Готовы начать?"
        
        # Если нет текста для не-первого шага - это ошибка
        if not message_text and interview.current_step_index > 0:
            logger.error(f"No message_text for step {interview.current_step_index}, step_data: {step_data}")
            # Не создаем пустой шаг
            interview.pending_next_step = None
            await self.session.flush()
            return
        
        step = InterviewStep(
            interview_id=interview.id,
            type=InterviewStepType(step_type),
            status=InterviewStepStatus.IN_PROGRESS,
            question_text=message_text,
        )
        
        if step_type == "CODE_TASK":
            code_task_data = step_data.get("code_task", {})
            
            topic = code_task_data.get("topic") 
            difficulty = code_task_data.get("difficulty", "medium")
            language = code_task_data.get("language", "python")
            
            selected_task = None
            
            # 1. Ищем все подходящие задачи в БД
            if topic:
                query = select(CodeTask).where(
                    CodeTask.topic == topic,
                    CodeTask.difficulty == difficulty,
                    CodeTask.language == language,
                )
                
                result = await self.session.execute(query)
                all_tasks = result.scalars().all()
                
                if all_tasks:
                    # Проверяем процент задач с высоким usage_count
                    HIGH_USAGE_THRESHOLD = 10  # Порог для "высокого" usage_count
                    DIVERSITY_THRESHOLD = 0.7  # 70% задач
                    
                    high_usage_tasks = [t for t in all_tasks if t.usage_count > HIGH_USAGE_THRESHOLD]
                    high_usage_ratio = len(high_usage_tasks) / len(all_tasks)
                    
                    logger.info(f"Found {len(all_tasks)} tasks for topic {topic}, {len(high_usage_tasks)} have usage_count > {HIGH_USAGE_THRESHOLD} ({high_usage_ratio:.1%})")
                    
                    # Если > 70% задач имеют высокий usage_count - добавляем новую задачу через ML
                    if high_usage_ratio > DIVERSITY_THRESHOLD:
                        logger.info(f"High usage ratio {high_usage_ratio:.1%} > {DIVERSITY_THRESHOLD:.0%}, generating new task to increase diversity")
                        generated_data = await self.ml_client.generate_code_task(topic, difficulty, language)
                        
                        if generated_data and generated_data.get("description"):
                            new_task = CodeTask(
                                description=generated_data.get("description", ""),
                                initial_code=generated_data.get("initial_code", ""),
                                language=language,
                                test_cases=generated_data.get("test_cases", []),
                                topic=topic,
                                difficulty=difficulty,
                                usage_count=0
                            )
                            self.session.add(new_task)
                            await self.session.flush()
                            all_tasks.append(new_task)
                            logger.info(f"Added new ML-generated task {new_task.id} to pool")
                    
                    # Выбираем задачу с минимальным usage_count (с рандомизацией среди топ-3)
                    tasks_sorted = sorted(all_tasks, key=lambda t: t.usage_count)
                    top_candidates = tasks_sorted[:min(3, len(tasks_sorted))]
                    selected_task = random.choice(top_candidates)
                    selected_task.usage_count += 1
                    logger.info(f"Selected task {selected_task.id} with usage_count={selected_task.usage_count-1} -> {selected_task.usage_count}")
                else:
                    # Если совсем нет задач - создаем первую через ML
                    logger.info(f"No tasks found for topic {topic}, generating first task")
                    generated_data = await self.ml_client.generate_code_task(topic, difficulty, language)
                    
                    if generated_data and generated_data.get("description"):
                        new_task = CodeTask(
                            description=generated_data.get("description", ""),
                            initial_code=generated_data.get("initial_code", ""),
                            language=language,
                            test_cases=generated_data.get("test_cases", []),
                            topic=topic,
                            difficulty=difficulty,
                            usage_count=1
                        )
                        self.session.add(new_task)
                        selected_task = new_task
                        logger.info(f"Created first task for topic {topic}")

            if selected_task:
                step.code_task = selected_task
                if not step.question_text:
                    step.question_text = selected_task.description
            else:
                 logger.error("Failed to assign a code task to the step.")
                 step.question_text = "Произошла ошибка при получении задачи. Пожалуйста, сообщите администратору."

        self.session.add(step)
        
        # Для DIALOG шагов сохраняем question_text как сообщение
        # (это следующий вопрос от AI)
        if message_text and step_type == "DIALOG":
            message = ChatMessage(
                interview_id=interview.id,
                sender=MessageSender.AI,
                text=message_text,
            )
            self.session.add(message)
        
        # Очищаем pending_next_step, так как мы его использовали
        interview.pending_next_step = None
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
            .where(
                or_(
                    Interview.user_id == user_id,
                    Interview.creator_id == user_id,
                )
            )
            .group_by(Interview.id)
            .order_by(Interview.created_at.desc())
        )
        interviews = result.all()
        interviews_list = []
        for interview, steps, chat_messages in interviews:
            interview.steps_count = steps
            interview.chat_messages_count = chat_messages
            interviews_list.append(
                ListInterviewItemSchema.model_validate(interview, from_attributes=True)
            )
        return interviews_list

    async def find_interview_by_token(
        self,
        public_token: str,
    ) -> Interview:
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
            select(Interview).where(Interview.public_token == public_token)
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
            query = query.where(
                or_(Interview.user_id == user_id, Interview.creator_id == user_id)
            )

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

        session_id = str(interview_id)
        
        # Вызываем ML API для оценки ответа И получения next_step
        ml_response = await self.ml_client.process_message(
            session_id=session_id,
            user_answer=text,
        )
        logger.info(f"ML response: {ml_response}")

        # Обновляем текущий шаг
        await self._update_current_step(interview, ml_response, text)

        # Добавляем feedback от ML в чат (если есть)
        feedback_text = ml_response.get("feedback") or ml_response.get("ai_feedback")
        if feedback_text:
            feedback_message = ChatMessage(
                interview_id=interview.id,
                sender=MessageSender.AI,
                text=feedback_text,
            )
            self.session.add(feedback_message)
            await self.session.flush()

        status = ml_response.get("status", "IN_PROGRESS")

        if status != "COMPLETED":
            # Сохраняем next_step в pending
            next_step_data = ml_response.get("next_step", ml_response.get("step", {}))
            interview.pending_next_step = next_step_data
            
            # Создаем следующий шаг (для CODE_TASK ищем в БД, не дергая ML снова)
            await self._create_step_from_pending_next_step(interview)
            interview.current_step_index += 1
        else:
            interview.status = InterviewStatus.COMPLETED
            interview.total_score = ml_response.get("score")
            interview.overall_feedback = ml_response.get("ai_feedback") or ml_response.get("feedback")
            
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

    async def handle_chat_message_stream(
        self,
        interview_id: UUID,
        sender: MessageSender,
        text: str,
    ):
        """
        SSE стриминг версия handle_chat_message.
        Yields события по мере получения от ML модели.
        """
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

        session_id = str(interview_id)
        
        # Собираем данные из стрима
        full_text = ""
        metadata = {}
        
        # Стримим события от ML
        async for event in self.ml_client.process_message_stream(
            session_id=session_id,
            user_answer=text,
        ):
            event_type = event.get("type")
            
            if event_type == "text_chunk":
                chunk_content = event.get("content", "")
                full_text += chunk_content
                logger.debug(f"Streaming text chunk: {chunk_content[:50]}...")
                # Передаем чанк дальше на фронт
                yield event
            
            elif event_type == "_metadata":
                # Внутренние метаданные - НЕ передаем на фронт, только сохраняем
                metadata = event.get("data", {})
                logger.info(f"Received metadata: score={metadata.get('score')}, next_step={metadata.get('next_step', {}).get('type')}")
            
            elif event_type == "done":
                # Стрим завершен
                yield event
                break
            
            elif event_type == "error":
                logger.error(f"Ошибка от ML стрима: {event.get('message')}")
                yield event
                raise BadRequestException(f"Ошибка ML: {event.get('message')}")
        
        # После завершения стрима - обновляем БД
        # Используем answer_text из metadata (это answerText из JSON ответа ML)
        answer_text = metadata.get("answer_text", full_text)
        
        ml_response = {
            "feedback": metadata.get("feedback"),
            "score": metadata.get("score"),
            "next_step": metadata.get("next_step"),
            "ai_feedback": answer_text,
            "status": metadata.get("status", "IN_PROGRESS"),
            "total_score": metadata.get("total_score"),
            "overall_feedback": metadata.get("overall_feedback")
        }
        
        logger.info(f"ML stream completed. Full text len: {len(full_text)}, answer_text: {answer_text[:100]}")
        
        # Обновляем текущий шаг
        await self._update_current_step(interview, ml_response, text)
        
        # НЕ сохраняем answer_text как отдельное сообщение!
        # Оно будет сохранено как question_text следующего шага в _create_step_from_pending_next_step
        
        response_status = ml_response.get("status", "IN_PROGRESS")
        
        if response_status != "COMPLETED":
            # Сохраняем next_step в pending
            next_step_data = ml_response.get("next_step")
            if next_step_data:
                interview.pending_next_step = next_step_data
                
                # Создаем следующий шаг
                await self._create_step_from_pending_next_step(interview)
                interview.current_step_index += 1
        else:
            interview.status = InterviewStatus.COMPLETED
            interview.total_score = ml_response.get("total_score") or ml_response.get("score")
            interview.overall_feedback = ml_response.get("overall_feedback") or full_text
        
        await self.session.commit()
        
        # Отправляем финальный Interview объект (без type, просто модель)
        refreshed_interview = await self.find_interview_by_id(interview_id, None)
        from core.dto.interview import InterviewSchema
        interview_data = InterviewSchema.model_validate(refreshed_interview, from_attributes=True)
        
        # Отправляем чистый Interview как в обычном /message
        yield interview_data.model_dump(mode='json')

    async def _update_current_step(self, interview: Interview, ml_response: dict[str, Any], user_answer: str):
        current_step = next(
            (s for s in interview.steps if s.status == InterviewStepStatus.IN_PROGRESS),
            None,
        )

        if current_step:
            current_step.status = InterviewStepStatus.COMPLETED
            current_step.user_answer = ml_response.get("user_answer", user_answer)
            current_step.feedback = ml_response.get("feedback")
            current_step.score = ml_response.get("score")
            await self.session.flush()

    async def run_playground_code(self, code: str, language: str, test_cases: list[dict] | None = None) -> dict:
        if not test_cases:
            test_cases = []
        return await self.judge0_client.run_tests(code, language, test_cases)

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
        current_step.status = InterviewStepStatus.COMPLETED 

        test_cases = current_step.code_task.test_cases
        if not isinstance(test_cases, list):
            test_cases = []
            
        judge_result = await self.judge0_client.run_tests(
            user_code, 
            current_step.code_task.language, 
            test_cases
        )
        
        result = await self.session.execute(
            select(CodeTestResult).where(
                CodeTestResult.interview_step_id == step_id
            )
        )
        for old_result in result.scalars().all():
            await self.session.delete(old_result)
        await self.session.flush()

        passed_count = 0
        total_count = len(judge_result["results"])
        
        for res in judge_result["results"]:
            test_status = CodeTestResultStatus.PASSED if res["passed"] else CodeTestResultStatus.FAILED
            if res["passed"]:
                passed_count += 1
                
            test_result = CodeTestResult(
                interview_step_id=step_id,
                test_id="test",
                status=test_status,
                details=f"Expected: {res.get('expected')}, Got: {res.get('stdout')}. Error: {res.get('stderr')}"
            )
            self.session.add(test_result)
            
        execution_summary = f"Code execution result: {passed_count}/{total_count} tests passed."
        if passed_count < total_count:
            execution_summary += " Some tests failed."
        else:
            execution_summary += " All tests passed successfully."
            
        # Добавляем описание задачи, так как ML ее не знает (она была выбрана из БД)
        task_context = f"Task Description:\n{current_step.code_task.description}\n"
        if current_step.code_task.topic:
             task_context += f"Topic: {current_step.code_task.topic}\n"
            
        session_id = str(interview_id)
        
        # Вызываем ML для оценки И получения next_step
        ml_response = await self.ml_client.process_message(
            session_id=session_id,
            user_answer=f"{task_context}\nUser Code:\n{user_code}\n\nSystem Execution Result:\n{execution_summary}"
        )
        
        current_step.feedback = ml_response.get("feedback")
        current_step.score = ml_response.get("score")
        
        # Добавляем feedback от ML в чат
        feedback_text = ml_response.get("feedback") or ml_response.get("ai_feedback")
        if feedback_text:
            feedback_message = ChatMessage(
                interview_id=interview.id,
                sender=MessageSender.AI,
                text=feedback_text,
            )
            self.session.add(feedback_message)
            await self.session.flush()
        
        status = ml_response.get("status", "IN_PROGRESS")
        if status != "COMPLETED":
             # Сохраняем next_step и создаем следующий шаг
             next_step_data = ml_response.get("next_step", ml_response.get("step", {}))
             interview.pending_next_step = next_step_data
             await self._create_step_from_pending_next_step(interview)
             interview.current_step_index += 1
        else:
            interview.status = InterviewStatus.COMPLETED
            interview.total_score = ml_response.get("score")
            interview.overall_feedback = ml_response.get("ai_feedback")

        await self.session.commit()
        await self.session.refresh(interview)
        return await self.find_interview_by_id(interview_id, None)

    async def skip_step(self, interview_id: UUID, step_id: UUID) -> Interview:
        interview = await self.find_interview_by_id(interview_id, None)
        
        if interview.status != InterviewStatus.IN_PROGRESS:
             raise BadRequestException("Интервью не в процессе.")
             
        current_step = next((s for s in interview.steps if s.id == step_id), None)
        if not current_step:
            raise BadRequestException("Шаг не найден.")
            
        current_step.status = InterviewStepStatus.COMPLETED
        current_step.user_answer = "[SKIPPED BY USER]"
        current_step.score = 0
        
        session_id = str(interview_id)
        
        # Вызываем ML для получения фидбека И next_step
        ml_response = await self.ml_client.process_message(
            session_id=session_id,
            user_answer="User skipped this task."
        )
        
        current_step.feedback = ml_response.get("feedback")
        
        # Добавляем feedback от ML в чат
        feedback_text = ml_response.get("feedback") or ml_response.get("ai_feedback")
        if feedback_text:
            feedback_message = ChatMessage(
                interview_id=interview.id,
                sender=MessageSender.AI,
                text=feedback_text,
            )
            self.session.add(feedback_message)
            await self.session.flush()
        
        status = ml_response.get("status", "IN_PROGRESS")
        if status != "COMPLETED":
             next_step_data = ml_response.get("next_step", ml_response.get("step", {}))
             interview.pending_next_step = next_step_data
             await self._create_step_from_pending_next_step(interview)
             interview.current_step_index += 1
        else:
            interview.status = InterviewStatus.COMPLETED
            interview.total_score = ml_response.get("score")
            interview.overall_feedback = ml_response.get("ai_feedback")

        await self.session.commit()
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
    ) -> str:
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
