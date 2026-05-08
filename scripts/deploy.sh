#!/bin/bash
set -e

PORT=${DEPLOY_PORT:-22}
CONTAINER_NAME="catty-app"

echo "Deploying image: $IMAGE"

ssh -p "$PORT" -o StrictHostKeyChecking=no "$DEPLOY_USER@$DEPLOY_HOST" << EOF
set -e

echo "Login GHCR"
echo "$DOCKER_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

echo "Pulling $IMAGE"
docker pull $IMAGE

echo "Stopping container"
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

echo "Starting container"
docker run -d \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  -p 8181:8181 \
  -e RELEASE_HASH=$RELEASE_HASH \
  $IMAGE

echo "OK"
docker ps
EOF
