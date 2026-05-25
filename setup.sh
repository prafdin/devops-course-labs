#!/bin/zsh
set -e

PROJECT_DIR="/home/light/catty-reminders-app"
CURRENT_USER="light"

PROXY="course.prafdin.ru"
TOKEN="devops"
ID="volyanyuk"

echo "========================================"
echo "Пользователь: $CURRENT_USER"
echo "Директория: $PROJECT_DIR"
echo "========================================"

echo "1. Делаем скрипты исполняемыми..."
chmod +x "$PROJECT_DIR/deploy.sh"
chmod +x "$PROJECT_DIR/test.sh"
chmod +x "$PROJECT_DIR/webhook_server.py"

echo "2. Настраиваем FRP (проброс доменов)..."
sudo tee /etc/frp/frpc.toml > /dev/null <<EOF
serverAddr = "$PROXY"
serverPort = 7000

auth.method = "token"
auth.token = "$TOKEN"

[[proxies]]
name = "hook-$ID"
type = "http"
localPort = 8080
customDomains = ["webhook.$ID.$PROXY"]

[[proxies]]
name = "app-$ID"
type = "http"
localPort = 8181
customDomains =["app.$ID.$PROXY"]
EOF

sudo systemctl restart frpc
sudo systemctl enable frpc

echo "3. Создаем системную службу для Вебхука (webhook-server)..."
sudo tee /etc/systemd/system/webhook-server.service > /dev/null <<EOF
[Unit]
Description=GitHub Webhook Server
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "4. Создаем системную службу для Приложения (catty-app)..."
sudo tee /etc/systemd/system/catty-app.service > /dev/null <<EOF
[Unit]
Description=Catty Reminders FastAPI App
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8181
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "5. Перезагружаем конфигурацию и запускаем службы..."
sudo systemctl daemon-reload

sudo systemctl stop webhook-server catty-app 2>/dev/null || true
sudo systemctl enable webhook-server
sudo systemctl start webhook-server
sudo systemctl enable catty-app
sudo systemctl start catty-app

echo "========================================"
echo "Установка завершена успешно!"
echo "Адрес вебхука: http://webhook.$ID.$PROXY/"
echo "Адрес приложения: http://app.$ID.$PROXY/"
echo "========================================"
