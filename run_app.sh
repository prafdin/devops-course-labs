#!/bin/bash
# 1. Заходим в папку
cd /home/password-123/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

# 2. код из GitHub
git fetch --all
git reset --hard "$SHA"

# 3. зависимости
/home/password-123/catty-reminders-app/venv/bin/python -m pip install -r requirements.txt

# 4. Сохраняем DEPLOY_REF
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-env

# 5. Перезапускаем
sudo systemctl restart catty

# 6. Проверка
sleep 3
if systemctl is-active --quiet catty
    echo "SUCCESS: Deployed $SHA"
else
    echo "ERROR"
    exit 1
fi
