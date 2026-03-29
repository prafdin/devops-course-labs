#!/bin/bash
cd ~/catty-reminders-app

# 1. Принудительно чистим и обновляем код
git fetch origin lab2
git reset --hard origin/lab2

# 2. Убиваем старые процессы (жестко)
pkill -9 -f "app.main" || true
pkill -9 -f "uvicorn" || true

# 3. Устанавливаем зависимости
pip install -r requirements.txt --user

# 4. Запускаем через uvicorn
# Добавим задержку, чтобы логи успели записаться
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8181 > deploy.log 2>&1 &

# 5. Проверка порта
sleep 5
if sudo ss -tulpn | grep -q ":8181"; then
    echo "SUCCESS: Port 8181 is open."
else
    echo "ERROR: Port 8181 is NOT open. Log content:"
    cat deploy.log
    exit 1
fi
exit 0
