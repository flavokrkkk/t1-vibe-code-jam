# ИИ-агент для проведения интервью

ИИ-агент для проведения технических интервью на базе SciBox LLM API.

## Установка

### Создание виртуального окружения

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
# На macOS/Linux:
source venv/bin/activate

# На Windows:
# venv\Scripts\activate

# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt
```

### Запуск API сервера

**Вариант 1: Автоматический запуск (рекомендуется)**
```bash
./start.sh
```

**Вариант 2: Ручной запуск**
```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate

# Запуск сервера
python run_api.py
```

Сервер будет доступен по адресу `http://localhost:8080`

### Тестирование

```bash
# Запуск тестов
pytest test_api.py -v

# Интерактивное тестирование диалога
python test_dialog.py
```

## Получение API ключа

1. Получите API ключ от SciBox
2. Установите переменную окружения:
```bash
export SCIBOX_API_KEY="your-api-key-here"
export SCIBOX_BASE_URL="https://llm.t1v.scibox.tech/v1"
```

Или используйте IP-адрес:
```bash
export SCIBOX_BASE_URL="http://45.145.191.148:4000/v1"
```

## API Эндпоинты

### Начало интервью

**POST `/start`** — начало интервью (обычный режим)

**POST `/start/stream`** — начало интервью (с использованием стриминга внутри)

Запрос:
```json
{
  "job_title": "Python Developer",
  "required_skills": ["Python", "FastAPI", "SQL"],
  "amount_of_tasks": 5,
  "session_id": "optional-session-id"
}
```

Ответ:
```json
{
  "session_id": "uuid-сессии",
  "step": {
    "type": "DIALOG",
    "question_text": "Текст первого вопроса",
    "status": "IN_PROGRESS",
    "score": null,
    "ai_feedback": "Приветствие и первый вопрос",
    "user_answer": null,
    "feedback": null,
    "next_step": {
      "type": "DIALOG",
      "question_text": "Следующий вопрос"
    }
  }
}
```

### Обработка ответа пользователя

**POST `/message`** — обработка ответа (обычный режим)

**POST `/message/stream`** — обработка ответа (с использованием стриминга внутри)

Запрос:
```json
{
  "session_id": "uuid-сессии",
  "user_answer": "Я работал с Python 3 года, использовал FastAPI для создания REST API."
}
```

Ответ:
```json
{
  "type": "DIALOG",
  "question_text": "Отличный опыт! Расскажите подробнее о вашем опыте с FastAPI.",
  "status": "IN_PROGRESS",
  "score": 85,
  "ai_feedback": "Кандидат показал хорошее понимание технологий.",
  "user_answer": "Я работал с Python 3 года...",
  "feedback": "Хороший ответ с конкретными примерами. Можно было упомянуть про async/await.",
  "next_step": {
    "type": "DIALOG",
    "question_text": "Следующий вопрос"
  }
}
```

### Генерация задачи на код

**POST `/generate_task`** — генерация полной задачи на программирование

Запрос:
```json
{
  "topic": "AsyncIO",
  "difficulty": "medium",
  "language": "python"
}
```

Ответ:
```json
{
  "description": "Подробное описание задачи",
  "initial_code": "class Solution(object):\n    def solve(self, ...):\n        pass",
  "test_cases": [
    {"input": "...", "output": "..."},
    {"input": "...", "output": "..."}
  ],
  "topic": "AsyncIO",
  "difficulty": "medium",
  "language": "python"
}
```

### Управление сессиями

**DELETE `/session/{session_id}`** — удаление сессии интервью

**GET `/health`** — проверка здоровья сервиса

## Разница между обычными и стриминг эндпоинтами

- **`/start` и `/message`** — используют `llm.invoke()` (обычный режим)
- **`/start/stream` и `/message/stream`** — используют `llm.stream()` внутри для получения ответа от LLM, но возвращают полный ответ клиенту (как обычные эндпоинты)

Оба типа эндпоинтов возвращают одинаковый формат ответа. Стриминг используется только внутри для оптимизации получения ответа от LLM.

## Использование InterviewAgent напрямую

```python
from interview_agent import InterviewAgent

agent = InterviewAgent()

first_question = agent.start_interview(
    job_title="Python Developer",
    required_skills=["Python", "FastAPI", "SQL"],
    amount_of_tasks=5
)

response = agent.process_answer("Мой ответ кандидата")
feedback = agent.generate_feedback()
```

## Параметры InterviewAgent

- `job_title`: Название вакансии
- `required_skills`: Список требуемых навыков
- `amount_of_tasks`: Количество задач для интервью (1-30)
- `model`: Модель SciBox (по умолчанию "qwen3-32b-awq")
- `api_key`: API ключ (опционально, можно через переменную окружения)

## Доступные модели SciBox

### Чат-модели

- `qwen3-32b-awq` (по умолчанию) — универсальная чат-модель, 2 RPS
- `qwen3-coder-30b-a3b-instruct-fp8` — кодовая модель, 2 RPS

### Эмбеддинг-модели

- `bge-m3` — эмбеддинг-модель для поиска и ранжирования, 7 RPS

## Примеры использования API

### Пример с curl

```bash
# Начало интервью
curl -X POST http://localhost:8080/start/stream \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Python Developer",
    "required_skills": ["Python", "FastAPI"],
    "amount_of_tasks": 5
  }'

# Отправка ответа
curl -X POST http://localhost:8080/message/stream \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "ваш-session-id",
    "user_answer": "Я работал с Python 3 года"
  }'
```

### Пример с Python requests

```python
import requests

BASE_URL = "http://localhost:8080"

# Начало интервью
response = requests.post(
    f"{BASE_URL}/start/stream",
    json={
        "job_title": "Python Developer",
        "required_skills": ["Python", "FastAPI", "SQL"],
        "amount_of_tasks": 5
    }
)
data = response.json()
session_id = data["session_id"]
print(f"Первый вопрос: {data['step']['question_text']}")

# Отправка ответа
response = requests.post(
    f"{BASE_URL}/message/stream",
    json={
        "session_id": session_id,
        "user_answer": "Я работал с Python 3 года, использовал FastAPI."
    }
)
step = response.json()
print(f"Ответ интервьюера: {step['question_text']}")
print(f"Оценка: {step.get('score')}")
```

## Ограничения RPS

- `qwen3-32b-awq`: 2 RPS
- `qwen3-coder-30b-a3b-instruct-fp8`: 2 RPS
- `bge-m3`: 7 RPS

Ограничение распространяется на всю команду (workspace). При параллельных запросах используйте очереди или синхронизацию.

## Retry логика

`SciBoxClient` автоматически обрабатывает ошибки 429, 500, 502, 503 с экспоненциальным backoff (до 3 попыток по умолчанию).

## Особенности моделей

### qwen3-32b-awq

Поддерживает режим reasoning/thinking. Для отключения добавьте `/no_think` в начало system prompt:
```python
{"role": "system", "content": "/no_think Ты помощник"}
```

### qwen3-coder-30b-a3b-instruct-fp8

Оптимизирована для задач ревью, генерации и объяснения кода. Рекомендуется использовать с `temperature=0.2-0.3`.
