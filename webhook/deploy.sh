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

# Перезапускаем через systemd
echo "=== Перезапуск сервиса ==="
sudo systemctl daemon-reload
sudo systemctl restart app.service

echo "=== Деплой завершен ==="
