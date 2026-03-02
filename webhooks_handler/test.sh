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
echo "Текущая директория: $(pwd)"
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

echo "=== запуск приложения $BRANCH ==="
systemctl stop myapp
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8181 > /dev/null 2>&1 &
APP_PID=$!



export PYTHONPATH=/home/alex/3kurs/dev-ops/catty-reminders-app:$PYTHONPATH
echo "=== Выполняем тесты из папки tests ==="
pytest tests --maxfail=1 --disable-warnings -q

RESULT=$?
kill $APP_PID

exit $RESULT