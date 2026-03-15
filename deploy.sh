#!/bin/bash

set -e  # Выход при любой ошибке

echo "🚀 Деплой начат: $(date)" >> /tmp/deploy.log

# Перезапускаем приложение
sudo systemctl restart devops-app.service

sleep 2

# Проверяем, что приложение отвечает
if curl -s http://localhost:8181 > /dev/null; then
    echo "✅ Деплой завершён успешно: $(date)" >> /tmp/deploy.log
else
    echo "❌ Приложение не отвечает после деплоя!" >> /tmp/deploy.log
    exit 1
fi
