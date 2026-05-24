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

# Обновляем код
git fetch origin
git checkout -B $BRANCH origin/$BRANCH
git reset --hard origin/$BRANCH

# Получаем текущий SHA
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
    pip install --upgrade pip > /dev/null 2>&1 || true
    pip install -r requirements.txt > /dev/null 2>&1 || pip install -r requirements.txt
    
    # Устанавливаем Playwright браузер
    if pip list 2>/dev/null | grep -q playwright; then
        echo "=== Установка Playwright браузеров ==="
        playwright install chromium > /dev/null 2>&1 || true
    fi
fi

# Перезапускаем сервис
echo "=== Перезапуск сервиса ==="
sudo systemctl daemon-reload
sudo systemctl restart app.service

# Проверяем что сервис запустился
sleep 3
if sudo systemctl is-active --quiet app.service; then
    echo "✅ Сервис успешно запущен"
else
    echo "❌ Сервис не запустился"
    sudo systemctl status app.service --no-pager
    exit 1
fi

# Проверяем что приложение отвечает
sleep 2
MAX_RETRIES=10
for i in $(seq 1 $MAX_RETRIES); do
    if curl -s -f http://127.0.0.1:8181/login > /dev/null 2>&1; then
        echo "✅ Приложение отвечает на запросы"
        break
    fi
    echo "   Ожидаем запуск приложения... (попытка $i/$MAX_RETRIES)"
    sleep 2
    
    if [ $i -eq $MAX_RETRIES ]; then
        echo "❌ Приложение не отвечает после перезапуска"
        echo "=== Логи приложения ==="
        sudo journalctl -u app.service -n 30 --no-pager
        exit 1
    fi
done

echo "=== Деплой ветки $BRANCH завершен ==="
echo "✅ Деплой SHA: $CURRENT_SHA"
