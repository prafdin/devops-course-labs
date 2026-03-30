#!/bin/bash

set -e

echo "========================================="
echo "ЗАПУСК ТЕСТОВ"
echo "========================================="

#Активируем виртуальное окружение
source /home/mb/catty-reminders-app/venv/bin/activate

if [ ! -f "inputs.json" ]; then
    cat > inputs.json <<EOF
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

echo "========================================="
echo "Запуск pytest тестов..."
echo "========================================="

python3 -m pytest

PYTEST_EXIT_CODE=$?

echo "========================================="
if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    echo "ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!"
else
    echo "НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ (код: $PYTEST_EXIT_CODE)"
fi
echo "========================================="

deactivate

exit $PYTEST_EXIT_CODE