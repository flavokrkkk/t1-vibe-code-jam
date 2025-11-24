# Решение проблем с Docker

## Проблема: "failed to resolve source metadata" при сборке frontend

Эта ошибка обычно возникает из-за проблем с сетью или временной недоступностью Docker Hub.

### Решения:

#### 1. Повторите попытку
Часто это временная проблема с Docker Hub:
```bash
docker compose -f compose.yaml up -d --build frontend
```

#### 2. Проверьте подключение к Docker Hub
```bash
docker pull node:20-slim
docker pull nginx:alpine
```

#### 3. Очистите кэш Docker
```bash
docker system prune -a
docker compose -f compose.yaml build --no-cache frontend
```

#### 4. Проверьте настройки DNS в Docker
Если используете VPN или прокси, проверьте настройки DNS в Docker Desktop:
- Settings → Docker Engine → добавьте:
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

#### 5. Используйте альтернативный registry (если Docker Hub недоступен)
Можно использовать зеркала или другие registry, но это требует изменения Dockerfile.

#### 6. Проверьте файрвол/антивирус
Убедитесь, что Docker Desktop имеет доступ к интернету через файрвол.

#### 7. Перезапустите Docker Desktop
Иногда помогает простой перезапуск Docker Desktop.

### Если проблема сохраняется:

Попробуйте собрать образ вручную с более подробным выводом:
```bash
cd frontend
docker build -t frontend-test -f Dockerfile .
```

Это поможет увидеть, на каком именно этапе происходит ошибка.

