#!/usr/bin/env bash
set -Eeuo pipefail

TARGET_SHA="${1:?usage: deploy.sh <commit-sha> [branch]}"
BRANCH="${2:-lab1}"

BASE_DIR="${APP_BASE_DIR:-/opt/catty-reminders-app}"
APP_DIR="${APP_DIR:-$BASE_DIR/current}"
VENV_DIR="${VENV_DIR:-$BASE_DIR/venv}"
REPO_URL="${REPO_URL:-https://github.com/an664/catty-reminders-app.git}"
APP_SERVICE="${APP_SERVICE:-catty-reminders-app.service}"
LOCK_FILE="${LOCK_FILE:-/run/catty-reminders-app-deploy.lock}"

mkdir -p "$BASE_DIR"

(
  flock 9

  if [ ! -d "$APP_DIR/.git" ]; then
    git clone --no-checkout "$REPO_URL" "$APP_DIR"
  fi

  git -C "$APP_DIR" remote set-url origin "$REPO_URL"
  git -C "$APP_DIR" fetch --prune origin "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH" \
    || git -C "$APP_DIR" fetch --prune origin
  git -C "$APP_DIR" checkout --force "$TARGET_SHA"
  git -C "$APP_DIR" clean -fd

  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
  "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

  tmp_env="$(mktemp)"
  {
    printf 'DEPLOY_REF=%s\n' "$TARGET_SHA"
    printf 'PYTHONUNBUFFERED=1\n'
  } > "$tmp_env"
  install -m 0644 "$tmp_env" /etc/catty-app.env
  rm -f "$tmp_env"

  systemctl restart "$APP_SERVICE"
) 9>"$LOCK_FILE"
