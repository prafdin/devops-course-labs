#!/bin/bash

set -e

REPO_DIR="/home/ct/catty-reminders-app"
BRANCH=$1

cd "$REPO_DIR"

git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git pull origin "$BRANCH"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv/
fi

source .venv/bin/activate

pip install -r requirements.txt

python3 -m pytest -v
