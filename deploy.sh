#!/bin/bash

cd "$HOME/catty-reminders-app"

git fetch origin

git reset --hard origin/lab1

sudo systemctl restart catty
