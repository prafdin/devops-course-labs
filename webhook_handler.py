#!/usr/bin/env python3
import os
import subprocess
import sys
import datetime
import json
import logging
from flask import Flask, request, jsonify

# --- КОНФИГУРАЦИЯ ---
APP_DIR = "/home/ilya/catty-reminders-app"
ENV_FILE = "/etc/catty-app-env"
LOG_FILE = "/var/log/webhook/deploy.log"
REPO_URL = "https://github.com/IMPULSE-LAB-CRYPTO/catty-reminders-app.git"

app = Flask(__name__)

# Настройка подробного логирования
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_command(cmd, working_dir=None):
    """Запускает системную команду и логирует результат/ошибки"""
    try:
        result = subprocess.run(
            cmd, 
            cwd=working_dir, 
            check=True, 
            capture_output=True, 
            text=True,
            shell=isinstance(cmd, str)
        )
        logging.info(f"Команда выполнена: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка команды: {e.cmd}")
        logging.error(f"Вывод ошибки (stderr): {e.stderr}")
        return False, e.stderr

def deploy_process(commit_hash):
    """Основная логика развертывания"""
    logging.info(f"--- СТАРТ ДЕПЛОЯ (Коммит: {commit_hash}) ---")

    # 1. Проверка директории
    if not os.path.exists(APP_DIR):
        logging.warning(f"Директория {APP_DIR} не найдена. Клонирую...")
        success, out = run_command(["git", "clone", REPO_URL, APP_DIR])
        if not success: return

    # 2. Обновление кода
    logging.info("Обновление кода через git fetch и reset...")
    run_command(["git", "-C", APP_DIR, "fetch", "--all"])
    success, out = run_command(["git", "-C", APP_DIR, "reset", "--hard", commit_hash])
    if not success:
        logging.error("Не удалось переключиться на коммит. Возможно, хеш неверный.")
        return

    # 3. Установка зависимостей
    if os.path.exists(os.path.join(APP_DIR, "requirements.txt")):
        logging.info("Установка зависимостей через pip...")
        success, out = run_command(["pip3", "install", "-r", "requirements.txt"], working_dir=APP_DIR)
    
    # 4. Запись переменной окружения (Критично для прохождения тестов лабы)
    logging.info(f"Запись DEPLOY_REF в {ENV_FILE}...")
    env_cmd = f"echo 'DEPLOY_REF={commit_hash}' | sudo tee {ENV_FILE}"
    success, out = run_command(env_cmd)

    # 5. Перезапуск основного сервиса
    logging.info("Перезапуск сервиса catty-app...")
    success, out = run_command(["sudo", "systemctl", "restart", "catty-app"])
    
    if success:
        logging.info("--- ДЕПЛОЙ УСПЕШНО ЗАВЕРШЕН ---")
    else:
        logging.error("--- ДЕПЛОЙ ЗАВЕРШИЛСЯ С ОШИБКОЙ ПРИ ПЕРЕЗАПУСКЕ ---")

@app.route('/', methods=['POST'])
def webhook_receiver():
    # Проверка на Ping от GitHub
    event = request.headers.get('X-GitHub-Event')
    if event == 'ping':
        return jsonify({'status': 'pong'}), 200

    # Получаем JSON данные
    try:
        data = request.get_json(force=True)
    except Exception as e:
        logging.error(f"Ошибка парсинга JSON: {e}")
        return jsonify({'error': 'invalid json'}), 400

    if event != 'push':
        return jsonify({'status': 'ignored', 'event': event}), 200

    # Извлечение коммита (пробуем разные поля)
    commit_hash = data.get('after')
    if not commit_hash or commit_hash == "0000000000000000000000000000000000000000":
        # Если это пуш новой ветки или специфическое событие
        commit_hash = data.get('head_commit', {}).get('id')

    if not commit_hash:
        logging.warning(f"Получен push запрос без хеша коммита. Данные: {list(data.keys())}")
        return jsonify({'error': 'no commit hash found'}), 400

    # Запуск деплоя в отдельном процессе
    logging.info(f"📩 Webhook принят: событие {event}, коммит {commit_hash}")
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--execute-deploy", commit_hash])


    return jsonify({
        'status': 'deploying',
        'commit': commit_hash,
        'message': 'Deployment started in background'
    }), 202

if __name__ == '__main__':
    # Если скрипт вызван для выполнения деплоя
    if len(sys.argv) > 1 and sys.argv[1] == "--execute-deploy":
        deploy_process(sys.argv[2])
    else:
        # Запуск сервера
        logging.info("Запуск Flask сервера на порту 8080...")
        app.run(host='0.0.0.0', port=8080, debug=False)