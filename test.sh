#!/bin/bash

echo "Запуск тестов приложения catty-reminders-app..."
echo "================================================"

VENV_PATH="/home/deemeed/catty-reminders-app/venv"
source "$VENV_PATH/bin/activate"

if [ ! -f "inputs.json" ]; then
    echo "Создание конфигурации тестов..."
    cat > inputs.json << EOF
{
    "base_url": "http://127.0.0.1:8181",
    "users": [
        {
            "username": "heisenberg",
            "password": "P@ssw0rd"
        },
        {
            "username": "tester",
            "password": "foobar123"
        }
    ]
}
EOF
fi

echo "Запуск pytest..."
python3 -m pytest

TEST_RESULT=$?

deactivate

if [ $TEST_RESULT -eq 0 ]; then
    echo "Все тесты пройдены успешно!"
    exit 0
else
    echo "Тесты не пройдены! Деплой будет отменен."
    exit 1
fi