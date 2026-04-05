#!/bin/bash
# 1. Заходим в папку проекта
cd /home/ilya/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

# 2. Обновляем код из GitHub
git fetch --all
git reset --hard "$SHA"

# 3. Обновляем зависимости
/home/ilya/catty-reminders-app/venv/bin/python -m pip install -r requirements.txt

# 4. Сохраняем DEPLOY_REF для отображения на сайте
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env

# 5. Перезапускаем само приложение
sudo systemctl restart catty-app

# 6. Проверка
sleep 3
if systemctl is-active --quiet catty-app; then
    echo "SUCCESS: Deployed $SHA"
else
    echo "ERROR: App failed"
    exit 1
fi

