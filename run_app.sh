#!/bin/bash
cd ~/catty-reminders-app
git fetch origin lab2
git reset --hard origin/lab2
pip install -r requirements.txt
pkill -f "app.main" || true
# Запускаем приложение и полностью отвязываем его от терминала
nohup python3 -m app.main --port 8181 > deploy.log 2>&1 &
exit 0
