#!/bin/bash

set -e
echo "Current directory is $(pwd)"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

COMMIT_HASH="$1"

if [ -z "$COMMIT_HASH" ]; then
    echo "ERROR: Commit hash is not provided!"
    exit 1
fi

echo "=== Starting deployment for commit $COMMIT_HASH at $(date) ==="

echo "1. Pulling latest code..."
git fetch origin
git checkout "$COMMIT_HASH"

echo "2. Setting up dependencies..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Installing Playwright browsers..."
python3 -m playwright install chromium

echo "3. Running tests..."
if ! python3 -m pytest tests/; then
    echo "ERROR: Tests failed! Performing rollback to the previous version..."
    git checkout -
    echo "Restarting main application service to apply rollback..."
    sudo /bin/systemctl restart app.service
    exit 1
fi

echo "Tests passed successfully!"

echo "4. Updating DEPLOY_REF..."
echo "DEPLOY_REF=$COMMIT_HASH" > .env

echo "5. Restarting main application service..."
sudo /bin/systemctl restart app.service

echo "=== Deployment finished successfully ==="