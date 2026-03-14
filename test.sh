#!/bin/bash
echo "🧪 Запуск тестов..."
# Проверка синтаксиса всех .py файлов в папке app
if python3 -m py_compile app/*.py 2>/dev/null; then
    echo "✅ Синтаксис корректен"
    exit 0
else
    echo "❌ Ошибка синтаксиса"
    exit 1
fi
