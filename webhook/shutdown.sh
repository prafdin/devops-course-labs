#!/bin/bash

echo "========================================="
echo "🛑 ОСТАНОВКА ВСЕХ СЕРВИСОВ ЛАБОРАТОРНОЙ РАБОТЫ"
echo "========================================="
echo

# ===== Конфигурация =====
ID="miftyahov"
PROXY="course.prafdin.ru"
APP_DIR="/opt/catty-reminders"
WEBHOOK_LOG="/var/log/webhook/webhook.log"
APP_LOG_SERVICE="catty-reminders"

# 1. Остановка webhook-обработчика
echo "[1] Остановка webhook-handler..."
sudo systemctl stop webhook-handler
sudo systemctl status webhook-handler --no-pager | head -3
echo

# 2. Остановка приложения
echo "[2] Остановка catty-reminders..."
sudo systemctl stop catty-reminders
sudo systemctl status catty-reminders --no-pager | head -3
echo

# 3. Остановка FRP
echo "[3] Остановка frpc..."
sudo systemctl stop frpc
sudo systemctl status frpc --no-pager | head -3
echo

# 4. Проверка портов (должны быть свободны)
echo "[4] Проверка освобождения портов:"
sudo ss -tlnp | grep -E "8080|8181" || echo "   ✅ Порты 8080 и 8181 свободны"
echo

# 5. Финальный статус всех сервисов
echo "[5] Статус всех сервисов после остановки:"
sudo systemctl status frpc catty-reminders webhook-handler --no-pager | grep "Active:" | sed 's/^/   /'
echo

# 6. Проверка логов (последние записи перед остановкой)
echo "[6] Последние записи в логах перед остановкой:"
echo "   Лог webhook (последние 5 строк):"
tail -5 "$WEBHOOK_LOG" 2>/dev/null | sed 's/^/      /' || echo "      Лог не найден"
echo
echo "   Лог приложения (последние 5 строк):"
sudo journalctl -u "$APP_LOG_SERVICE" -n 5 --no-pager 2>/dev/null | sed 's/^/      /' || echo "      Нет записей"

echo
echo "========================================="
echo "✅ ВСЕ СЕРВИСЫ ОСТАНОВЛЕНЫ"
echo "========================================="
echo "🖥️  Теперь можно безопасно выключить виртуальную машину командой:"
echo "   sudo shutdown now"
echo "========================================="