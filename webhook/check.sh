#!/bin/bash

echo "===== ПРОВЕРКА СИСТЕМЫ (лабораторная работа №1) ====="
echo

# ===== Конфигурация =====
ID="miftyahov"
PROXY="course.prafdin.ru"
APP_DIR="/opt/catty-reminders"
WEBHOOK_LOG="/var/log/webhook/webhook.log"
DEPLOY_LOG="/var/log/webhook/deployments.log"

# ===== Проверка сервисов systemd =====
check_service() {
    if systemctl is-active --quiet "$1"; then
        echo "$1: работает"
    else
        echo "$1: НЕ работает"
    fi
}

check_service "frpc"
check_service "catty-reminders"
check_service "webhook-handler"

# ===== Проверка портов =====
echo
if ss -tlnp | grep -q ":8181"; then
    echo "Порт 8181 (приложение): слушается"
else
    echo "Порт 8181 (приложение): НЕ слушается"
fi

if ss -tlnp | grep -q ":8080"; then
    echo "Порт 8080 (webhook): слушается"
else
    echo "Порт 8080 (webhook): НЕ слушается"
fi

# ===== Локальный доступ к приложению =====
echo
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8181/login 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo "Приложение локально (http://localhost:8181/login): отвечает (200)"
elif [ -n "$HTTP_CODE" ]; then
    echo "Приложение локально: отвечает с кодом $HTTP_CODE"
else
    echo "Приложение локально: НЕ отвечает"
fi

# ===== Локальный доступ к webhook (имитация ping) =====
WEBHOOK_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "test"}' 2>/dev/null)

if [ "$WEBHOOK_CODE" = "200" ] || [ "$WEBHOOK_CODE" = "202" ]; then
    echo "Webhook локально (POST /): отвечает ($WEBHOOK_CODE)"
else
    echo "Webhook локально: НЕ отвечает (код $WEBHOOK_CODE)"
fi

# ===== Доступность внешних адресов через FRP =====
echo
APP_EXT=$(curl -s -o /dev/null -w "%{http_code}" -I "http://app.$ID.$PROXY" 2>/dev/null | head -1)
if [ -n "$APP_EXT" ]; then
    echo "http://app.$ID.$PROXY: доступен (код $APP_EXT)"
else
    echo "http://app.$ID.$PROXY: НЕ доступен"
fi

WEBHOOK_EXT=$(curl -s -o /dev/null -w "%{http_code}" -I "http://webhook.$ID.$PROXY" 2>/dev/null | head -1)
if [ -n "$WEBHOOK_EXT" ]; then
    echo "http://webhook.$ID.$PROXY: доступен (код $WEBHOOK_EXT)"
else
    echo "http://webhook.$ID.$PROXY: НЕ доступен"
fi

# ===== Проверка логов =====
echo
if [ -f "$WEBHOOK_LOG" ]; then
    echo "Лог webhook ($WEBHOOK_LOG): существует"
else
    echo "Лог webhook: НЕ найден"
fi

if [ -f "$DEPLOY_LOG" ]; then
    echo "Лог деплоев ($DEPLOY_LOG): существует"
else
    echo "Лог деплоев: НЕ найден"
fi

# ===== Последний коммит в репозитории =====
echo
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR" 2>/dev/null
    LAST_COMMIT=$(git log -1 --oneline 2>/dev/null)
    if [ -n "$LAST_COMMIT" ]; then
        echo "Последний коммит в приложении: $LAST_COMMIT"
    else
        echo "Не удалось получить коммит"
    fi
else
    echo "Папка приложения $APP_DIR не найдена или не является git-репозиторием"
fi

echo
echo "===== ПРОВЕРКА ЗАВЕРШЕНА ====="