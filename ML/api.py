from __future__ import annotations

import json
import logging
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from openai import InternalServerError, APITimeoutError, APIError

from interview_agent import InterviewAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Interview Agent API", version="1.0.0")

agents: dict[str, InterviewAgent] = {}


class StartInterviewRequest(BaseModel):
    """Запрос на начало интервью."""
    
    job_title: str = Field(..., min_length=1, max_length=200, description="Название вакансии")
    required_skills: list[str] = Field(..., min_length=1, description="Список требуемых навыков")
    amount_of_tasks: int = Field(..., ge=1, le=30, description="Количество вопросов в интервью")
    session_id: str | None = Field(None, description="ID сессии (опционально, для синхронизации с бэкендом)")
    preferences: str | None = Field(None, description="Дополнительные предпочтения (например: 'побольше задач на код')")


class NextStepDialog(BaseModel):
    """Следующий шаг - диалог."""
    type: str = Field("DIALOG", description="Тип шага")
    question_text: str = Field(..., description="Текст вопроса")


class NextStepCodeTask(BaseModel):
    """Следующий шаг - кодовая задача."""
    type: str = Field("CODE_TASK", description="Тип шага")
    code_task: dict[str, str] = Field(..., description="Параметры задачи: topic, difficulty, language")


class InterviewStepResponse(BaseModel):
    """Ответ с шагом интервью."""
    
    type: str = Field(..., description="Тип шага: DIALOG или CODE_TASK")
    question_text: str | None = Field(None, description="Текст вопроса или ответа интервьюера")
    status: str = Field(..., description="Статус: IN_PROGRESS или COMPLETED")
    score: int | None = Field(None, description="Оценка за шаг (0-100)")
    ai_feedback: str | None = Field(None, description="Обратная связь от ИИ")
    user_answer: str | None = Field(None, description="Ответ пользователя")
    feedback: str | None = Field(None, description="Краткая обратная связь")
    next_step: dict[str, Any] | None = Field(None, description="Следующий шаг интервью")
    code_task: dict[str, Any] | None = Field(None, description="Полная кодовая задача (если type=CODE_TASK)")


class MessageRequest(BaseModel):
    """Запрос с сообщением пользователя."""
    
    session_id: str = Field(..., description="ID сессии интервью")
    user_answer: str = Field(..., min_length=1, max_length=5000, description="Ответ пользователя")


class StartInterviewResponse(BaseModel):
    """Ответ на начало интервью."""
    
    session_id: str = Field(..., description="ID сессии интервью")
    step: InterviewStepResponse = Field(..., description="Первый шаг интервью")


@app.post("/start", response_model=StartInterviewResponse, status_code=status.HTTP_200_OK)
async def start_interview(request: StartInterviewRequest) -> StartInterviewResponse:
    """Начало интервью - создание сессии и получение первого вопроса."""
    try:
        agent = InterviewAgent()
        # Используем переданный session_id или генерируем новый
        session_id = request.session_id or str(uuid4())
        
        # Проверяем, что session_id не занят
        if session_id in agents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Сессия с ID {session_id} уже существует"
            )
        
        first_step = agent.start_interview(
            job_title=request.job_title,
            required_skills=request.required_skills,
            amount_of_tasks=request.amount_of_tasks,
            preferences=request.preferences,
        )
        
        agents[session_id] = agent
        
        return StartInterviewResponse(
            session_id=session_id,
            step=InterviewStepResponse(**first_step)
        )
    except Exception as e:
        logger.error(f"Ошибка при начале интервью: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при начале интервью: {str(e)}"
        )


@app.post("/message", response_model=InterviewStepResponse, status_code=status.HTTP_200_OK)
async def process_message(request: MessageRequest) -> InterviewStepResponse:
    """Обработка ответа пользователя и получение следующего шага."""
    if request.session_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия интервью не найдена"
        )
    
    try:
        agent = agents[request.session_id]
        step = agent.process_answer(request.user_answer)
        
        if step is None:
            raise RuntimeError("Агент вернул None вместо шага интервью")
        
        if step.get("status") == "COMPLETED" and agent.is_interview_complete():
            final_feedback = agent.generate_feedback()
            step["ai_feedback"] = final_feedback
            step["feedback"] = final_feedback
        
        return InterviewStepResponse(**step)
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке сообщения: {str(e)}"
        )


