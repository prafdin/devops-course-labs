#!/bin/bash
set -e
APP_DIR="/home/alex/3kurs/dev-ops/catty-reminders-app"
VENV="$APP_DIR/venv"

echo "=== Запуск тестов проекта ==="

cd "$APP_DIR"

if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        echo "=== создание виртуального окружения $BRANCH ==="
        python -m venv venv
    fi
    echo "=== запуск виртуального окружения $BRANCH ==="
    source venv/bin/activate
    echo "=== установка зависимостей $BRANCH ==="
    pip install -r requirements.txt
fi

if [ -f "requirements.txt" ]; then
    echo "=== Установка зависимостей ==="
    pip install -r requirements.txt
fi

cd /home/alex/3kurs/dev-ops/catty-reminders-app

echo "=== Выполняем тесты из папки tests ==="
pytest tests --maxfail=1 --disable-warnings -q

RESULT=$?

exit $RESULT