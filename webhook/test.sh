#!/bin/bash
REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
cd "$REPO_DIR"

source .venv/bin/activate

echo "[TEST] Запуск временного сервера..."
uvicorn main:app --host 0.0.0.0 --port 8181 > /tmp/test_app.log 2>&1 &
APP_PID=$!

echo "[TEST] Ожидание готовности порта 8181..."
for i in {1..10}; do
    if nc -z 127.0.0.1 8181; then
        echo "Порт доступен!"
        break
    fi
    sleep 1
done

echo "[TEST] Запуск pytest..."
python3 -m pytest -v --base-url http://127.0.0.1:8181
RESULT=$?

kill $APP_PID || true
exit $RESULT
