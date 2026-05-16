#!/usr/bin/env bash
set -Eeuo pipefail

BRANCH="${1:-lab3}"
REQUESTED_SHA="${2:-}"
APP_DIR="/home/kali/catty-reminders-app"

echo "Deploying branch '$BRANCH' via Docker into '$APP_DIR'"

cd "$APP_DIR"
git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"

if [[ -n "$REQUESTED_SHA" ]]; then
    git reset --hard "$REQUESTED_SHA"
fi

echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

echo "Pulling Docker image: $IMAGE"
docker pull "$IMAGE"

echo "Stopping old container..."
docker stop catty-test || true
docker rm catty-test || true

echo "Starting new Docker container..."
docker run -d \
  -p 8181:8181 \
  --name catty-test \
  --restart unless-stopped \
  -e DEPLOY_REF="$REQUESTED_SHA" \
  "$IMAGE"

echo "Docker deployment completed successfully!"
