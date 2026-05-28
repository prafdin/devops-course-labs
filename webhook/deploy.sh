#!/bin/bash

echo "🚀 Начинаем развертывание демо-сайта..."

# Проверяем, установлен ли nginx
if ! command -v nginx &> /dev/null; then
    echo "❌ nginx не установлен."
    exit 1
fi

# Создаем директорию для сайта
sudo mkdir -p /var/www/demo

# Копируем файлы
echo "📁 Копируем файлы сайта..."
sudo cp webhook/index.html /var/www/demo/

# Копируем конфигурацию nginx
echo "⚙️  Применяем конфигурацию nginx..."
sudo cp webhook/nginx.conf /etc/nginx/sites-available/demo-site
sudo ln -sf /etc/nginx/sites-available/demo-site /etc/nginx/sites-enabled/

# Проверяем конфигурацию
echo "🔍 Проверяем конфигурацию nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    # Перезапускаем nginx
    echo "🔄 Перезапускаем nginx..."
    sudo systemctl reload nginx
    
    echo "✅ Развертывание завершено успешно!"
else
    echo "❌ Ошибка в конфигурации nginx"
    exit 1
fi