#!/bin/bash
set -e
REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
cd "$REPO_DIR"

source .venv/bin/activate

playwright install chromium

pip install -r requirements.txt -q

echo "[TEST] Запуск временного сервера для тестов..."
uvicorn main:app --host 127.0.0.1 --port 8181 > /tmp/test_app.log 2>&1 &
APP_PID=$!
sleep 3

echo "[TEST] Запуск pytest..."
set +e 
python3 -m pytest -v
RESULT=$?

kill $APP_PID
exit $RESULT
