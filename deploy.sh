#!/bin/bash
# Берем тег из аргумента или ставим lab4 по умолчанию
TAG=${1:-lab4}
export IMAGE_TAG=$TAG

echo "🚀 Деплой мультиконтейнерного стека (Tag: $TAG)..."

# Останавливаем старое и запускаем новое в фоне
docker compose down
docker compose pull app
docker compose up -d

echo "✅ Стек запущен и доступен на порту 8182!"
