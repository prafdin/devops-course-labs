#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/kirill/desktop/devops"
ENV_FILE="$APP_DIR/.env.deploy"

DEPLOY_COMMIT="${1:-}"

echo "🚀 Deploying Catty..."

cd "$APP_DIR"

git fetch origin

if [ -n "$DEPLOY_COMMIT" ]; then
  echo "🎯 Deploying specific commit: $DEPLOY_COMMIT"
  git checkout "$DEPLOY_COMMIT"
else
  echo "🎯 Deploying latest from lab2"
  git checkout lab2
  git pull origin lab2
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

.venv/bin/pip install -r requirements.txt

DEPLOY_REF="$(git rev-parse HEAD)"
printf 'DEPLOY_REF=%s\n' "$DEPLOY_REF" > "$ENV_FILE"

echo "Using DEPLOY_REF=$DEPLOY_REF"

echo "🔄 Restarting catty-app.service..."
sudo systemctl restart catty-app.service
sleep 3

if sudo systemctl is-active catty-app.service; then
    echo "✅ Service restarted successfully"
else
    echo "❌ Service failed to restart!"
    exit 1
fi

echo "✅ Catty deployed successfully"
