import os
import subprocess
import threading
import logging
import hmac
import hashlib
from flask import Flask, request, jsonify

# ========== КОНФИГУРАЦИЯ ==========
REPO_DIR = "/home/vboxuser/catty-reminders-app"
ENV_FILE = "/etc/catty-app-env"
SERVICE = "catty"
SECRET = "devops-webhook-secret" 
LOG_FILE = "/home/vboxuser/deploy.log"

app = Flask(__name__)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def verify_signature(payload_body, signature_header):
    """Проверка подписи GitHub (для безопасности)"""
    if not signature_header:
        return False
    hash_object = hmac.new(SECRET.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

def run_deploy(sha, branch_ref):
    """Асинхронный деплой: обновление кода, запись DEPLOY_REF, перезапуск сервиса"""
    try:
        logging.info(f"Начинаю деплой для коммита {sha} (ветка {branch_ref})")
        
        # 1. Обновить код 
        subprocess.run(["/usr/bin/git", "-C", REPO_DIR, "fetch", "--all"], check=True, capture_output=True)
        subprocess.run(["/usr/bin/git", "-C", REPO_DIR, "reset", "--hard", sha], check=True, capture_output=True)
        
        # 2. Обновить зависимости
        subprocess.run([f"{REPO_DIR}/venv/bin/pip", "install", "-r", f"{REPO_DIR}/requirements.txt"], check=True, capture_output=True)
        
        # 3. Записать новый DEPLOY_REF в файл окружения
        with open(ENV_FILE, "w") as f:
            f.write(f"DEPLOY_REF={sha}\n")
        
        # 4. Перезапустить systemd сервис
        subprocess.run(["sudo", "systemctl", "restart", SERVICE], check=True, capture_output=True)
        
        logging.info(f"Деплой успешен: {sha}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при выполнении команды: {e.stderr.decode() if e.stderr else str(e)}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook():
    # Проверяем тип события
    event_type = request.headers.get('X-GitHub-Event')
    if event_type != 'push':
        logging.info(f"Игнорируем событие {event_type}")
        return jsonify({"status": "ignored", "reason": "not a push event"}), 200
    
    # Проверка подписи
     signature = request.headers.get('X-Hub-Signature-256')
     if not verify_signature(request.data, signature):
         logging.warning("Неверная подпись запроса")
         return jsonify({"status": "error", "reason": "invalid signature"}), 403
    
    payload = request.json
    sha = payload.get('after')
    ref = payload.get('ref', '')
    
    # Игнорируем удаление ветки (sha = 0000...)
    if not sha or sha == '0000000000000000000000000000000000000000':
        logging.info("Получен push с нулевым SHA (удаление ветки), игнорируем")
        return jsonify({"status": "ignored", "reason": "branch deletion"}), 200
    
    # Деплоим только для ветки lab1
    if ref != 'refs/heads/lab1':
        logging.info(f"Push в ветку {ref} не соответствует целевой (lab1), игнорируем")
        return jsonify({"status": "ignored", "reason": "wrong branch"}), 200
    
    # Запускаем деплой в отдельном потоке, чтобы не блокировать ответ
    threading.Thread(target=run_deploy, args=(sha, ref)).start()
    
    logging.info(f"Принят push для {sha}, деплой запущен")
    return jsonify({"status": "accepted", "commit": sha}), 202

# Для совместимости с оригинальной инструкцией – оставляем также корневой путь '/'
@app.route('/', methods=['POST'])
def legacy_webhook():
    return webhook()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
