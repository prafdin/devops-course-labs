#!/bin/bash
set -e

BRANCH=$1
APP_DIR="/home/ubuntu/devops/catty-reminders-app"

echo "=== Запуск тестов проекта ветки $BRANCH ==="

cd "$APP_DIR"

# Обновляем .env файл
DEPLOY_REF="$(git rev-parse HEAD)"
echo "DEPLOY_REF=$DEPLOY_REF" > "$APP_DIR/.env"
echo "Текущий SHA: $DEPLOY_REF"

# Активируем окружение
source venv/bin/activate

# Проверяем и устанавливаем Playwright браузер если нужно
if [ ! -d "/home/ubuntu/.cache/ms-playwright/chromium_headless_shell-1208" ]; then
    echo "=== Устанавливаем Playwright браузер ==="
    playwright install chromium
fi

# Запускаем приложение в фоне
echo "Запускаем приложение..."
pkill -f "uvicorn app.main:app" || true
nohup uvicorn app.main:app --host 127.0.0.1 --port 8181 > /tmp/uvicorn.log 2>&1 &
APP_PID=$!

# Ждем запуска
sleep 5

# Проверяем что приложение запустилось
if curl -s http://127.0.0.1:8181/login > /dev/null 2>&1; then
    echo "✅ Приложение запущено"
else
    echo "❌ Приложение не запустилось"
    cat /tmp/uvicorn.log
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

# Запускаем тесты
echo "Выполняем тесты..."
export PYTHONPATH=$APP_DIR:$PYTHONPATH
PLAYWRIGHT_BROWSERS_PATH=/home/ubuntu/.cache/ms-playwright pytest tests --maxfail=1 --disable-warnings -q
RESULT=$?

# Останавливаем приложение
kill $APP_PID 2>/dev/null || true

exit $RESULT
