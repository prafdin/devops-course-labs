#!/bin/bash
set -e

DEPLOY_REF=$1
APP_DIR="/home/dmitri/app"

echo "=== DEPLOY релиза ==="
echo "Target SHA: $DEPLOY_REF"

# Переходим в директорию приложения
cd "$APP_DIR" || exit 1

# Обновляем код из репозитория
echo "Fetching updates..."
git fetch --all --tags
git reset --hard "$DEPLOY_REF"

# Обновляем зависимости
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Сохраняем версию для отображения в приложении
echo "Saving DEPLOY_REF..."
echo "DEPLOY_REF=$DEPLOY_REF" | sudo tee /etc/app-deploy-env

# Перезапускаем приложение
echo "Restarting application..."
sudo systemctl daemon-reload
sudo systemctl restart app

# Проверка статуса
sleep 3
if systemctl is-active --quiet app; then
    echo "✅ SUCCESS: Deployed $DEPLOY_REF"
else
    echo "❌ ERROR: Application failed to start"
    exit 1
fi
