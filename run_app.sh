#!/bin/bash

# 1. Используем переменные, чтобы не дублировать пути
APP_DIR="/home/ilya/catty-reminders-app"
VENV_PYTHON="$APP_DIR/venv/bin/python"
SERVICE_NAME="catty-app"

# Проверяем, передан ли SHA коммита
if [ -z "$1" ]; then
    echo "ERROR: No commit SHA provided"
    exit 1
fi

SHA=$1
echo "--- Starting Deployment of SHA: ${SHA:0:7} ---"

# 2. Безопасный переход в директорию
cd "$APP_DIR" || { echo "Directory $APP_DIR not found"; exit 1; }

# 3. Обновление исходного кода
echo "Fetching updates from origin..."
git fetch --all --quiet
git reset --hard "$SHA"

# 4. Обновление зависимостей через venv
echo "Installing dependencies..."
$VENV_PYTHON -m pip install -q -r requirements.txt

# 5. Сохранение метаданных деплоя
# Используем > /dev/null, чтобы не дублировать вывод в консоль
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env > /dev/null

# 6. Рестарт сервиса
echo "Restarting $SERVICE_NAME..."
sudo systemctl restart "$SERVICE_NAME"

# 7. Расширенная проверка
sleep 5
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "✅ SUCCESS: App is running (SHA: $SHA)"
else
    echo "❌ ERROR: $SERVICE_NAME failed to start. Check logs: journalctl -u $SERVICE_NAME"
    exit 1
fi
