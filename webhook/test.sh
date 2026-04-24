#!/bin/bash
set -e

BRANCH=$1
APP_DIR="/home/ubuntu/devops/catty-reminders-app"
VENV="$APP_DIR/venv"

echo "=== Запуск тестов проекта ветки $BRANCH ==="

cd "$APP_DIR"

DEPLOY_REF="$(git rev-parse HEAD)"

echo "Текущий SHA ветки $BRANCH: $DEPLOY_REF"
echo "DEPLOY_REF=$DEPLOY_REF" > /home/ubuntu/devops/catty-reminders-app/.env

# Проверяем и создаем виртуальное окружение если нужно
if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        echo "=== создание виртуального окружения $BRANCH ==="
        python3 -m venv venv
    fi
    echo "=== активация виртуального окружения $BRANCH ==="
    source venv/bin/activate
    echo "=== установка зависимостей $BRANCH ==="
    pip install -r requirements.txt
fi

echo "Текущая директория: $(pwd)"

# Запускаем приложение для тестов
echo "=== запуск приложения $BRANCH для тестов ==="
# Останавливаем старый процесс если есть
pkill -f "uvicorn app.main:app" || true

# Запускаем приложение в фоне
source venv/bin/activate
nohup uvicorn app.main:app --reload --host 127.0.0.1 --port 8181 > /tmp/app.log 2>&1 &
APP_PID=$!

# Ждем запуска приложения
sleep 5

# Запускаем тесты
echo "=== Выполняем тесты из папки tests ==="
export PYTHONPATH=/home/ubuntu/devops/catty-reminders-app:$PYTHONPATH
PLAYWRIGHT_BROWSERS_PATH=/home/ubuntu/.cache/ms-playwright pytest tests --maxfail=1 --disable-warnings -q
RESULT=$?

# Останавливаем приложение
kill $APP_PID 2>/dev/null || true

exit $RESULT
