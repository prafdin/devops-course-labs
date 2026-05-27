#!/bin/bash
set -e

: "${DEPLOY_HOST:?DEPLOY_HOST not set}"
: "${DEPLOY_USER:?DEPLOY_USER not set}"
: "${RELEASE_HASH:?RELEASE_HASH not set}"
: "${IMAGE_NAME:?IMAGE_NAME not set}"
: "${DOCKER_TOKEN:?DOCKER_TOKEN not set}"
: "${GITHUB_ACTOR:?GITHUB_ACTOR not set}"

DEPLOY_PORT=${DEPLOY_PORT:-22}
CONTAINER_NAME="catty-app"
PORT="8181"

IMAGE_NAME=$(echo "$IMAGE_NAME" | tr '[:upper:]' '[:lower:]')
IMAGE="$IMAGE_NAME:$RELEASE_HASH"

SSH_OPTIONS="-p $DEPLOY_PORT -o StrictHostKeyChecking=no"

ssh $SSH_OPTIONS "$DEPLOY_USER@$DEPLOY_HOST" bash -s << EOF
    echo "$DOCKER_TOKEN" | sudo docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
    sudo docker pull "$IMAGE"
    
    sudo docker stop "$CONTAINER_NAME" || true
    sudo docker rm "$CONTAINER_NAME" || true
    
    sudo docker run -d \
        -p "$PORT:$PORT" \
        --name "$CONTAINER_NAME" \
        --restart unless-stopped \
        "$IMAGE"
    
    sleep 4
    
    if sudo docker ps | grep -q "$CONTAINER_NAME"; then
        echo "Deployment successful"
    else
        echo "ERROR: App failed to start"
        sudo docker logs "$CONTAINER_NAME"
        exit 1
    fi
EOF
