#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/ct/catty-reminders-app"
ENV_FILE="$APP_DIR/.env.deploy"

echo "🚀 Deploying Catty..."

cd "$APP_DIR"

if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/pip install -r requirements.txt

DEPLOY_REF="$(git rev-parse HEAD)"
printf 'DEPLOY_REF=%s\n' "$DEPLOY_REF" > "$ENV_FILE"

echo "Using DEPLOY_REF=$DEPLOY_REF"

echo "🔄 Restarting app.service..."
systemctl --user restart app.service
sleep 3

if systemctl --user is-active app.service; then
    echo "✅ Service restarted successfully"
else
    echo "❌ Service failed to restart!"
    exit 1
fi

echo "✅ Catty deployed successfully"
