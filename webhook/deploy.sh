#!/bin/bash
set -e

BRANCH=$1
APP_DIR="/home/ubuntu/devops/catty-reminders-app"

if [ -z "$BRANCH" ]; then
    echo "❌ No branch specified"
    exit 1
fi

echo "=== DEPLOY ветки $BRANCH ==="

cd $APP_DIR

# Обновляем код до последнего коммита ветки
git fetch origin
git checkout -B $BRANCH origin/$BRANCH
git reset --hard origin/$BRANCH

# Получаем текущий SHA для деплоя
CURRENT_SHA=$(git rev-parse HEAD)
echo "DEPLOY_REF=$CURRENT_SHA" > "$APP_DIR/.env"
echo "DEPLOY_TIME=$(date -Iseconds)" >> "$APP_DIR/.env"
echo "Текущий SHA: $CURRENT_SHA"

# Обновляем зависимости
if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        echo "=== Создание виртуального окружения ==="
        python3 -m venv venv
    fi
    source venv/bin/activate
    echo "=== Установка зависимостей ==="
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Устанавливаем Playwright браузер если нужно
    if pip list | grep -q playwright; then
        echo "=== Установка Playwright браузеров ==="
        playwright install chromium
    fi
fi

# Исправляем права на .env файл
sudo chown ubuntu:ubuntu "$APP_DIR/.env" 2>/dev/null || true
chmod 644 "$APP_DIR/.env" 2>/dev/null || true

# Перезапускаем через systemd
echo "=== Перезапуск сервиса ==="
sudo systemctl daemon-reload
sudo systemctl restart app.service

# Проверяем что сервис успешно запустился
sleep 3
if sudo systemctl is-active --quiet app.service; then
    echo "✅ Сервис успешно запущен"
    echo "=== Статус сервиса ==="
    sudo systemctl status app.service --no-pager --lines 0
else
    echo "❌ Сервис не запустился"
    sudo systemctl status app.service --no-pager
    echo "=== Логи сервиса ==="
    sudo journalctl -u app.service -n 30 --no-pager
    exit 1
fi

# Дополнительная проверка что приложение отвечает
sleep 2
if curl -s http://127.0.0.1:8181/ > /dev/null 2>&1; then
    echo "✅ Приложение отвечает на запросы"
else
    echo "⚠️ Сервис запущен, но приложение не отвечает"
    echo "=== Логи приложения ==="
    sudo journalctl -u app.service -n 20 --no-pager
fi

echo "=== Деплой ветки $BRANCH завершен ==="
echo "✅ Деплой SHA: $CURRENT_SHA"
