#!/bin/bash
REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
cd "$REPO_DIR"
source .venv/bin/activate

fuser -k 8181/tcp || true

echo "[TEST] Запуск сервера..."
uvicorn app.main:app --host 127.0.0.1 --port 8181 > /tmp/test_app.log 2>&1 &
APP_PID=$!

sleep 5

echo "[TEST] Запуск pytest..."
python3 -m pytest -v
RESULT=$?

kill $APP_PID || true
exit $RESULT
