#!/bin/bash
set -e

APP_PATH="/home/qzm/Desktop/catty-reminders-app"
cd $APP_PATH

export REPO_LOWER="kuzminstanislav/catty-reminders-app"
export RELEASE_HASH=$(git rev-parse HEAD)

echo "REPO_LOWER=${REPO_LOWER}" > .env
echo "RELEASE_HASH=${RELEASE_HASH}" >> .env

docker compose pull
docker compose up -d --remove-orphans --pull always
