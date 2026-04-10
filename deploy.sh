#!/bin/bash
set -e

DEPLOY_REF=$1
REPO_URL="git@github.com:Rovver52/catty-reminders-app"
APP_DIR="/home/${USER}/catty-reminders-app"

echo "=== DEPLOY ==="
echo "Commit SHA: $DEPLOY_REF"

if [ ! -d "$APP_DIR/.git" ]; then
    echo "First deploy - cloning repository"
    mkdir -p "$APP_DIR"
    git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

echo "Fetching updates..."
git fetch --all --tags

echo "Checking out commit: $DEPLOY_REF"
git checkout --detach "$DEPLOY_REF"

echo "DEPLOY_REF=$DEPLOY_…! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo "Restarting myapp service..."
sudo systemctl restart catty

sleep 3
if sudo systemctl is-active --quiet catty; then
    echo "Deploy successful!"
else
    echo "Error: myapp service failed to start"
    sudo systemctl status catty --no-pager
    exit 1
fi
