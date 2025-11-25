#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until python -c "
import asyncio
import sys
import os

# Получаем DATABASE_URL из переменной окружения
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print('DATABASE_URL not set', file=sys.stderr)
    sys.exit(1)

# Конвертируем postgresql:// в postgresql+asyncpg:// для async
async_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_db():
    try:
        engine = create_async_engine(async_url)
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        await engine.dispose()
        return True
    except Exception as e:
        print(f'DB check failed: {e}', file=sys.stderr)
        return False

if asyncio.run(check_db()):
    sys.exit(0)
else:
    sys.exit(1)
" 2>&1; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"

