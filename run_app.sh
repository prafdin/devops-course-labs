#!/bin/bash
# 1. Заходим в папку проекта
cd /home/ilya/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

# 2. Принудительно обновляем код
git fetch --all
git reset --hard "$SHA"

# 3. Обновляем зависимости venv
/home/ilya/catty-reminders-app/venv/bin/python -m pip install -r requirements.txt

# 4. Пишем хэш для страницы сайта
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env

# 5. Перезапускаем сервис catty-app через systemd
sudo systemctl restart catty-app

# 6. Проверка статуса
sleep 3
if systemctl is-active --quiet catty-app; then
    echo "SUCCESS: SHA $SHA is live on catty-app"
else
    echo "ERROR: catty-app service failed to start"
    exit 1
fi
