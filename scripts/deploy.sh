#!/bin/bash
set -e

CONTAINER_NAME="catty-app"
PORT=8181

if [ -z "$DEPLOY_HOST" ] || [ -z "$DEPLOY_USER" ]; then
  echo "DEPLOY_HOST / DEPLOY_USER missing"
  exit 1
fi

if [ -z "$RELEASE_HASH" ]; then
  echo "RELEASE_HASH missing"
  exit 1
fi

IMAGE="${IMAGE_NAME}:${RELEASE_HASH}"

echo "Deploying: $IMAGE"

ssh -p "$DEPLOY_PORT" "$DEPLOY_USER@$DEPLOY_HOST" << EOF
set -e

echo "Logging into GHCR..."
echo "$DOCKER_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

echo "Pulling image..."
docker pull $IMAGE

echo "Restarting container..."
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

docker run -d \
  -p 3155:8181 \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  -e DEPLOY_REF=$RELEASE_HASH \
  $IMAGE

echo "Deployed OK"
EOF
