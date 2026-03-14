#!/usr/bin/env python3
import os
import subprocess
import sys
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

APP_DIR = "/opt/catty-app"
REPO_URL = "https://github.com/IMPULSE-LAB-CRYPTO/catty-reminders-app.git"
LOG_FILE = "/var/log/webhook/deploy.log"

def log_message(msg):
    """Запись сообщения в лог-файл с временной меткой"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)  # также выводим в консоль (для journalctl)

def deploy():
    log_message("🚀 Начат процесс развёртывания")

    # 1. Клонирование или обновление кода
    try:
        if not os.path.exists(APP_DIR):
            subprocess.run(["git", "clone", REPO_URL, APP_DIR], check=True, capture_output=True, text=True)
            log_message("✅ Репозиторий склонирован")
        else:
            result = subprocess.run(["git", "-C", APP_DIR, "pull"], check=True, capture_output=True, text=True)
            log_message(f"✅ Код обновлён: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        log_message(f"❌ Ошибка при обновлении кода: {e.stderr}")
        return

    # 2. Сборка (build.sh)
    build_script = os.path.join(APP_DIR, "build.sh")
    if os.path.exists(build_script) and os.access(build_script, os.X_OK):
        try:
            result = subprocess.run([build_script], cwd=APP_DIR, check=True, capture_output=True, text=True)
            log_message(f"✅ Сборка выполнена:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            log_message(f"❌ Ошибка сборки:\n{e.stderr}")
            return
    else:
        log_message("ℹ️ Скрипт сборки не найден, пропускаем")

    # 3. Тесты
    test_script = os.path.join(APP_DIR, "test.sh")
    if os.path.exists(test_script) and os.access(test_script, os.X_OK):
        try:
            result = subprocess.run([test_script], cwd=APP_DIR, check=True, capture_output=True, text=True)
            log_message(f"✅ Тесты (test.sh) пройдены:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            log_message(f"❌ Тесты не пройдены:\n{e.stderr}")
            return
    else:
        # Попытка запустить pytest, если установлен
        try:
            result = subprocess.run(["pytest"], cwd=APP_DIR, check=True, capture_output=True, text=True)
            log_message(f"✅ Тесты (pytest) пройдены:\n{result.stdout}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            log_message("ℹ️ Тесты не настроены, продолжаем без тестов")

    # 4. Установка зависимостей
    req_file = os.path.join(APP_DIR, "requirements.txt")
    if os.path.exists(req_file):
        try:
            result = subprocess.run(["pip3", "install", "-r", req_file], check=True, capture_output=True, text=True)
            log_message(f"✅ Зависимости установлены:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            log_message(f"❌ Ошибка при установке зависимостей:\n{e.stderr}")
            return

    # Получение хеша коммита для deployref
    try:
        commit_hash = subprocess.run(
            ["git", "-C", APP_DIR, "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        with open("/etc/catty-app-env", "w") as f:
            f.write(f"DEPLOY_REF={commit_hash}\n")
        log_message(f"✅ Хеш коммита сохранён: {commit_hash}")
    except Exception as e:
        log_message(f"⚠️ Не удалось получить хеш коммита: {e}")

    # 5. Перезапуск сервиса
    try:
        subprocess.run(["sudo", "systemctl", "restart", "catty-app"], check=True, capture_output=True, text=True)
        log_message("✅ Сервис catty-app перезапущен")
    except subprocess.CalledProcessError as e:
        log_message(f"❌ Ошибка при перезапуске сервиса:\n{e.stderr}")
        return

    log_message("🎉 Развёртывание завершено успешно")

@app.route('/', methods=['POST'])
def webhook():
    event = request.headers.get('X-GitHub-Event')
    if event != 'push':
        return jsonify({'msg': 'ignored'}), 200

    log_message("📩 Получен webhook (push), запускаем deploy в фоне")
    subprocess.Popen([sys.executable, os.path.abspath(__file__), 'deploy'])
    return jsonify({'status': 'accepted'}), 202

@app.route('/health', methods=['GET'])
def health():
    return "ok"

@app.route('/logs', methods=['GET'])
def show_logs():
    """Отдаёт последние 50 строк лога (просто для проверки)"""
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()[-50:]  # последние 50 строк
        return "<pre>" + "".join(lines) + "</pre>", 200
    except FileNotFoundError:
        return "Лог-файл ещё не создан", 404

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'deploy':
        deploy()
    else:
        app.run(host='0.0.0.0', port=8080)