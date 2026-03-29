#!/bin/bash
cd ~/catty-reminders-app

# 1. Сбрасываем все локальные изменения и принудительно тянем код
git fetch origin lab2
git reset --hard origin/lab2

# 2. Убиваем старые процессы принудительно (-9)
pkill -9 -f "app.main" || true
pkill -9 -f "uvicorn" || true

# 3. Запускаем приложение
nohup python3 -m app.main --port 8181 > deploy.log 2>&1 &

# Даем время на запуск
sleep 5
exit 0
