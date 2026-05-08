#!/bin/bash
set -e

REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')
IMAGE="ghcr.io/${REPO_LOWER}:${RELEASE_HASH}"

echo "Deploying: $IMAGE"

ssh -p "$DEPLOY_PORT" \
  -o StrictHostKeyChecking=no \
  "$DEPLOY_USER@$DEPLOY_HOST" \
  "DOCKER_TOKEN='$DOCKER_TOKEN' GITHUB_ACTOR='$GITHUB_ACTOR' RELEASE_HASH='$RELEASE_HASH' IMAGE='$IMAGE' bash -s" << 'EOF'

set -e

echo "Login GHCR"
echo "$DOCKER_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

echo "Pull image"
docker pull "$IMAGE"

echo "Restart container"
docker stop catty-app || true
docker rm catty-app || true

docker run -d \
  --name catty-app \
  --restart unless-stopped \
  -p 8181:8181 \
  -e COMMIT_SHA="$RELEASE_HASH" \
  "$IMAGE"

echo "OK"
docker ps

EOF
