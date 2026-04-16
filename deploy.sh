#!/bin/bash

echo "Запуск деплоя catty-reminders-app..."
echo "======================================"

APP_DIR="/opt/catty-reminders-app"
REPO_DIR=$(pwd) 
SERVICE_NAME="catty-app"

DEPLOY_REF=$1

#DEPLOY_REF="$(git rev-parse HEAD)"


echo "Текущий SHA ветки: $DEPLOY_REF"
echo "DEPLOY_REF=$DEPLOY_REF" > /home/deemeed/catty-reminders-app/.env

# echo "DEPLOY_REF=$DEPLOY_REF" | sudo tee "$APP_DIR/.env" > /dev/null

# cd "$REPO_DIR" || { echo "Ошибка: не удалось зайти в $REPO_DIR"; exit 1; }

# sudo find "$APP_DIR" -maxdepth 1 ! -name 'venv' ! -name '.env' ! -name '.' -exec rm -rf {} +
# echo "Копирование файлов..."
# sudo cp -r . "$APP_DIR/"
# sudo rm -rf "$APP_DIR/.git"
# sudo rm -rf "$APP_DIR/.gitignore"
# if [ ! -d "$APP_DIR/venv" ]; then
#     echo "Создание виртуального окружения..."
#     sudo python3 -m venv "$APP_DIR/venv"
# fi
# sudo "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"
# sudo chown -R deemeed:deemeed "$APP_DIR"


echo "Перезапуск сервиса..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

cd $REPO_DIR

echo "Деплой успешно завершен!"