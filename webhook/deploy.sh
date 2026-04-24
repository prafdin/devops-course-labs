#!/bin/bash
set -e

BRANCH=$1
REPO_URL="https://github.com/mzpdqk/catty-reminders-app"
APP_DIR="/home/ubuntu/devops/catty-reminders-app"

echo "=== DEPLOY ветки $BRANCH ==="

if [ ! -d "$APP_DIR/.git" ]; then
    echo "Первый запуск — клонирование"
    git clone $REPO_URL $APP_DIR
fi

cd $APP_DIR

git fetch origin

# Проверяем существует ли ветка
if git show-ref --verify --quiet refs/heads/$BRANCH; then
    git checkout -B $BRANCH origin/$BRANCH
else
    git checkout -b $BRANCH origin/$BRANCH
fi

git reset --hard origin/$BRANCH

DEPLOY_REF="$(git rev-parse HEAD)"

echo "Текущий SHA ветки $BRANCH: $DEPLOY_REF"
echo "DEPLOY_REF=$DEPLOY_REF" > /home/ubuntu/devops/catty-reminders-app/.env

# Обновляем зависимости
if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        echo "=== создание виртуального окружения $BRANCH ==="
        python3 -m venv venv
    fi
    echo "=== активация виртуального окружения $BRANCH ==="
    source venv/bin/activate
    echo "=== установка зависимостей $BRANCH ==="
    pip install -r requirements.txt
fi

# Перезапускаем сервис (если используете systemd)
# Если нет systemd сервиса, просто перезапускаем процесс
echo "=== перезапуск приложения $BRANCH ==="
if systemctl list-units --full -all | grep -q "app.service"; then
    sudo systemctl restart app.service
else
    # Или просто перезапускаем процесс
    pkill -f "uvicorn app.main:app" || true
    source venv/bin/activate
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8081 > /tmp/app_prod.log 2>&1 &
fi

echo "=== Деплой завершен ==="
