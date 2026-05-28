#!/bin/bash
set -e

export REPO_LOWER=$(echo "${{ github.repository }}" | tr '[:upper:]' '[:lower:]')

cd /home/qzm/Desktop/catty-reminders-app/

echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin

docker compose pull
docker compose up -d --remove-orphans --force-recreate

sleep 5

if [ $(docker inspect -f '{{.State.Running}}' catty_backend) == "true" ]; then
    exit 0
else
    docker logs catty_backend
    exit 1
fi
