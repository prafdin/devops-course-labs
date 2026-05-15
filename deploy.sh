#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/enjoyer/my-app"
ENV_FILE="$APP_DIR/.env"
DEPLOY_COMMIT="${1:-}"

echo "🚀 Deploying Catty..."
cd "$APP_DIR"
git fetch origin

if [ -n "$DEPLOY_COMMIT" ]; then
  echo "🎯 Deploying specific commit: $DEPLOY_COMMIT"
  git checkout -qf "$DEPLOY_COMMIT"
else
  echo "🎯 Deploying latest from lab2"
  git checkout lab2
  git pull origin lab2
fi

source venv/bin/activate
pip install -r requirements.txt

DEPLOY_REF="$(git rev-parse HEAD)"
echo "DEPLOY_REF=$DEPLOY_REF" > "$ENV_FILE"

echo "🔄 Restarting catty-app..."
sudo systemctl restart catty-app

echo "⏳ Waiting for service to become active..."
for i in {1..15}; do
  if sudo systemctl is-active --quiet catty-app; then
    echo "✅ Service restarted successfully"
    exit 0
  fi
  sleep 1
done

echo "❌ Service failed to become active after 15 seconds!"
exit 1
