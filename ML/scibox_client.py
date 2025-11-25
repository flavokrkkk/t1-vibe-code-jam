from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion

from scibox_config import (
    DEFAULT_CHAT_MODEL,
    DEFAULT_CODER_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    MODELS,
    SCIBOX_BASE_URL,
)

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


class SciBoxClient:
    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        if not api_key:
            raise ValueError("SciBox API key обязателен для создания клиента.")
        
        if base_url is None:
            base_url = os.getenv("SCIBOX_BASE_URL", SCIBOX_BASE_URL)
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _retry_request(self, func, *args, **kwargs):
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e).lower()
                last_error = e
                
                if attempt < self.max_retries - 1:
                    if any(code in error_msg for code in ["429", "500", "502", "503", "rate limit", "internal"]):
                        delay = self.retry_delay * (2 ** attempt)
                        logger.warning(f"Ошибка {e}, повтор через {delay}с (попытка {attempt + 1}/{self.max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        raise
                else:
                    raise last_error
        
        raise last_error
    
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = DEFAULT_CHAT_MODEL,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 256,
        stream: bool = False,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ) -> ChatCompletion | Any:
        if model not in MODELS or MODELS[model]["type"] != "chat":
            raise ValueError(f"Модель {model} не является чат-моделью")
        
        def _call():
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=stream,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
            )
        
        return self._retry_request(_call)
    
    def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str = DEFAULT_CHAT_MODEL,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 256,
    ):
        if model not in MODELS or MODELS[model]["type"] != "chat":
            raise ValueError(f"Модель {model} не является чат-моделью")
        
        def _call():
            return self.client.chat.completions.stream(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
        
        return self._retry_request(_call)
    
    def embeddings(
        self,
        input_text: str | list[str],
        model: str = DEFAULT_EMBEDDING_MODEL,
    ):
        if model not in MODELS or MODELS[model]["type"] != "embedding":
            raise ValueError(f"Модель {model} не является эмбеддинг-моделью")
        
        def _call():
            return self.client.embeddings.create(
                model=model,
                input=input_text,
            )
        
        return self._retry_request(_call)
    
    def list_models(self):
        def _call():
            return self.client.models.list()
        
        return self._retry_request(_call)

