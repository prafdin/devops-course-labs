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

echo "=== Переходим на commit ==="
git checkout --detach $DEPLOY_REF

echo "Текущий SHA релиза: $DEPLOY_REF"

# ⭐ СОЗДАЕМ ФАЙЛ С ПЕРЕМЕННЫМИ ДЛЯ SYSTEMD
echo "DEPLOY_REF=$DEPLOY_REF" |  tee /etc/catty-app-env

# Также создаем .env файл в проекте (на всякий случай)
echo "DEPLOY_REF=$DEPLOY_REF" > $APP_DIR/.env

if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        echo "=== Создание виртуального окружения ==="
        python3 -m venv venv
    fi
    echo "=== Активация виртуального окружения ==="
    source venv/bin/activate
    echo "=== Установка зависимостей ==="
    pip install -r requirements.txt
fi

echo "=== Перезапуск приложения ==="
sudo systemctl daemon-reload
sudo systemctl restart catty
