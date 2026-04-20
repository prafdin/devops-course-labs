#!/bin/bash

echo "======================================"
echo "Начинаем деплой сервиса..."
echo "======================================"

SERVICE="catty-app"

DEPLOY_REF=$1
echo "DEPLOY_REF=$DEPLOY_REF" > /home/mb/catty-reminders-app/.env

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE
sudo systemctl restart $SERVICE

sleep 2

if systemctl is-active --quiet $SERVICE; then
    echo "ДЕПЛОЙ УСПЕШНО ЗАВЕРШЕН!"
else
    echo "ОШИБКА! СЕРВИС НЕ ЗАПУСТИЛСЯ"
fi