# AI Interview Assistant - FastAPI Backend

Production-ready бэкенд на FastAPI для системы AI-интервью.

## Структура проекта

```
backend_fastapi/
├── api/
│   └── v1/
│       ├── endpoints/      # API эндпоинты
│       ├── schemas/         # Pydantic схемы
│       └── services/        # Бизнес-логика
├── core/
│   ├── config.py           # Настройки приложения
│   ├── exceptions.py      # Кастомные исключения
│   ├── logging.py          # Настройка логирования
│   └── security.py         # JWT и безопасность
├── db/
│   ├── models.py           # SQLAlchemy модели
│   └── session.py          # Сессии БД
├── main.py                 # Точка входа
├── requirements.txt        # Зависимости
├── Dockerfile              # Docker образ
└── docker-compose.yml      # Docker Compose конфигурация
```

## Установка и запуск

### Локальная разработка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Настройте переменные окружения в `.env`

5. Запустите приложение:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

1. Запустите через Docker Compose:
```bash
docker-compose up -d
```

2. Приложение будет доступно по адресу: http://localhost:8000

3. Документация API:
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Аутентификация
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `POST /api/auth/refresh-token` - Обновление токена

### Пользователи
- `GET /api/user/` - Получение текущего пользователя

### Интервью
- `POST /api/interviews/` - Создание интервью
- `GET /api/interviews/` - Список интервью пользователя
- `GET /api/interviews/{id}` - Получение интервью по ID
- `POST /api/interviews/{id}/message` - Отправка сообщения
- `POST /api/interviews/{id}/steps/{step_id}/code` - Отправка кода
- `POST /api/interviews/{id}/audio` - Отправка аудио

## Технологии

- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy 2.0+** - ORM с async поддержкой
- **Pydantic v2** - валидация данных
- **PostgreSQL** - база данных
- **JWT** - аутентификация
- **Argon2** - хеширование паролей
- **Ollama** - LLM для генерации ответов
- **AssemblyAI** - транскрипция аудио

## Безопасность

- JWT токены для аутентификации
- Argon2 для хеширования паролей
- Валидация всех входных данных через Pydantic
- CORS настройки
- Защита от SQL injection через SQLAlchemy

## Миграции БД

Для работы с миграциями используйте Alembic:

```bash
# Создание миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## Тестирование

```bash
# Запуск тестов
pytest

# С покрытием
pytest --cov=api --cov=core --cov=db
```

## Production

Для production рекомендуется:

1. Использовать переменные окружения для секретов
2. Настроить HTTPS
3. Использовать reverse proxy (nginx)
4. Настроить логирование
5. Использовать миграции Alembic вместо auto-create
6. Настроить мониторинг и алерты

## Лицензия

MIT