@app.post("/start/stream", response_model=StartInterviewResponse, status_code=status.HTTP_200_OK)
async def start_interview_stream(request: StartInterviewRequest) -> StartInterviewResponse:
    """Начало интервью с использованием стриминга внутри."""
    try:
        agent = InterviewAgent()
        session_id = request.session_id or str(uuid4())
        
        if session_id in agents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Сессия с ID {session_id} уже существует"
            )
        
        full_response = ""
        for chunk in agent.start_interview_stream(
            job_title=request.job_title,
            required_skills=request.required_skills,
            amount_of_tasks=request.amount_of_tasks,
            preferences=request.preferences,
        ):
            full_response += chunk
        
        if not full_response:
            raise RuntimeError("Пустой ответ от модели")
        
        parsed = agent._parse_ai_response(full_response)
        
        if parsed.get("type") == "new_step":
            next_step = parsed.get("nextStep", {})
            next_step_type = next_step.get("type", "DIALOG")
            answer_text = parsed.get("answerText", "")
            next_question_text = next_step.get("questionText", "")
            
            question_text = answer_text or next_question_text
            
            next_step_data = None
            if next_step_type == "CODE_TASK":
                code_task = next_step.get("codeTask", {})
                next_step_data = {
                    "type": "CODE_TASK",
                    "code_task": {
                        "topic": code_task.get("topic", "Python"),
                        "difficulty": code_task.get("difficulty", "medium"),
                        "language": code_task.get("language", "python")
                    }
                }
            else:
                next_step_data = {
                    "type": "DIALOG",
                    "question_text": next_question_text or answer_text
                }
            
            first_step = {
                "type": "DIALOG",
                "question_text": question_text,
                "status": "IN_PROGRESS",
                "score": parsed.get("score"),
                "ai_feedback": answer_text,
                "user_answer": None,
                "feedback": parsed.get("feedback"),
                "next_step": next_step_data
            }
        else:
            answer_text = parsed.get("answerText", full_response[:300])
            first_step = {
                "type": "DIALOG",
                "question_text": answer_text,
                "status": "IN_PROGRESS",
                "score": None,
                "ai_feedback": answer_text,
                "user_answer": None,
                "feedback": None,
                "next_step": {
                    "type": "DIALOG",
                    "question_text": answer_text
                }
            }
        
        agents[session_id] = agent
        
        return StartInterviewResponse(
            session_id=session_id,
            step=InterviewStepResponse(**first_step)
        )
    except Exception as e:
        logger.error(f"Ошибка при начале интервью: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при начале интервью: {str(e)}"
        )


