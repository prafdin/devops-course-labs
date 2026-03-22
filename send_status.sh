#!/bin/bash
STATE=$1
DESCRIPTION=$2
SHA=$(git rev-parse HEAD)

curl -X POST \
-H "Authorization: Bearer $GITHUB_TOKEN" \
-H "Accept: application/vnd.github+json" \
https://api.github.com/repos/Vadimkadkdoofjf/catty-reminders-app/statuses/$SHA \
-d "{
    \"state\":\"$STATE\",
    \"context\":\"webhook-deploy\",
    \"description\":\"$DESCRIPTION\",
    \"target_url\":\"http://app.petrov.course.prafdin.ru\"
}"
