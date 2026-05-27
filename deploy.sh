#!/bin/bash
set -e

cd /home/qzm/Desktop/catty-reminders-app

docker compose pull
docker compose down --volumes --remove-orphans || true
docker rm -f catty_db catty_app || true
docker compose up -d --remove-orphans
