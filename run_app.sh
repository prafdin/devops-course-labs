#!/bin/bash
# 1. Заходим в папку проекта
cd /home/vboxuser/lab2/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

# 2. Обновляем код из GitHub
git fetch --all
git reset --hard "$SHA"

# 3. Обновляем зависимости
/home/vboxuser/lab2/catty-reminders-app/venv/bin/python -m pip install -r requirements.txt

# 4. Останавливаем старый процесс на порту 8181
pkill -f "uvicorn.*app.main" || true
sleep 2

# 5. Запускаем приложение с переменной окружения (в фоне)
cd /home/vboxuser/lab2/catty-reminders-app
export DEPLOY_REF=$SHA
nohup /home/vboxuser/lab2/catty-reminders-app/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8181 > /tmp/catty-app.log 2>&1 &

# 6. Ждём запуска
sleep 5

# 7. Проверяем, запустилось ли
if pgrep -f "uvicorn.*app.main" > /dev/null; then
    echo "SUCCESS: Deployed $SHA"
    exit 0
else
    echo "ERROR: App failed to start"
    exit 1
fi
