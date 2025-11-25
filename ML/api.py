from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

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


class InterviewStepResponse(BaseModel):
    """Ответ с шагом интервью."""
    
    type: str = Field(..., description="Тип шага: DIALOG или CODE_TASK")
    question_text: str | None = Field(None, description="Текст вопроса или ответа интервьюера")
    status: str = Field(..., description="Статус: IN_PROGRESS или COMPLETED")
    score: int | None = Field(None, description="Оценка за шаг (0-100)")
    ai_feedback: str | None = Field(None, description="Обратная связь от ИИ")
    user_answer: str | None = Field(None, description="Ответ пользователя")
    feedback: str | None = Field(None, description="Краткая обратная связь")


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

