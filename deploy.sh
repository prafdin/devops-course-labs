#!/bin/bash
set -e

APP_DIR="/home/vboxuser/catty-reminders-app"

REF="$1"          # например, refs/heads/lab1
COMMIT_SHA="$2"   # SHA из payload (after)

cd "$APP_DIR"

git fetch origin

if [ -n "$REF" ]; then
    BRANCH="${REF#refs/heads/}"
    git checkout "$BRANCH"
else
    BRANCH="lab1"
    git checkout "$BRANCH"
fi

if [ -n "$COMMIT_SHA" ]; then
    git reset --hard "$COMMIT_SHA"
fi

# Обновляем DEPLOY_REF для сервиса
echo "DEPLOY_REF=$(git rev-parse HEAD)" | sudo tee /etc/catty.env > /dev/null

# Устанавливаем зависимости при необходимости
if [ -f requirements.txt ]; then
    python3 -m pip install --break-system-packages -r requirements.txt
fi

# Запускаем тесты, если есть
if [ -d tests ]; then
    python3 -m unittest discover tests
fi

sudo systemctl daemon-reload
sudo systemctl restart catty.service
