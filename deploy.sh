#!/bin/bash
set -e

cd /home/qzm/Desktop/catty-reminders-app/

echo "Updating docker-compose with image: ghcr.io/$REPO_LOWER:$RELEASE_HASH"

sed -i "s|image: ghcr.io/[^:]*:.*|image: ghcr.io/$REPO_LOWER:$RELEASE_HASH|" docker-compose.yaml

docker compose pull
docker compose up -d --remove-orphans --force-recreate

sleep 8

if docker inspect -f '{{.State.Running}}' catty_backend 2>/dev/null | grep -q true; then
    echo "Deployment successful"
    exit 0
else
    echo "Container is not running. Logs:"
    docker logs catty_backend || true
    exit 1
fi
