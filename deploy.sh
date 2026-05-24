#!/bin/bash
echo "=== Starting deployment ==="
cd /home/alexander/csharp-example

echo "1. Pulling latest changes from GitHub..."
git pull origin lab1

echo "2. Running unit tests..."
dotnet test
if [ $? -eq 0 ]; then
    echo "Tests passed! 🟢"
    echo "3. Building and publishing the application..."
    dotnet publish -c Release -o /home/alexander/app ExampleWebService/ExampleWebService.csproj
    
    # Если скрипту передан аргумент (хэш из вебхука), используем его. 
    # Если нет — берем локальный хэш из git rev-parse.
    if [ -n "$1" ]; then
        COMMIT_HASH="$1"
        echo "Using commit SHA from webhook payload: $COMMIT_HASH"
    else
        COMMIT_HASH=$(git rev-parse HEAD)
        echo "Using local git commit SHA: $COMMIT_HASH"
    fi
    
    echo "DEPLOY_REF=$COMMIT_HASH" > /home/alexander/app/csharp.env
    echo "Saved commit hash ($COMMIT_HASH) to environment file."
    
    echo "4. Restarting the web application service..."
    sudo /usr/bin/systemctl restart csharp-app.service
    echo "=== Deployment finished successfully! 🚀 ==="
else
    echo "Tests failed! 🔴 Deployment aborted."
    exit 1
fi
