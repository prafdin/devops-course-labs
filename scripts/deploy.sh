#!/bin/bash
set -e

: "${DEPLOY_HOST:?DEPLOY_HOST required}"
: "${DEPLOY_USER:?DEPLOY_USER required}"
: "${DEPLOY_PORT:?DEPLOY_PORT required}"
: "${RELEASE_HASH:?RELEASE_HASH required}"
: "${IMAGE:?IMAGE required}"

CONTAINER_NAME="catty-app"
HOST_PORT=3155
CONTAINER_PORT=8181

echo "Deploying: $IMAGE"

ssh -p "$DEPLOY_PORT" -o StrictHostKeyChecking=no "$DEPLOY_USER@$DEPLOY_HOST" << EOF
set -e

echo "Logging into GHCR..."
echo "$DOCKER_TOKEN" | sudo docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

echo "Pulling image..."
sudo docker pull $IMAGE

echo "Stopping old container..."
sudo docker stop $CONTAINER_NAME || true
sudo docker rm $CONTAINER_NAME || true

echo "Starting new container..."
sudo docker run -d \
  -p $HOST_PORT:$CONTAINER_PORT \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  -e DEPLOY_REF=$RELEASE_HASH \
  $IMAGE

sleep 3

sudo docker ps | grep -q $CONTAINER_NAME && echo "OK deployed"
EOF
