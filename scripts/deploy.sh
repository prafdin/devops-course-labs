#!/usr/bin/env bash
set -Eeuo pipefail

BRANCH="${1:-}"
REQUESTED_SHA="${2:-}"

if [[ -z "$BRANCH" ]]; then
  echo "Usage: $0 <branch> [sha]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_REPO_URL="$(git -C "$SCRIPT_DIR/.." remote get-url origin 2>/dev/null || true)"

REPO_URL="${REPO_URL:-$DEFAULT_REPO_URL}"
APP_DIR="${APP_DIR:-/opt/catty/app}"
APP_SERVICE="${APP_SERVICE:-catty-app.service}"
APP_RESTART_COMMAND="${APP_RESTART_COMMAND:-}"
APP_ENV_FILE="${APP_ENV_FILE:-$APP_DIR/.env}"
IMAGE="${IMAGE:-}"
COMPOSE_DEPLOY="${COMPOSE_DEPLOY:-0}"
COMPOSE_FILE_PATH="${COMPOSE_FILE_PATH:-$APP_DIR/docker-compose.yaml}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-catty}"
CONTAINER_NAME="${CONTAINER_NAME:-catty-reminders-app}"
CONTAINER_PORT="${CONTAINER_PORT:-8181}"
HOST_PORT="${HOST_PORT:-8181}"
DOCKER_BIN="${DOCKER_BIN:-}"
LOCK_FILE="${LOCK_FILE:-/tmp/catty-deploy.lock}"
LOCK_DIR="${LOCK_DIR:-/tmp/catty-deploy.lockdir}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUN_TESTS="${RUN_TESTS:-1}"
TEST_COMMAND="${TEST_COMMAND:-.venv/bin/python -m pytest tests/test_unit.py}"

if [[ -z "$REPO_URL" ]]; then
  echo "REPO_URL is not set and could not be read from git remote origin" >&2
  exit 2
fi

run_docker_deploy() {
  if [[ -z "$IMAGE" ]]; then
    return 1
  fi

  if [[ -z "$DOCKER_BIN" ]]; then
    DOCKER_BIN="$(command -v docker || true)"
  fi
  if [[ -z "$DOCKER_BIN" && -x /opt/homebrew/bin/docker ]]; then
    DOCKER_BIN="/opt/homebrew/bin/docker"
  fi
  if [[ -z "$DOCKER_BIN" && -x /usr/local/bin/docker ]]; then
    DOCKER_BIN="/usr/local/bin/docker"
  fi
  if [[ -z "$DOCKER_BIN" ]]; then
    echo "docker command not found" >&2
    exit 1
  fi

  export PATH="$(dirname "$DOCKER_BIN"):$PATH"
  export DOCKER_CONFIG="${DOCKER_CONFIG:-/tmp/catty-docker-config}"
  mkdir -p "$DOCKER_CONFIG"

  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    echo "$GITHUB_TOKEN" | "$DOCKER_BIN" login ghcr.io -u "${GITHUB_ACTOR:-github-actions}" --password-stdin
  fi

  if [[ "$COMPOSE_DEPLOY" == "1" ]]; then
    if [[ ! -f "$COMPOSE_FILE_PATH" ]]; then
      echo "docker compose file not found at $COMPOSE_FILE_PATH" >&2
      exit 1
    fi

    "$DOCKER_BIN" stop "$CONTAINER_NAME" 2>/dev/null || true
    "$DOCKER_BIN" rm "$CONTAINER_NAME" 2>/dev/null || true
    export IMAGE
    export DEPLOY_REF="$DEPLOYED_SHA"
    "$DOCKER_BIN" compose -f "$COMPOSE_FILE_PATH" --project-name "$COMPOSE_PROJECT_NAME" pull
    "$DOCKER_BIN" compose -f "$COMPOSE_FILE_PATH" --project-name "$COMPOSE_PROJECT_NAME" up -d --remove-orphans
    "$DOCKER_BIN" image prune -af >/dev/null 2>&1 || true
    return 0
  fi

  "$DOCKER_BIN" pull "$IMAGE"
  "$DOCKER_BIN" stop "$CONTAINER_NAME" 2>/dev/null || true
  "$DOCKER_BIN" rm "$CONTAINER_NAME" 2>/dev/null || true
  "$DOCKER_BIN" run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -p "$HOST_PORT:$CONTAINER_PORT" \
    -e DEPLOY_REF="$DEPLOYED_SHA" \
    "$IMAGE"
}

mkdir -p "$(dirname "$LOCK_FILE")"
if command -v flock >/dev/null 2>&1; then
  exec 200>"$LOCK_FILE"
  flock -x 200
else
  until mkdir "$LOCK_DIR" 2>/dev/null; do
    sleep 1
  done
  trap 'rmdir "$LOCK_DIR"' EXIT
fi

echo "Deploying branch '$BRANCH' from '$REPO_URL' into '$APP_DIR'"

if [[ ! -d "$APP_DIR/.git" ]]; then
  mkdir -p "$(dirname "$APP_DIR")"
  git clone "$REPO_URL" "$APP_DIR"
fi

git -C "$APP_DIR" fetch --prune origin '+refs/heads/*:refs/remotes/origin/*'
git -C "$APP_DIR" checkout -B "$BRANCH" "origin/$BRANCH"
if [[ -n "$REQUESTED_SHA" ]]; then
  git -C "$APP_DIR" reset --hard "$REQUESTED_SHA"
else
  git -C "$APP_DIR" reset --hard "origin/$BRANCH"
fi

DEPLOYED_SHA="$(git -C "$APP_DIR" rev-parse HEAD)"
if [[ -n "$REQUESTED_SHA" && "$DEPLOYED_SHA" != "$REQUESTED_SHA" ]]; then
  echo "Requested SHA $REQUESTED_SHA, deployed SHA $DEPLOYED_SHA" >&2
  exit 1
fi

if [[ ! -x "$APP_DIR/.venv/bin/python" ]]; then
  "$PYTHON_BIN" -m venv "$APP_DIR/.venv"
fi

"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

if [[ "$RUN_TESTS" != "0" ]]; then
  (
    cd "$APP_DIR"
    bash -lc "$TEST_COMMAND"
  )
fi

if [[ -n "$IMAGE" ]]; then
  run_docker_deploy
  echo "Docker deployment completed at $DEPLOYED_SHA with $IMAGE"
  exit 0
fi

touch "$APP_ENV_FILE"
if grep -q '^DEPLOY_REF=' "$APP_ENV_FILE"; then
  sed -i.bak "s/^DEPLOY_REF=.*/DEPLOY_REF=$DEPLOYED_SHA/" "$APP_ENV_FILE"
  rm -f "$APP_ENV_FILE.bak"
else
  printf 'DEPLOY_REF=%s\n' "$DEPLOYED_SHA" >> "$APP_ENV_FILE"
fi

if [[ -n "$APP_RESTART_COMMAND" ]]; then
  bash -lc "$APP_RESTART_COMMAND"
elif [[ -z "$APP_SERVICE" || "$APP_SERVICE" == "none" ]]; then
  echo "Skipping service restart"
elif [[ "$(id -u)" -eq 0 ]]; then
  systemctl restart "$APP_SERVICE"
else
  sudo systemctl restart "$APP_SERVICE"
fi

echo "Deployment completed at $DEPLOYED_SHA"
