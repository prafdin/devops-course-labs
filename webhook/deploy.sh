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

# Обновляем зависимости
source venv/bin/activate
pip install -r requirements.txt

# Перезапускаем сервис
echo "=== Перезапуск приложения ==="
pkill -f "uvicorn app.main:app" || true
sleep 2
nohup uvicorn app.main:app --host 0.0.0.0 --port 8081 > /tmp/app.log 2>&1 &

echo "=== Деплой завершен ==="
