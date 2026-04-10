#!/bin/bash
# Берем тег из первого аргумента, если его нет — ставим lab4
TAG=${1:-lab4}

echo "🚀 Начинаем деплой. Тег образа: $TAG"

# Экспортируем переменную, чтобы docker-compose её увидел
export IMAGE_TAG=$TAG

# Останавливаем старое и запускаем новое
docker compose down
docker compose pull app
docker compose up -d

echo "✅ Стек успешно запущен на порту 8182!"
