#!/bin/bash

echo "Запуск деплоя catty-reminders-app..."
echo "======================================"

REPO_DIR=$(pwd) 
SERVICE_NAME="catty-app"

DEPLOY_REF=$1
#DEPLOY_REF="$(git rev-parse HEAD)"

echo "Текущий SHA ветки: $DEPLOY_REF"
echo "DEPLOY_REF=$DEPLOY_REF" > /home/deemeed/catty-reminders-app/.env

echo "Перезапуск сервиса..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

cd $REPO_DIR

echo "Деплой успешно завершен!"