#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"

echo -e "${BLUE}=== Тестирование Interview Agent API ===${NC}\n"

# Проверка здоровья сервиса
echo -e "${YELLOW}1. Проверка здоровья сервиса...${NC}"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "${API_URL}/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Сервис работает${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ Сервис не отвечает (HTTP $HTTP_CODE)${NC}"
    echo "Убедитесь, что сервер запущен: python3 run_api.py"
    exit 1
fi

echo ""

# Начало интервью
echo -e "${YELLOW}2. Начало интервью...${NC}"
START_RESPONSE=$(curl -s -X POST "${API_URL}/start" \
    -H "Content-Type: application/json" \
    -d '{
        "job_title": "Python Developer",
        "required_skills": ["Python", "FastAPI", "SQL"],
        "amount_of_tasks": 3
    }' \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$START_RESPONSE" | tail -n1)
BODY=$(echo "$START_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Интервью начато${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    
    # Извлечение session_id
    SESSION_ID=$(echo "$BODY" | python3 -c "
import sys, json, re
try:
    data = json.load(sys.stdin)
    print(data.get('session_id', ''))
except:
    text = sys.stdin.read()
    match = re.search(r'\"session_id\"\s*:\s*\"([a-f0-9\-]{36})\"', text)
    if match:
        print(match.group(1))
" 2>/dev/null)
    
    if [ -z "$SESSION_ID" ]; then
        echo -e "${RED}✗ Не удалось извлечь session_id${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Session ID: $SESSION_ID${NC}"
else
    echo -e "${RED}✗ Ошибка при начале интервью (HTTP $HTTP_CODE)${NC}"
    echo "$BODY"
    exit 1
fi

echo ""

# Отправка первого ответа
echo -e "${YELLOW}3. Отправка первого ответа...${NC}"
ANSWER1="Я использую Python уже 3 года, работал с FastAPI и SQLAlchemy"
MESSAGE_RESPONSE=$(curl -s -X POST "${API_URL}/message" \
    -H "Content-Type: application/json" \
    -d "{
        \"session_id\": \"$SESSION_ID\",
        \"user_answer\": \"$ANSWER1\"
    }" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$MESSAGE_RESPONSE" | tail -n1)
BODY=$(echo "$MESSAGE_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Ответ обработан${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ Ошибка при обработке сообщения (HTTP $HTTP_CODE)${NC}"
    echo "$BODY"
fi

echo ""

# Отправка второго ответа
echo -e "${YELLOW}4. Отправка второго ответа...${NC}"
ANSWER2="Я не знаю, что такое декораторы"
MESSAGE_RESPONSE2=$(curl -s -X POST "${API_URL}/message" \
    -H "Content-Type: application/json" \
    -d "{
        \"session_id\": \"$SESSION_ID\",
        \"user_answer\": \"$ANSWER2\"
    }" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$MESSAGE_RESPONSE2" | tail -n1)
BODY=$(echo "$MESSAGE_RESPONSE2" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Ответ обработан${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ Ошибка при обработке сообщения (HTTP $HTTP_CODE)${NC}"
    echo "$BODY"
fi

echo ""

# Отправка третьего ответа
echo -e "${YELLOW}5. Отправка третьего ответа...${NC}"
ANSWER3="Я работал с асинхронным программированием в Python, использовал asyncio и aiohttp"
MESSAGE_RESPONSE3=$(curl -s -X POST "${API_URL}/message" \
    -H "Content-Type: application/json" \
    -d "{
        \"session_id\": \"$SESSION_ID\",
        \"user_answer\": \"$ANSWER3\"
    }" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$MESSAGE_RESPONSE3" | tail -n1)
BODY=$(echo "$MESSAGE_RESPONSE3" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Ответ обработан${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ Ошибка при обработке сообщения (HTTP $HTTP_CODE)${NC}"
    echo "$BODY"
fi

echo ""

# Удаление сессии
echo -e "${YELLOW}6. Удаление сессии...${NC}"
DELETE_RESPONSE=$(curl -s -X DELETE "${API_URL}/session/$SESSION_ID" -w "\n%{http_code}")
HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)
BODY=$(echo "$DELETE_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Сессия удалена${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ Ошибка при удалении сессии (HTTP $HTTP_CODE)${NC}"
    echo "$BODY"
fi

echo ""
echo -e "${GREEN}=== Тестирование завершено ===${NC}"

