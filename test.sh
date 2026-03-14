#!/bin/bash
echo "🧪 Запуск тестов..."
# Если есть pytest — запускаем его, иначе проверяем синтаксис
if command -v pytest &> /dev/null; then
    pytest
    if [ $? -eq 0 ]; then
        echo "✅ Тесты pytest пройдены"
    else
        echo "❌ Тесты pytest упали"
        exit 1
    fi
else
    echo "pytest не найден, проверяем синтаксис"
    if python3 -m py_compile app/*.py 2>/dev/null; then
        echo "✅ Синтаксис корректен"
    else
        echo "❌ Ошибка синтаксиса"
        exit 1
    fi
fi
exit 0