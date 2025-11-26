FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей (если понадобятся, например для сборки пакетов)
# RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Порт, на котором работает ML API
EXPOSE 8080

# Команда запуска с параметрами для SSE стриминга
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "300", "--timeout-graceful-shutdown", "30"]