@app.post("/message/stream")
async def process_message_stream(request: MessageRequest):
    """Реальный SSE стриминг - отправка чанков текста по мере получения от LLM."""
    if request.session_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия интервью не найдена"
        )
    
    try:
        agent = agents[request.session_id]
        
        chunks = []
        for chunk in agent.process_answer_stream(request.user_answer):
            chunks.append(chunk)
        
        if not chunks:
            raise RuntimeError("Пустой ответ от модели")
        
        full_response = "".join(chunks)
        
        if full_response.strip().startswith("{"):
            try:
                step_data = json.loads(full_response)
                return InterviewStepResponse(**step_data)
            except json.JSONDecodeError:
                pass
        
        code_submission = agent._parse_code_submission(request.user_answer)
        parsed = agent._parse_ai_response(full_response)
        response_type = parsed.get("type", "dialog_response")
        
        if code_submission and response_type == "new_step":
            next_step = parsed.get("nextStep", {})
            next_step_type = next_step.get("type", "DIALOG")
            
            answer_text = parsed.get("answerText", "")
            next_question_text = next_step.get("questionText", "")
            full_code_task = None
            
            next_step_data = None
            if next_step_type == "CODE_TASK":
                code_task = next_step.get("codeTask", {})
                topic = code_task.get("topic", "Python")
                difficulty = code_task.get("difficulty", "medium")
                language = code_task.get("language", "python")
                
                try:
                    full_code_task = agent.generate_code_task(topic, difficulty, language)
                    question_text = f"{answer_text or 'Переходим к кодовой задаче.'}\n\n**Задача:**\n{full_code_task['description']}\n\n**Начальный код:**\n```{language}\n{full_code_task['initial_code']}\n```"
                except Exception as e:
                    logger.error(f"Ошибка генерации задачи: {e}")
                    question_text = answer_text or "Переходим к кодовой задаче."
                    full_code_task = {
                        "description": "Ошибка генерации задачи",
                        "initial_code": "",
                        "test_cases": [],
                        "topic": topic,
                        "difficulty": difficulty,
                        "language": language
                    }
                
                next_step_data = {
                    "type": "CODE_TASK",
                    "code_task": {
                        "topic": topic,
                        "difficulty": difficulty,
                        "language": language
                    }
                }
    async def generate_sse():
        try:
            agent = agents[request.session_id]
            full_raw_text = ""
            displayed_text = ""
            in_json_block = False
            json_buffer = ""
            
            # Собираем весь RAW ответ от LLM
            for chunk in agent.process_answer_stream(request.user_answer):
                full_raw_text += chunk
            
            if not full_raw_text:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Пустой ответ от модели'})}\n\n"
                return
            
            # Парсим полный ответ для получения метаданных
            parsed = agent._parse_ai_response(full_raw_text)
            response_type = parsed.get("type", "dialog_response")
            
            # ВСЕГДА используем answerText из JSON (это правильный текст ответа)
            answer_text = parsed.get("answerText", "")
            
            if answer_text:
                # Стримим answerText посимвольно для эффекта печатания
                for char in answer_text:
                    yield f"data: {json.dumps({'type': 'text_chunk', 'content': char}, ensure_ascii=False)}\n\n"
                displayed_text = answer_text
            else:
                question_text = next_question_text or answer_text
                if not question_text:
                    question_text = "Следующий вопрос."
                next_step_data = {
                    "type": "DIALOG",
                    "question_text": question_text
                }
            
            step = {
                "type": "DIALOG" if next_step_type == "DIALOG" else "CODE_TASK",
                "question_text": question_text,
                "status": "IN_PROGRESS",
                displayed_text = ""
            
            # Формируем внутренние метаданные (НЕ отправляем их как событие!)
            metadata = {
                "response_type": response_type,
                "score": parsed.get("score"),
                "ai_feedback": answer_text,
                "user_answer": request.user_answer,
                "feedback": parsed.get("feedback", ""),
                "next_step": next_step_data
            }
            
            if full_code_task:
                step["code_task"] = full_code_task
            return InterviewStepResponse(**step)
        
        if response_type == "final_feedback":
            step = {
                "type": "DIALOG",
                "question_text": parsed.get("answerText", ""),
                "status": "COMPLETED",
                "score": parsed.get("totalScore"),
                "ai_feedback": parsed.get("overallFeedback", ""),
                "user_answer": request.user_answer,
                "feedback": parsed.get("feedback", ""),
                "next_step": None
            }
        elif response_type == "new_step":
            next_step = parsed.get("nextStep", {})
            next_step_type = next_step.get("type", "DIALOG")
            
            answer_text = parsed.get("answerText", "")
            next_question_text = next_step.get("questionText", "")
            full_code_task = None
            
            next_step_data = None
            if next_step_type == "CODE_TASK":
                code_task = next_step.get("codeTask", {})
                topic = code_task.get("topic", "Python")
                difficulty = code_task.get("difficulty", "medium")
                language = code_task.get("language", "python")
                
                try:
                    full_code_task = agent.generate_code_task(topic, difficulty, language)
                    question_text = f"{answer_text or 'Переходим к кодовой задаче.'}\n\n**Задача:**\n{full_code_task['description']}\n\n**Начальный код:**\n```{language}\n{full_code_task['initial_code']}\n```"
                except Exception as e:
                    logger.error(f"Ошибка генерации задачи: {e}")
                    question_text = answer_text or "Переходим к кодовой задаче."
                    full_code_task = {
                        "description": "Ошибка генерации задачи",
                        "initial_code": "",
                        "test_cases": [],
                        "topic": topic,
                        "difficulty": difficulty,
                        "language": language
                    }
                
                next_step_data = {
                    "type": "CODE_TASK",
                    "code_task": {
                        "topic": topic,
                        "difficulty": difficulty,
                        "language": language
                    }
                }
            else:
                question_text = next_question_text or answer_text
                if not question_text:
                    question_text = "Следующий вопрос."
                next_step_data = {
                    "type": "DIALOG",
                    "question_text": question_text
                }
            
            step = {
                "type": "DIALOG" if next_step_type == "DIALOG" else "CODE_TASK",
                "question_text": question_text,
                "status": "COMPLETED" if agent.interview_ended else "IN_PROGRESS",
                "score": parsed.get("score"),
                "ai_feedback": answer_text,
                "user_answer": request.user_answer,
                "feedback": parsed.get("feedback", ""),
                "next_step": next_step_data
            }
            
            if full_code_task:
                step["code_task"] = full_code_task
        else:
            answer_text = parsed.get("answerText", "")
            step = {
                "type": "DIALOG",
                "question_text": answer_text,
                "status": "COMPLETED" if agent.interview_ended else "IN_PROGRESS",
                "score": None,
                "ai_feedback": answer_text,
                "user_answer": request.user_answer,
                "feedback": None,
                "next_step": {
                    "type": "DIALOG",
                    "question_text": answer_text
                }
            }
        
        if step.get("status") == "COMPLETED" and agent.is_interview_complete():
            final_feedback = agent.generate_feedback()
            step["ai_feedback"] = final_feedback
            step["feedback"] = final_feedback
        
        return InterviewStepResponse(**step)
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке сообщения: {str(e)}"
        )
                "feedback": parsed.get("feedback"),
                "answer_text": displayed_text or parsed.get("answerText", ""),
                "status": "COMPLETED" if (response_type == "final_feedback" or agent.interview_ended) else "IN_PROGRESS"
            }
            
            # Если интервью завершено
            if agent.is_interview_complete():
                final_feedback = agent.generate_feedback()
                metadata["final_feedback"] = final_feedback
                metadata["status"] = "COMPLETED"
            
            # Определяем next_step
            if response_type == "new_step":
                next_step = parsed.get("nextStep", {})
                next_step_type = next_step.get("type", "DIALOG")
                
                if next_step_type == "CODE_TASK":
                    code_task = next_step.get("codeTask", {})
                    metadata["next_step"] = {
                        "type": "CODE_TASK",
                        "code_task": {
                            "topic": code_task.get("topic", "Python"),
                            "difficulty": code_task.get("difficulty", "medium"),
                            "language": code_task.get("language", "python")
                        }
                    }
                else:
                    # Если questionText пустой, используем answerText
                    question_text = next_step.get("questionText") or parsed.get("answerText", "")
                    metadata["next_step"] = {
                        "type": "DIALOG",
                        "question_text": question_text
                    }
            elif response_type == "final_feedback":
                metadata["next_step"] = None
                metadata["status"] = "COMPLETED"
                metadata["total_score"] = parsed.get("totalScore")
                metadata["overall_feedback"] = parsed.get("overallFeedback", "")
            
            # НЕ отправляем metadata как событие - бекенд его получит внутренне
            # Только сохраняем для возврата
            
            # Возвращаем метаданные в специальном формате (для внутреннего использования)
            yield f"data: {json.dumps({'type': '_metadata', 'data': metadata}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            logger.error(f"Ошибка при стриминге: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.delete("/session/{session_id}", status_code=status.HTTP_200_OK)
