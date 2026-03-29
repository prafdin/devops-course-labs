#!/bin/bash
cd ~/catty-reminders-app

SHA=$1  # Берем хеш из аргумента, который прислал GitHub

# 1. Принудительно качаем ВСЕ ветки и хеши из Гитхаба
git fetch --all
git reset --hard $SHA

# 2. Убиваем старые процессы
sudo pkill -9 -f "app.main" || true
sudo pkill -9 -f "uvicorn" || true

# 3. Устанавливаем зависимости
pip install -r requirements.txt --user

# 4. ЗАПУСК 
# Мы передаем хеш в переменную окружения DEPLOY_REF, 
# чтобы приложение ОБЯЗАТЕЛЬНО показало его боту.
export DEPLOY_REF=$SHA
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8181 </dev/null > deploy.log 2>&1 &

echo "Deployed SHA: $SHA"
exit 0
