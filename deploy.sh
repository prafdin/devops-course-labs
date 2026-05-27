#!/bin/bash
set -e

cd /home/qzm/Desktop/catty-reminders-app

docker compose pull
docker compose up -d --remove-orphans
