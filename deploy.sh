#!/bin/bash
set -e

DEPLOY_REF=$1
REPO_URL="git@github.com:Rovver52/catty-reminders-app"
APP_DIR="/home/rover/catty-reminders-app"

echo "=== DEPLOY релиза ==="

if [ ! -d "$APP_DIR/.git" ]; then
    echo "Первый запуск — клонирование"
    git clone $REPO_URL $APP_DIR
fi

cd $APP_DIR

echo "=== Подтягиваем обновления ==="
git fetch --all --tags

echo "=== Переходим на  commit ==="
git checkout --detach $DEPLOY_REF

echo "Текущий SHA релиза: $DEPLOY_REF"
echo "DEPLOY_REF=$DEPLOY_REF" > /home/rover/catty-reminders-app/.env.deploy

if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        echo "=== создание виртуального окружения==="
        python -m venv venv
    fi
    echo "=== запуск виртуального окружения ==="
    source venv/bin/activate
    echo "=== установка зависимостей ==="
    pip install -r requirements.txt
fi

echo "=== запуск приложения ==="
sudo systemctl restart myapp
