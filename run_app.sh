#!/bin/bash
# Заходим в папку проекта
cd /home/ilya/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

# 1. Обновляем код (жестко)
git fetch origin lab2
git reset --hard "$SHA"

# 2. Записываем хэш в файл конфигурации (чтобы сайт его показал боту)
# Мы используем sudo tee, так как ранее  настраивал права для него в visudo
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env

# 3. Убиваем старые процессы uvicorn
sudo pkill -9 -f "uvicorn" || true

# 4. ЗАПУСК через мой VENV (как в Лабе 1, но через nohup)
# ВАЖНО: используем полный путь
export DEPLOY_REF=$SHA
nohup /home/ilya/catty-reminders-app/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8181 </dev/null > deploy.log 2>&1 &

# 5. Даем 5 секунд и проверяем, открылся ли порт
sleep 5
if sudo ss -tulpn | grep -q ":8181"; then
    echo "SUCCESS: App is running on port 8181 with SHA $SHA"
else
    echo "ERROR: App failed to start. Check deploy.log"
    cat deploy.log
    exit 1
fi