async def delete_session(session_id: str) -> dict[str, str]:
    """Удаление сессии интервью."""
    if session_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия интервью не найдена"
        )
    
    del agents[session_id]
    return {"message": "Сессия удалена"}


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Проверка здоровья сервиса."""
    return {"status": "ok"}


class GenerateTaskRequest(BaseModel):
    """Запрос на генерацию задачи."""
    topic: str = Field(..., min_length=1, max_length=200, description="Тема задачи")
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Сложность: easy, medium, hard")
    language: str = Field(..., min_length=1, max_length=50, description="Язык программирования")


class GenerateTaskResponse(BaseModel):
    """Ответ с полной задачей."""
    description: str = Field(..., description="Описание задачи")
    initial_code: str = Field(..., description="Начальный код")
    test_cases: list[dict[str, str]] = Field(..., description="Тест-кейсы (до 3)")
    topic: str = Field(..., description="Тема задачи")
    difficulty: str = Field(..., description="Сложность")
    language: str = Field(..., description="Язык программирования")


@app.post("/generate_task", response_model=GenerateTaskResponse, status_code=status.HTTP_200_OK)
async def generate_task(request: GenerateTaskRequest) -> GenerateTaskResponse:
    """Генерация полной задачи на код по параметрам."""
    try:
        agent = InterviewAgent()
        task = agent.generate_code_task(
            topic=request.topic,
            difficulty=request.difficulty,
            language=request.language
        )
        return GenerateTaskResponse(**task)
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        
        cause = getattr(e, '__cause__', None)
        cause_type = type(cause).__name__ if cause else None
        cause_msg = str(cause) if cause else ""
        
        is_timeout = (
            "504" in error_msg or 
            "Gateway Time-out" in error_msg or 
            "Gateway Timeout" in error_msg or
            "timeout" in error_msg.lower() or
            "504" in cause_msg or
            "Gateway Time-out" in cause_msg or
            "Gateway Timeout" in cause_msg or
            "timeout" in cause_msg.lower() or
            isinstance(e, APITimeoutError) or
            (cause and isinstance(cause, APITimeoutError))
        )
        
        is_api_error = (
            isinstance(e, (InternalServerError, APIError)) or
            "InternalServerError" in error_type or
            "APIError" in error_type or
            (cause and isinstance(cause, (InternalServerError, APIError))) or
            "InternalServerError" in (cause_type or "") or
            "APIError" in (cause_type or "")
        )
        
        if is_timeout:
            logger.error(f"Таймаут при генерации задачи: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Превышено время ожидания ответа от сервиса генерации. Попробуйте позже."
            )
        
        if is_api_error:
            logger.error(f"Ошибка API при генерации задачи: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис генерации временно недоступен. Попробуйте позже."
            )
        
        logger.error(f"Ошибка при генерации задачи: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при генерации задачи: {str(e)}"
        )

