#!/bin/bash

echo "Запуск деплоя catty-reminders-app..."
echo "======================================"

APP_DIR="/home/deemeed/catty-reminders-app"
REPO_DIR=$(pwd) 
SERVICE_NAME="catty-app"

if [ -n "$1" ]; then
    DEPLOY_REF="$1"
else
    DEPLOY_REF="$(git rev-parse HEAD)"
fi

echo "Текущий SHA ветки: $DEPLOY_REF"
echo "DEPLOY_REF=$DEPLOY_REF" > /home/deemeed/catty-reminders-app/.env

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

echo "Перезапуск сервиса..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

cd $REPO_DIR

echo "Деплой успешно завершен!"