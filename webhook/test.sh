#!/bin/bash
set -e

BRANCH=$1
APP_DIR="/home/ubuntu/devops/catty-reminders-app"

if [ -z "$BRANCH" ]; then
    echo "❌ No branch specified"
    exit 1
fi

echo "=== Запуск тестов проекта ветки $BRANCH ==="

cd "$APP_DIR"

# Обновляем код до последнего коммита ветки
git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH" 2>/dev/null || git checkout "$BRANCH"
git pull origin "$BRANCH"

# Обновляем .env файл
DEPLOY_REF="$(git rev-parse HEAD)"
echo "DEPLOY_REF=$DEPLOY_REF" > "$APP_DIR/.env"
echo "Текущий SHA: $DEPLOY_REF"

# Активируем окружение
if [ ! -d "venv" ]; then
    echo "=== Создание виртуального окружения ==="
    python3 -m venv venv
fi

source venv/bin/activate

# Устанавливаем зависимости
if [ -f "requirements.txt" ]; then
    echo "=== Установка зависимостей ==="
    pip install -q -r requirements.txt
fi

# Устанавливаем Playwright браузер если нужно
if pip list | grep -q playwright; then
    echo "=== Устанавливаем Playwright браузер ==="
    playwright install chromium
fi

# Проверяем что сервис приложения работает
echo "=== Проверка работающего приложения ==="
if curl -s http://127.0.0.1:8181/ > /dev/null 2>&1; then
    echo "✅ Приложение доступно"
else
    echo "⚠️ Приложение не отвечает, проверяем статус сервиса..."
    sudo systemctl status app.service --no-pager
    echo "Пытаемся перезапустить сервис..."
    sudo systemctl restart app.service
    sleep 5
    if curl -s http://127.0.0.1:8181/ > /dev/null 2>&1; then
        echo "✅ Приложение восстановлено"
    else
        echo "❌ Приложение не доступно"
        exit 1
    fi
fi

# Запускаем тесты
echo "=== Выполняем тесты ==="
export PYTHONPATH=$APP_DIR:$PYTHONPATH
pytest tests --maxfail=1 --disable-warnings -q
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo "✅ Тесты прошли успешно"
else
    echo "❌ Тесты завершились с ошибкой"
fi

exit $RESULT
