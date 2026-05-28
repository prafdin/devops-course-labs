#!/bin/bash
set -e

cd /home/qzm/Desktop/catty-reminders-app/

export REPO_LOWER="${REPO_LOWER}"
export RELEASE_HASH="${RELEASE_HASH}"

sed -i "s|image: ghcr.io/.*:latest|image: ghcr.io/${REPO_LOWER}:${RELEASE_HASH}|" docker-compose.yaml

docker compose pull
docker compose up -d --remove-orphans --force-recreate

sleep 8

if [ "$(docker inspect -f '{{.State.Running}}' catty_backend)" = "true" ]; then
    echo "Deployment successful"
    exit 0
else
    docker logs catty_backend
    exit 1
fi
