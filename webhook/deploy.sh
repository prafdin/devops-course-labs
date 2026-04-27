#!/bin/bash
set -e

PROJECT_DIR="/home/vboxuser/devops-lab/catty-reminders-app"
TARGET_COMMIT=$1

if [ -z "$TARGET_COMMIT" ]; then
    echo "❌ No commit hash provided"
    exit 1
fi

echo "▶️ Starting deployment for $TARGET_COMMIT"

cd "$PROJECT_DIR"

git fetch --all
git reset --hard "$TARGET_COMMIT"

CURRENT_SHA=$(git rev-parse HEAD)
echo "DEPLOY_REF=$CURRENT_SHA" > "$PROJECT_DIR/.env"

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
fi

sudo chown vboxuser:vboxuser "$PROJECT_DIR/.env"
chmod 644 "$PROJECT_DIR/.env"

echo "🔄 Restarting service..."
sudo systemctl daemon-reload
sudo systemctl restart app.service

echo "✅ Deployment complete (SHA: $CURRENT_SHA)" 
