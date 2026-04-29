#!/bin/bash
set -e

REPO_URL="https://github.com/anzorcode05/catty-reminders-app"
APP_DIR="/home/anzorcode/app"
WEBHOOK_DIR="/home/anzorcode/webhook"
LOG_FILE="$WEBHOOK_DIR/deploy.log"
BRANCH=$1

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

if [ -z "$BRANCH" ]; then
    log "ERROR: No branch specified"
    exit 1
fi

log "========================================="
log "Starting deployment for branch: $BRANCH"

TMP_DIR=$(mktemp -d)
log "Temp directory: $TMP_DIR"

log "Cloning repository..."
git clone --branch $BRANCH $REPO_URL $TMP_DIR

cd $TMP_DIR

export PYTHONPATH=$TMP_DIR:$PYTHONPATH

if [ -d "$TMP_DIR/testlib" ] && [ -d "$TMP_DIR/tests" ]; then
    cp -r $TMP_DIR/testlib $TMP_DIR/tests/
fi

log "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

export PLAYWRIGHT_BROWSERS_PATH=/home/anzorcode/playwright-browsers

log "Installing dependencies..."
pip install -q -r requirements.txt

log "Running tests..."
if pytest tests/ -v --maxfail=1 --disable-warnings; then
    COMMIT_HASH=$(git rev-parse HEAD)
    log "Tests passed"
    log "Commit hash: $COMMIT_HASH"
    
    echo "DEPLOY_REF=$COMMIT_HASH" > $APP_DIR/.env
    log "Saved DEPLOY_REF to .env"
    
    log "Copying files to app directory..."
    rsync -a --delete \
        --exclude='venv' \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        $TMP_DIR/ $APP_DIR/
    
    cp -r $TMP_DIR/tests $APP_DIR/ 2>/dev/null || true
    
    log "Restarting application service..."
    sudo systemctl restart app
    
    log "Deployment completed successfully"
else
    log "Tests failed. Deployment aborted."
    rm -rf $TMP_DIR
    exit 1
fi

rm -rf $TMP_DIR
log "Cleaned up temp directory"
log "========================================="
