#!/bin/bash
echo "🧪 Запускаем тесты для catty-reminders-app..."

# Проверяем, что приложение отвечает на порту 8181
curl -f http://localhost:8181 > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Приложение доступно на порту 8181"
else
    echo "❌ Приложение не отвечает на порту 8181"
    exit 1
fi

echo "🎉 Все тесты пройдены!"
