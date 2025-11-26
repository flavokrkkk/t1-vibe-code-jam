#!/bin/bash

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

echo "Активация виртуального окружения..."
source venv/bin/activate

echo "Установка/обновление зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Запуск API сервера..."
python run_api.py

