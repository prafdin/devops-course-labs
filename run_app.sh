#!/bin/bash
cd /home/vboxuser/lab2/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

git fetch --all
git reset --hard "$SHA"

if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
fi

./venv/bin/python -m pip install -r requirements.txt

# Обновляем DEPLOY_REF в файле
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env

# Перезапускаем приложение
sudo systemctl restart catty-app

# Перезагружаем Nginx, чтобы подхватил новую переменную
sudo systemctl reload nginx

sleep 3
if systemctl is-active --quiet catty-app; then
    echo "SUCCESS: Deployed $SHA"
else
    echo "ERROR: App failed"
    exit 1
fi
