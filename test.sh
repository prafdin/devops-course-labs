#!/bin/bash
echo "🧪 Запуск тестов..."
cd /home/ilya/catty-app
source venv/bin/activate

if command -v pytest &> /dev/null; then
    pytest
    if [ $? -eq 0 ]; then
        echo "✅ Тесты pytest пройдены"
        exit 0
    else
        echo "❌ Тесты pytest упали"
        exit 1
    fi
else
    echo "pytest не найден, проверяем синтаксис"
    python3 -m py_compile app/*.py 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Синтаксис корректен"
        exit 0
    else
        echo "❌ Ошибка синтаксиса"
        exit 1
    fi
fi
