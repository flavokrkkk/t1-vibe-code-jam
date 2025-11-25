# ИИ-агент для проведения интервью

ИИ-агент для проведения технических интервью на базе SciBox LLM API.

## Установка

```bash
pip install -r requirements.txt
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

## Использование InterviewAgent

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
- `amount_of_tasks`: Количество задач для интервью
- `model`: Модель SciBox (по умолчанию "qwen3-32b-awq")
- `api_key`: API ключ (опционально, можно через переменную окружения)

## Доступные модели SciBox

### Чат-модели

- `qwen3-32b-awq` (по умолчанию) — универсальная чат-модель, 2 RPS
- `qwen3-coder-30b-a3b-instruct-fp8` — кодовая модель, 2 RPS

### Эмбеддинг-модели

- `bge-m3` — эмбеддинг-модель для поиска и ранжирования, 7 RPS

## Использование SciBoxClient

```python
from scibox_client import SciBoxClient

client = SciBoxClient()

# Чат-запрос
response = client.chat_completion(
    messages=[
        {"role": "system", "content": "/no_think Ты помощник"},
        {"role": "user", "content": "Привет!"}
    ],
    model="qwen3-32b-awq",
    temperature=0.7,
    max_tokens=256
)
print(response.choices[0].message.content)

# Эмбеддинги
emb = client.embeddings(
    input_text=["Текст 1", "Текст 2"],
    model="bge-m3"
)
```

## Работа с эмбеддингами

```python
from embeddings_utils import get_embeddings, find_most_similar, cosine_similarity

# Получение эмбеддингов
embeddings = get_embeddings(["Текст 1", "Текст 2"])

# Поиск похожих текстов
results = find_most_similar(
    query="Запрос",
    candidate_texts=["Текст 1", "Текст 2", "Текст 3"],
    top_k=2
)

# Сравнение схожести
similarity = cosine_similarity(embeddings[0], embeddings[1])
```

## Примеры

Запустите `scibox_example.py` для просмотра примеров использования всех возможностей API:

```bash
python scibox_example.py
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
