#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/kirill/desktop/devops"
cd "$APP_DIR"

echo "🚀 Deploying Catty..."

pip3 install -r requirements.txt

sudo systemctl restart catty-app.service

echo "✅ Catty deployed successfully"
