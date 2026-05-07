#!/bin/bash
set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" ]]; then
    echo "CRITICAL: Missing required variables."
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')
IMAGE_NAME="ghcr.io/${REPO_LOWER}:${RELEASE_HASH}"

echo "Deploying image: $IMAGE_NAME"

ssh -p "$TARGET_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "bash -s" << REMOTE_SCRIPT
    set -e

    echo "${GITHUB_TOKEN}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin

    echo "--> Pulling image"
    docker pull ${IMAGE_NAME}
    
    echo "--> Cleaning up old container"
    docker stop catty-app || true
    docker rm catty-app || true
    
    echo "--> Starting new container on port 80"
    docker run -d \
        --name catty-app \
        --restart always \
        -p 80:8181 \
        -e COMMIT_SHA=${RELEASE_HASH} \
        ${IMAGE_NAME}
        
    echo "--> Deployment successful"
REMOTE_SCRIPT
