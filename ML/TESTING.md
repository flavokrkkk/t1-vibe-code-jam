# Тестирование Interview Agent API

## Запуск сервера

Перед тестированием необходимо запустить сервер:

```bash
cd ML
python run_api.py
```

Или через uvicorn:

```bash
cd ML
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: `http://localhost:8000`

## Автоматические тесты (pytest)

Запуск всех тестов:

```bash
cd ML
pytest test_api.py -v
```

Запуск конкретного теста:

```bash
pytest test_api.py::test_start_interview -v
```

Запуск с покрытием:

```bash
pytest test_api.py --cov=api --cov-report=html
```

## Ручное тестирование

### 1. Python скрипт

```bash
cd ML
python test_api_examples.py
```

### 2. Bash скрипт

```bash
cd ML
chmod +x test_api_examples.sh
./test_api_examples.sh
```

### 3. Через curl

#### Проверка здоровья сервиса:
```bash
curl -X GET http://localhost:8000/health
```

#### Начало интервью:
```bash
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Python Developer",
    "required_skills": ["Python", "FastAPI", "SQL"],
    "amount_of_tasks": 5
  }'
```

Сохраните `session_id` из ответа для следующих запросов.

#### Отправка ответа пользователя:
```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "ВАШ_SESSION_ID",
    "user_answer": "Я работал с Python 3 года"
  }'
```

#### Удаление сессии:
```bash
curl -X DELETE http://localhost:8000/session/ВАШ_SESSION_ID
```

### 4. Через Python requests

```python
import requests

API_URL = "http://localhost:8000"

# Начало интервью
response = requests.post(f"{API_URL}/start", json={
    "job_title": "Python Developer",
    "required_skills": ["Python", "FastAPI"],
    "amount_of_tasks": 3
})
session_id = response.json()["session_id"]

# Отправка ответа
response = requests.post(f"{API_URL}/message", json={
    "session_id": session_id,
    "user_answer": "Мой ответ"
})
print(response.json())
```

## Тестирование через Swagger UI

После запуска сервера откройте в браузере:

```
http://localhost:8000/docs
```

Там можно:
- Просмотреть все эндпоинты
- Протестировать API интерактивно
- Увидеть схемы запросов и ответов

## Примеры запросов

### Успешное начало интервью

**Запрос:**
```json
POST /start
{
  "job_title": "Backend Developer",
  "required_skills": ["Python", "Django", "PostgreSQL"],
  "amount_of_tasks": 5
}
```

**Ответ:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "step": {
    "type": "DIALOG",
    "question_text": "Здравствуйте! Начнем интервью...",
    "status": "IN_PROGRESS",
    "score": null,
    "ai_feedback": null,
    "user_answer": null,
    "feedback": null
  }
}
```

### Обработка ответа

**Запрос:**
```json
POST /message
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_answer": "Я работал с Python 3 года"
}
```

**Ответ:**
```json
{
  "type": "DIALOG",
  "question_text": "Отлично! Расскажите подробнее...",
  "status": "IN_PROGRESS",
  "score": 75,
  "ai_feedback": "Кандидат показал хорошие знания...",
  "user_answer": "Я работал с Python 3 года",
  "feedback": "Хороший ответ"
}
```

### Завершенное интервью

**Ответ:**
```json
{
  "type": "DIALOG",
  "question_text": "Спасибо за интервью!",
  "status": "COMPLETED",
  "score": 85,
  "ai_feedback": "Итоговая обратная связь...",
  "user_answer": "Последний ответ",
  "feedback": "Итоговая обратная связь"
}
```

## Проверка ошибок

### Несуществующая сессия
```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "invalid-id",
    "user_answer": "Тест"
  }'
```
Ожидается: `404 Not Found`

### Невалидные данные
```bash
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "",
    "required_skills": [],
    "amount_of_tasks": 0
  }'
```
Ожидается: `422 Unprocessable Entity`

## Переменные окружения

Убедитесь, что установлены необходимые переменные:

```bash
export SCIBOX_API_KEY="your-api-key"
export SCIBOX_BASE_URL="https://llm.t1v.scibox.tech/v1"
```

Или создайте файл `.env`:

```
SCIBOX_API_KEY=your-api-key
SCIBOX_BASE_URL=https://llm.t1v.scibox.tech/v1
```

