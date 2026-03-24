#!/bin/bash

echo "Запуск деплоя catty-reminders-app..."
echo "======================================"

APP_DIR="/home/deemeed/catty-reminders-app"
REPO_DIR=$(pwd)  # Текущая директория
PORT=8181
SERVICE_NAME="catty-app"

sudo mkdir -p $APP_DIR

echo "Копирование файлов в $APP_DIR..."
sudo rsync -av --delete \
    --exclude '.git' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.pytest_cache' \
    --exclude '.env' \
    ./ $APP_DIR/

if [ ! -d "$APP_DIR/venv" ]; then
    echo "Создание виртуального окружения..."
    cd $APP_DIR
    sudo python3 -m venv venv
    cd $REPO_DIR
fi

if [ -f "/home/$USER/catty-env/.env" ]; then
    echo "Копирование .env файла..."
    sudo cp /home/$USER/catty-env/.env $APP_DIR/
else
    echo ".env файл не найден! Создаю из шаблона..."
    sudo cp .env.example $APP_DIR/.env
    echo "НЕ ЗАБУДЬ отредактировать $APP_DIR/.env с реальными данными!"
fi

DEPLOY_REF="$(git rev-parse HEAD)"

echo "Текущий SHA ветки $BRANCH: $DEPLOY_REF"
echo "DEPLOY_REF=$DEPLOY_REF" > /home/deemeed/catty-reminders-app/.env

echo "Перезапуск сервиса..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

cd $REPO_DIR

echo "Деплой успешно завершен!"