#!/bin/bash

API_URL="http://localhost:8000"

echo "=== Простое тестирование диалога ==="
echo ""

echo "1. Начинаем интервью..."
START_RESPONSE=$(curl -s -X POST "${API_URL}/start" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Python Developer",
    "required_skills": ["Python", "FastAPI", "SQL"],
    "amount_of_tasks": 3
  }')

SESSION_ID=$(echo "$START_RESPONSE" | grep -oE '"session_id"\s*:\s*"[a-f0-9\-]{36}"' | grep -oE '[a-f0-9\-]{36}' | head -1)

if [ -z "$SESSION_ID" ]; then
    echo "Ошибка: не удалось получить session_id"
    exit 1
fi

echo "Session ID: $SESSION_ID"
echo ""

QUESTION=$(echo "$START_RESPONSE" | python3 -c "
import sys, json, re
try:
    text = sys.stdin.read()
    text_cleaned = re.sub(r'<[^>]+>', '', text)
    text_cleaned = re.sub(r'\n', ' ', text_cleaned)
    text_cleaned = re.sub(r'\s+', ' ', text_cleaned)
    data = json.loads(text_cleaned)
    print(data['step']['question_text'][:200])
except:
    print('Вопрос получен')
" 2>/dev/null)

echo "[Интервьюер]: $QUESTION"
echo ""

for i in 1 2 3; do
    echo "--- Шаг $i ---"
    read -p "[Вы]: " USER_ANSWER
    
    if [ -z "$USER_ANSWER" ]; then
        USER_ANSWER="Пропускаю этот вопрос"
    fi
    
    RESPONSE=$(curl -s -X POST "${API_URL}/message" \
      -H "Content-Type: application/json" \
      -d "{
        \"session_id\": \"$SESSION_ID\",
        \"user_answer\": \"$USER_ANSWER\"
      }")
    
    QUESTION=$(echo "$RESPONSE" | python3 -c "
import sys, json, re
try:
    text = sys.stdin.read()
    text_cleaned = re.sub(r'<[^>]+>', '', text)
    text_cleaned = re.sub(r'\n', ' ', text_cleaned)
    text_cleaned = re.sub(r'\s+', ' ', text_cleaned)
    data = json.loads(text_cleaned)
    q = data.get('question_text', '')[:300]
    print(q)
    if data.get('status') == 'COMPLETED':
        print('\\n[СТАТУС: ЗАВЕРШЕНО]')
except:
    print('Ответ получен')
" 2>/dev/null)
    
    echo ""
    echo "[Интервьюер]: $QUESTION"
    echo ""
    
    if echo "$RESPONSE" | grep -q '"status"\s*:\s*"COMPLETED"'; then
        echo "Интервью завершено!"
        break
    fi
done

echo ""
echo "Удаление сессии..."
curl -s -X DELETE "${API_URL}/session/${SESSION_ID}" > /dev/null
echo "Готово!"

