from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from core.config.config import settings
from infrastructure.errors.base import BadRequestException

logger = logging.getLogger(__name__)


class MLClient:
    """Клиент для взаимодействия с ML API сервисом."""

    def __init__(self, base_url: str | None = None):
        """Инициализация ML клиента."""
        self.base_url = base_url or settings.ML_API_URL
        self.timeout = aiohttp.ClientTimeout(total=60.0)  # Таймаут для запросов к ML API

    async def start_interview(
        self,
        job_title: str,
        required_skills: list[str],
        amount_of_tasks: int,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Начало интервью - получение первого шага от ML сервиса."""
        url = f"{self.base_url}/start"
        payload = {
            "job_title": job_title,
            "required_skills": required_skills,
            "amount_of_tasks": amount_of_tasks,
        }
        # Если передан session_id, добавляем его в payload (ML API должен поддерживать это)
        if session_id:
            payload["session_id"] = session_id

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"ML API вернул ошибку: {response.status} - {error_text}")
                        raise BadRequestException(
                            f"Ошибка ML сервиса при начале интервью: {response.status}"
                        )
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка соединения с ML API: {e}")
            raise BadRequestException("Не удалось подключиться к ML сервису.") from e
        except asyncio.TimeoutError as e:
            logger.error(f"Таймаут при вызове ML API: {e}")
            raise BadRequestException("ML сервис не отвечает. Попробуйте позже.") from e

    async def process_message(
        self,
        session_id: str,
        user_answer: str,
    ) -> dict[str, Any]:
        """Обработка ответа пользователя и получение следующего шага."""
        url = f"{self.base_url}/message"
        payload = {
            "session_id": session_id,
            "user_answer": user_answer,
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 404:
                        error_text = await response.text()
                        logger.error(f"Сессия {session_id} не найдена в ML сервисе: {error_text}")
                        raise BadRequestException("Сессия интервью не найдена.")
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"ML API вернул ошибку: {response.status} - {error_text}")
                        raise BadRequestException(
                            f"Ошибка ML сервиса при обработке сообщения: {response.status}"
                        )
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка соединения с ML API: {e}")
            raise BadRequestException("Не удалось подключиться к ML сервису.") from e
        except asyncio.TimeoutError as e:
            logger.error(f"Таймаут при вызове ML API: {e}")
            raise BadRequestException("ML сервис не отвечает. Попробуйте позже.") from e

    async def process_message_stream(
        self,
        session_id: str,
        user_answer: str,
    ):
        """
        Обработка ответа пользователя с SSE стримингом через /message/stream.
        Возвращает async generator с чанками текста и метаданными.
        
        Yields:
            dict: События вида:
                - {"type": "text_chunk", "content": "..."}  # чанки текста
                - {"type": "metadata", "score": 85, "next_step": {...}}  # метаданные
                - {"type": "done"}  # завершение
                - {"type": "error", "message": "..."}  # ошибка
        """
        url = f"{self.base_url}/message/stream"
        payload = {
            "session_id": session_id,
            "user_answer": user_answer,
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120.0)) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 404:
                        error_text = await response.text()
                        logger.error(f"Сессия {session_id} не найдена в ML сервисе: {error_text}")
                        raise BadRequestException("Сессия интервью не найдена.")
                    
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"ML API вернул ошибку: {response.status} - {error_text}")
                        raise BadRequestException(
                            f"Ошибка ML сервиса при обработке сообщения: {response.status}"
                        )
                    
                    # Читаем SSE поток
                    import json
                    buffer = ""
                    
                    async for chunk in response.content.iter_any():
                        if not chunk:
                            continue
                            
                        # Декодируем чанк и добавляем в буфер
                        buffer += chunk.decode('utf-8')
                        
                        # Разбиваем по строкам
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            
                            if not line or not line.startswith('data: '):
                                continue
                            
                            # Парсим JSON из SSE
                            data_str = line[6:]  # Убираем "data: "
                            
                            # Пропускаем пустые data или комментарии
                            if not data_str or data_str.startswith(':'):
                                continue
                                
                            try:
                                event_data = json.loads(data_str)
                                logger.debug(f"SSE event received: type={event_data.get('type')}, content_len={len(str(event_data.get('content', '')))}")
                                yield event_data
                                
                                # Прерываем если получили done или error
                                if event_data.get("type") in ("done", "error"):
                                    logger.info(f"SSE stream completed with type: {event_data.get('type')}")
                                    return
                            except json.JSONDecodeError as e:
                                logger.warning(f"Не удалось распарсить SSE событие: {data_str[:100]}... Error: {e}")
                                continue
                            
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка соединения с ML API: {e}")
            raise BadRequestException("Не удалось подключиться к ML сервису.") from e
        except asyncio.TimeoutError as e:
            logger.error(f"Таймаут при вызове ML API: {e}")
            raise BadRequestException("ML сервис не отвечает. Попробуйте позже.") from e

    async def generate_code_task(
        self,
        topic: str,
        difficulty: str,
        language: str = "python"
    ) -> dict[str, Any]:
        """
        Запрос к ML сервису на генерацию новой задачи по теме.
        """
        url = f"{self.base_url}/generate_task"
        payload = {
            "topic": topic,
            "difficulty": difficulty,
            "language": language
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                     if response.status >= 400:
                        logger.warning(f"ML task generation failed or not implemented: {response.status}. Using fallback.")
                        # If generation endpoint fails, we might return empty or mock
                        return {} 
                     return await response.json()
        except Exception as e:
             logger.error(f"Failed to generate task: {e}")
             # In case of error, we can fallback to a very basic mock task or re-raise
             return {
                 "description": f"Write a function to solve a problem about {topic} ({difficulty}).",
                 "initial_code": "def solve():\n    pass",
                 "test_cases": [],
                 "topic": topic,
                 "difficulty": difficulty,
                 "language": language
             }
