#!/bin/bash
set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" ]]; then
    echo "CRITICAL: Missing required variables"
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

APP_DIR="/home/vboxuser/catty-reminders-app"

echo "Deploying to ${SERVER_HOST}..."

ssh -p "$TARGET_PORT" \
    -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" \
    "bash -s" << EOF

set -e

cd ${APP_DIR}

echo "--> Current env:"
echo "REPO_LOWER=${REPO_LOWER}"
echo "RELEASE_HASH=${RELEASE_HASH}"

export REPO_LOWER="${REPO_LOWER}"
export RELEASE_HASH="${RELEASE_HASH}"

echo "--> Stopping old containers"
docker-compose down || true

echo "--> Pulling latest image"
docker-compose pull

echo "--> Starting containers"
docker-compose up -d

echo "--> Cleanup"
docker image prune -af || true

echo "--> Deploy finished"
EOF
