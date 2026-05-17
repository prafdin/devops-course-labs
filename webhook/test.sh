#!/bin/bash
set -e
REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
BRANCH=$1

cd "$REPO_DIR"
git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git pull origin "$BRANCH"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv/
fi

source .venv/bin/activate
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
fi

echo "[TEST] Запуск pytest..."
python3 -m pytest -v

sudo tee /etc/systemd/system/devops-webhook.service > /dev/null <<EOF
[Unit]
Description=GitHub Webhook Listener
After=network.target

[Service]
User=kuzmin
WorkingDirectory=/home/qzm/Desktop/catty-reminders-app/webhook
Environment="GITHUB_TOKEN=devops"
ExecStart=/usr/bin/python3 /home/qzm/Desktop/catty-reminders-app/webhook/webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF