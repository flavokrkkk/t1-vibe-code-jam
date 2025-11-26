from __future__ import annotations

import json
import logging
import os
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from langchain_integration import get_scibox_llm
from scibox_config import DEFAULT_CODER_MODEL

logger = logging.getLogger(__name__)


class CodeTaskAgent:
    """Агент для работы с кодовыми задачами используя кодовую модель."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_CODER_MODEL):
        """Инициализация агента."""
        if api_key is None:
            api_key = os.getenv("SCIBOX_API_KEY")
        if not api_key:
            raise ValueError("SciBox API key обязателен.")
        
        self.llm = get_scibox_llm(model=model, temperature=0.2)
        self.model_name = model

    def _extract_json(self, text: str) -> dict[str, Any] | None:
        """Извлечение JSON из ответа модели."""
        patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```json\s*(\{.*\})\s*```',
            r'```\s*(\{.*?\})\s*```',
        ]
        
        for pattern in patterns:
            import re
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    json_str = match.group(1)
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        
        json_start = text.find('{')
        if json_start != -1:
            bracket_count = 0
            for i in range(json_start, len(text)):
                if text[i] == '{':
                    bracket_count += 1
                elif text[i] == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        try:
                            return json.loads(text[json_start:i+1])
                        except json.JSONDecodeError:
                            break
        
        return None

    def generate_code_task(
        self,
        topic: str,
        difficulty: str,
        language: str,
    ) -> dict[str, Any]:
        """Генерация полной задачи на код."""
        prompt = f"""Сгенерируй задачу на программирование в формате LeetCode.

Тема: {topic}
Сложность: {difficulty}
Язык: {language}

Формат кода (обязательно):
class Solution(object):
    def methodName(self, param1, param2):
        \"\"\"
        :type param1: List[int]
        :type param2: int
        :rtype: List[int]
        \"\"\"
        pass

Верни JSON:
{{
  "description": "описание задачи (2-3 предложения)",
  "initial_code": "class Solution(object):\\n    def twoSum(self, nums, target):\\n        \\\"\\\"\\\"\\n        :type nums: List[int]\\n        :type target: int\\n        :rtype: List[int]\\n        \\\"\\\"\\\"\\n        pass",
  "test_cases": [
    {{"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"}},
    {{"input": "nums = [3,2,4], target = 6", "output": "[1,2]"}}
  ]
}}

КРИТИЧЕСКИ ВАЖНО:
- initial_code ОБЯЗАТЕЛЬНО в формате LeetCode: class Solution(object)
- Метод ДОЛЖЕН иметь docstring с :type для каждого параметра и :rtype для возврата
- Для Python используй List[int], str, int, bool в type hints
- test_cases: массив из 2-3 тестов с input и output как строки"""
        
        messages = [
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        parsed = self._extract_json(response_text)
        if not parsed:
            raise RuntimeError(f"Не удалось извлечь JSON: {response_text[:200]}")
        
        test_cases = parsed.get("test_cases", [])
        if len(test_cases) > 3:
            test_cases = test_cases[:3]
        
        return {
            "description": parsed.get("description", ""),
            "initial_code": parsed.get("initial_code", ""),
            "test_cases": test_cases,
            "topic": topic,
            "difficulty": difficulty,
            "language": language
        }

    def evaluate_code(
        self,
        user_code: str,
        task_description: str,
        test_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Оценка кода с фидбэком."""
        passed = sum(1 for r in test_results if r.get("status") == "PASSED")
        total = len(test_results)
        
        prompt = f"""Задача: {task_description}

Код кандидата:
```python
{user_code}
```

Тесты: {passed}/{total} пройдено

Оцени код (0-100) и дай фидбэк (2-3 предложения). Верни JSON:
{{
  "score": 85,
  "feedback": "хорошо/плохо, что улучшить"
}}"""
        
        messages = [
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        parsed = self._extract_json(response_text)
        if not parsed:
            base_score = int((passed / total) * 100) if total > 0 else 0
            return {
                "score": base_score,
                "feedback": f"Пройдено тестов: {passed}/{total}"
            }
        
        return {
            "score": parsed.get("score", int((passed / total) * 100) if total > 0 else 0),
            "feedback": parsed.get("feedback", "")
        }

