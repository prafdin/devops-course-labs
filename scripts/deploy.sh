#!/bin/bash
set -e

if [ -z "$DEPLOY_HOST" ] || [ -z "$DEPLOY_USER" ] || [ -z "$RELEASE_HASH" ] || [ -z "$IMAGE_NAME" ]; then
    echo "Error: Required environment variables (DEPLOY_HOST, DEPLOY_USER, RELEASE_HASH, IMAGE_NAME) are not set"
    exit 1
fi

DEPLOY_PORT=${DEPLOY_PORT:-22}
CONTAINER_NAME="catty-app"
IMAGE="$IMAGE_NAME:$RELEASE_HASH"

echo "Deploying image $IMAGE to $DEPLOY_HOST"

ssh -p "$DEPLOY_PORT" -o StrictHostKeyChecking=no "$DEPLOY_USER@$DEPLOY_HOST" << EOF
    set -e
    
    echo "> Logging in to GHCR..."
    echo "$DOCKER_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

    echo "> Pulling image..."
    docker pull $IMAGE
    
    echo "> Cleaning up old container..."
    docker stop $CONTAINER_NAME || true
    docker rm $CONTAINER_NAME || true
    
    echo "> Starting new container on port 80..."
    docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        -p 80:8181 \
        -e COMMIT_SHA=$RELEASE_HASH \
        -e DEPLOY_REF=$RELEASE_HASH \
        $IMAGE
    
    echo "> Deployment finished successfully"
EOF
