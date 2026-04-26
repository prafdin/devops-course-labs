#!/bin/bash
STATE=$1
DESCRIPTION=$2
REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
OWNER="KuzminStanislav"
REPO="catty-reminders-app"

cd "$REPO_DIR"
SHA=$(git rev-parse HEAD)

curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$OWNER/$REPO/statuses/$SHA \
  -d "{
    \"state\":\"$STATE\",
    \"context\":\"CI/CD Pipeline\",
    \"description\":\"$DESCRIPTION\",
    \"target_url\":\"http://app.kuzmin.course.prafdin.ru\"
  }"
