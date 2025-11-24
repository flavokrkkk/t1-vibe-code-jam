# ИИ-агент для проведения интервью

ИИ-агент для проведения технических интервью на базе Groq API (Llama модели).

## Установка

```bash
pip install -r requirements.txt
```

## Получение API ключа

1. Перейдите на https://console.groq.com/keys
2. Зарегистрируйтесь (бесплатно)
3. Создайте новый API ключ
4. Установите переменную окружения:
```bash
export GROQ_API_KEY="your-api-key-here"
```

## Использование

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

## Параметры

- `job_title`: Название вакансии
- `required_skills`: Список требуемых навыков
- `amount_of_tasks`: Количество задач для интервью
- `model`: Модель Groq (по умолчанию "llama-3.3-70b-versatile")

## Доступные модели

- `llama-3.3-70b-versatile` (по умолчанию)
- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`
