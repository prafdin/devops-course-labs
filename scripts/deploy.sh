#!/bin/bash
set -e

echo "REPO=$REPO"
echo "RELEASE_HASH=$RELEASE_HASH"

REPO_LOWER=$(echo "$REPO" | tr '[:upper:]' '[:lower:]')
IMAGE="ghcr.io/${REPO_LOWER}:${RELEASE_HASH}"

echo "Deploying: $IMAGE"

ssh -p "${DEPLOY_PORT}" \
  -o StrictHostKeyChecking=no \
  "${DEPLOY_USER}@${DEPLOY_HOST}" \
  "IMAGE='$IMAGE' RELEASE_HASH='$RELEASE_HASH' GH_USER='$GH_USER' GH_TOKEN='$GH_TOKEN' bash -s" << 'EOF'

set -e

echo "Login GHCR"
echo "$GH_TOKEN" | docker login ghcr.io -u "$GH_USER" --password-stdin

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
