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

