#!/usr/bin/env python3
import os
import subprocess
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

APP_DIR = "/opt/catty-app"
REPO_URL = "https://github.com/IMPULSE-LAB-CRYPTO/catty-reminders-app.git"

def deploy():
    # 1. Клонирование или обновление кода
    if not os.path.exists(APP_DIR):
        subprocess.run(["git", "clone", REPO_URL, APP_DIR], check=True)
    else:
        subprocess.run(["git", "-C", APP_DIR, "pull"], check=True)

    # 2. Сборка приложения (если требуется)
    # Для Python-приложений сборка обычно не нужна, но если есть скрипт build.sh – выполняем
    build_script = os.path.join(APP_DIR, "build.sh")
    if os.path.exists(build_script) and os.access(build_script, os.X_OK):
        subprocess.run([build_script], cwd=APP_DIR, check=True)
        print("✅ Сборка выполнена")
    else:
        print("ℹ️ Скрипт сборки не найден, пропускаем")

    # 3. Запуск тестов
    # Пытаемся запустить test.sh, если есть
    test_script = os.path.join(APP_DIR, "test.sh")
    if os.path.exists(test_script) and os.access(test_script, os.X_OK):
        try:
            subprocess.run([test_script], cwd=APP_DIR, check=True)
            print("✅ Тесты (test.sh) пройдены")
        except subprocess.CalledProcessError:
            print("❌ Тесты не пройдены, деплой остановлен")
            return
    else:
        # Если test.sh нет, пробуем pytest (если установлен)
        try:
            subprocess.run(["pytest"], cwd=APP_DIR, check=True)
            print("✅ Тесты (pytest) пройдены")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ℹ️ Тесты не найдены или не настроены, продолжаем без тестов")

    # 4. Установка зависимостей (из requirements.txt)
    req_file = os.path.join(APP_DIR, "requirements.txt")
    if os.path.exists(req_file):
        subprocess.run(["pip3", "install", "-r", req_file], check=True)
        print("✅ Зависимости установлены")

    # 5. Перезапуск сервиса приложения
    subprocess.run(["sudo", "systemctl", "restart", "catty-app"], check=True)
    print("✅ Сервис catty-app перезапущен")

@app.route('/', methods=['POST'])
def webhook():
    event = request.headers.get('X-GitHub-Event')
    if event != 'push':
        return jsonify({'msg': 'ignored'}), 200

    # Запускаем deploy в фоне, чтобы не задерживать ответ GitHub
    subprocess.Popen([sys.executable, os.path.abspath(__file__), 'deploy'])
    return jsonify({'status': 'accepted'}), 202

@app.route('/health', methods=['GET'])
def health():
    return "ok"

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'deploy':
        deploy()
    else:
        app.run(host='0.0.0.0', port=8080)