#!/bin/bash
set -e

APP_DIR="/home/vboxuser/catty-reminders-app"
TARGET_PORT="${SERVER_PORT:-22}"

echo "Deploying..."

ssh -p "$TARGET_PORT" \
  -o StrictHostKeyChecking=no \
  "${SERVER_USER}@${SERVER_HOST}" << EOF
set -e
cd $APP_DIR

cat > .env << EOL
RELEASE_HASH=$RELEASE_HASH
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
EOL

echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
docker-compose --env-file .env down || true
docker-compose --env-file .env pull
docker-compose --env-file .env up -d --force-recreate
docker image prune -af || true
docker ps
EOF
