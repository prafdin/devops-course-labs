#!/bin/bash
set -e

BRANCH=$1
APP_DIR="/home/ubuntu/devops/catty-reminders-app"

echo "=== DEPLOY ветки $BRANCH ==="

cd $APP_DIR

# Обновляем код
git fetch origin
git checkout -B $BRANCH origin/$BRANCH
git reset --hard origin/$BRANCH

# Обновляем .env с новым SHA
DEPLOY_REF="$(git rev-parse HEAD)"
echo "DEPLOY_REF=$DEPLOY_REF" > "$APP_DIR/.env"
echo "Текущий SHA: $DEPLOY_REF"

# Обновляем зависимости
if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        echo "=== создание виртуального окружения ==="
        python3 -m venv venv
    fi
    source venv/bin/activate
    echo "=== установка зависимостей ==="
    pip install -r requirements.txt
fi

# Останавливаем приложение
echo "=== Останавливаем приложение ==="
pkill -f "uvicorn app.main:app" || true
sleep 3

# Запускаем приложение заново
echo "=== Запускаем приложение ==="
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8081 > /tmp/app.log 2>&1 &
NEW_PID=$!
echo "Приложение запущено с PID: $NEW_PID"

# Проверяем что запустилось
sleep 3
if ps -p $NEW_PID > /dev/null; then
    echo "✅ Приложение успешно запущено"
else
    echo "❌ Ошибка запуска приложения"
    cat /tmp/app.log
    exit 1
fi

echo "=== Деплой завершен ==="
