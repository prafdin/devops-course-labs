#!/bin/bash
set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" ]]; then
    echo "Missing required variables"
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

APP_DIR="/home/vboxuser/catty-reminders-app"

echo "Deploying to ${SERVER_HOST}"

ssh -p "$TARGET_PORT" \
    -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" \
<< EOF

set -e

cd ${APP_DIR}

export REPO_LOWER="${REPO_LOWER}"
export RELEASE_HASH="${RELEASE_HASH}"

echo "REPO_LOWER=\$REPO_LOWER"
echo "RELEASE_HASH=\$RELEASE_HASH"

docker-compose down || true

docker-compose pull

docker-compose up -d --force-recreate

docker image prune -af || true

docker ps
EOF
