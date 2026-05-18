#!/bin/bash
set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" ]]; then
    echo "CRITICAL: Missing required variables."
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

echo "Deploying via Docker Compose..."
echo "Release hash: $RELEASE_HASH"
echo "Repository: $REPO_LOWER"

scp -P "$TARGET_PORT" \
    -o StrictHostKeyChecking=no \
    docker-compose.yaml \
    "${SERVER_USER}@${SERVER_HOST}:/home/vboxuser/catty-reminders-app/docker-compose.yaml"

ssh -p "$TARGET_PORT" \
    -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" "bash -s" << EOF

set -e

export RELEASE_HASH="$RELEASE_HASH"

APP_DIR="/home/vboxuser/catty-reminders-app"

echo "--> Creating application directory if needed"
mkdir -p \$APP_DIR

echo "--> Entering app directory"
cd \$APP_DIR

echo "--> Logging into GHCR"
echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GITHUB_ACTOR}" --password-stdin

echo "--> Pulling exact release image"
docker pull ghcr.io/${REPO_LOWER}:${RELEASE_HASH}

echo "--> Stopping old containers"
docker-compose down || true

echo "--> Pulling compose images"
docker-compose pull

echo "--> Starting database"
docker-compose up -d db

echo "--> Waiting for MariaDB readiness"

until docker exec catty_db mariadb-admin ping \
    -h localhost \
    -uroot \
    -proot --silent; do
    echo "MariaDB is unavailable - sleeping"
    sleep 3
done

echo "--> Database is ready"

echo "--> Starting backend"
docker-compose up -d catty_backend

echo "--> Waiting backend startup"
sleep 10

echo "--> Backend health check"
curl http://localhost:8181/login

echo "--> Running containers:"
docker ps

echo "--> Backend logs:"
docker logs catty_backend --tail 50

echo "--> Cleaning unused images"
docker image prune -af || true

echo "--> Deployment finished successfully"

EOF
