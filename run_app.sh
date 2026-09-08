#!/bin/bash
set -euo pipefail

cd /opt/catty-reminders-app

SHA="${1:?SHA is required}"

echo "Deploying SHA: $SHA"

git fetch --all --tags
git reset --hard "$SHA"

source .venv/bin/activate
pip install -r requirements.txt

printf 'DEPLOY_REF=%s\n' "$SHA" | sudo tee /opt/catty-reminders-app/.env > /dev/null

sudo systemctl restart catty-app

sleep 3

if systemctl is-active --quiet catty-app; then
    echo "SUCCESS: Deployed $SHA"
else
    echo "ERROR: App failed"
    exit 1
fi
