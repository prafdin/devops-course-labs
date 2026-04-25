#!/bin/bash
set -euo pipefail

GIT_REF="${1:-lab2}"
APP_DIR="$HOME/catty-reminders-app"

echo "==> Deploying ref: $GIT_REF"
cd "$APP_DIR"

echo "==> Fetching latest"
git fetch --all --prune
git fetch --tags --force

echo "==> Resolving $GIT_REF"
if git show-ref --verify --quiet "refs/remotes/origin/$GIT_REF"; then
  TARGET="origin/$GIT_REF"
else
  TARGET="$GIT_REF"
fi
echo "==> Target: $TARGET"

echo "==> Checking out"
git checkout -f "$TARGET"

echo "==> Installing dependencies (venv)"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "==> Restarting service"
sudo systemctl restart catty-app

echo "==> Waiting for app to come up"
for i in $(seq 1 20); do
  if curl -fsS http://127.0.0.1:8181/login > /dev/null; then
    echo "==> Deploy successful"
    exit 0
  fi
  sleep 1
done

echo "==> App did not respond after restart"
sudo systemctl status catty-app --no-pager
exit 1
