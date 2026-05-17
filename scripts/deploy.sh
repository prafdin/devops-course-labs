#!/bin/bash
set -e

TARGET_PORT="${SERVER_PORT:-22}"

echo "Deploying..."

ssh -p "$TARGET_PORT" \
  -o StrictHostKeyChecking=no \
  "${SERVER_USER}@${SERVER_HOST}" "export RELEASE_HASH='${RELEASE_HASH}' MYSQL_ROOT_PASSWORD='${MYSQL_ROOT_PASSWORD}' MYSQL_USER='${MYSQL_USER}' MYSQL_PASSWORD='${MYSQL_PASSWORD}' GHCR_USER='${GHCR_USER}' GHCR_TOKEN='${GHCR_TOKEN}'; bash -s" << 'EOF'

set -e

mkdir -p /home/vboxuser/catty-reminders-app
cd /home/vboxuser/catty-reminders-app

COMPOSE_FILE="docker-compose.yaml"
if [ ! -f "docker-compose.yaml" ] && [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
fi

cat > .env << EOL
RELEASE_HASH=$RELEASE_HASH
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
EOL

echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

docker-compose -f $COMPOSE_FILE --env-file .env down || true
docker-compose -f $COMPOSE_FILE --env-file .env pull
docker-compose -f $COMPOSE_FILE --env-file .env up -d --force-recreate

echo "Waiting for database initialization..."
sleep 10

docker-compose -f $COMPOSE_FILE --env-file .env up -d catty_backend

docker image prune -af || true
docker ps
EOF
