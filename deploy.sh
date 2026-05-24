#!/bin/bash

BRANCH="${1:-lab1}"
cd "$HOME/catty-reminders-app"

git fetch origin

git checkout -B "$BRANCH" "origin/$BRANCH"

git reset --hard "origin/$BRANCH"

sudo systemctl restart catty
