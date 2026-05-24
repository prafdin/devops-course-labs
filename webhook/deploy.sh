#!/bin/bash
set -e

TARGET_COMMIT=$1
APP_DIR="/home/ubuntu/devops/catty-reminders-app"

if [ -z "$TARGET_COMMIT" ]; then
    echo "❌ No commit hash provided"
    exit 1
fi

echo "=== DEPLOY по коммиту: $TARGET_COMMIT ==="

cd "$APP_DIR"

git fetch --all
git reset --hard "$TARGET_COMMIT"

CURRENT_SHA=$(git rev-parse HEAD)
echo "DEPLOY_REF=$CURRENT_SHA" > "$APP_DIR/.env"

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
fi

sudo chown ubuntu:ubuntu "$APP_DIR/.env"
chmod 644 "$APP_DIR/.env"

echo "🔄 Restarting service..."
sudo systemctl restart app.service

echo "✅ Deployment complete (SHA: $CURRENT_SHA)"
