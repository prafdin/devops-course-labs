#!/usr/bin/env python3
import os
import subprocess
import threading
import logging
from flask import Flask, request, jsonify

REPO_DIR = "/home/dmitri/app"
ENV_FILE = "/etc/app-deploy-env"
SERVICE = "app"

app = Flask(__name__)
logging.basicConfig(
    filename="/home/dmitri/deploy.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_deploy(sha, ref):
    """Асинхронный деплой: обновление кода + перезапуск сервиса"""
    try:
        logging.info(f"Starting deploy for {sha[:7]} ({ref})")
        
        # 1. Обновляем код в репозитории
        subprocess.run(["git", "-C", REPO_DIR, "fetch", "--all"], check=True, timeout=60)
        subprocess.run(["git", "-C", REPO_DIR, "reset", "--hard", sha], check=True, timeout=30)
        
        # 2. Сохраняем хэш для отслеживания
        with open(ENV_FILE, "w") as f:
            f.write(f"DEPLOY_REF={sha}\nDEPLOY_BRANCH={ref}\n")
        
        # 3. Перезапускаем приложение
        subprocess.run(["sudo", "systemctl", "restart", SERVICE], check=True, timeout=15)
        
        logging.info(f"✅ Deploy success: {sha[:7]}")
    except Exception as e:
        logging.error(f"❌ Deploy failed: {e}")

@app.route('/', methods=['POST'])
def handle_webhook():
    event = request.headers.get('X-GitHub-Event')
    
    if event == 'push':
        payload = request.json or {}
        sha = payload.get('after')
        ref = payload.get('ref', 'unknown')
        
        # Игнорируем события удаления ветки
        if sha and sha != "0000000000000000000000000000000000000000":
            # Запускаем деплой в отдельном потоке, чтобы быстро ответить GitHub
            threading.Thread(target=run_deploy, args=(sha, ref), daemon=True).start()
            return jsonify({"status": "deploying"}), 202
    
    return jsonify({"status": "ignored"}), 200

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
