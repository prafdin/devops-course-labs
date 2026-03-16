#!/usr/bin/env python3
"""
Webhook handler for catty-reminders-app
Правильное переключение на любую ветку
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os
import threading
import logging
import datetime
import signal
import sys
import getpass
import time

# ===== Конфигурация =====
REPO_URL = "git@github.com:TimurMif/catty-reminders-app.git"
APP_DIR = "/opt/catty-reminders"
VENV_DIR = os.path.join(APP_DIR, "venv")
LOG_FILE = "/var/log/webhook/webhook.log"
DEPLOY_LOG = "/var/log/webhook/deployments.log"

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode('utf-8'))
            event = self.headers.get('X-GitHub-Event', 'unknown')
            logging.info(f"Получено событие: {event}")

            if event == 'push':
                branch = payload.get('ref', '').replace('refs/heads/', '')
                logging.info(f"Push в ветку: {branch}")

                commits = payload.get('commits', [])
                if commits:
                    last_commit = commits[-1]
                    commit_msg = last_commit.get('message', '')
                    committer = last_commit.get('committer', {}).get('name', '')
                    logging.info(f"Коммит: {commit_msg} от {committer}")

                thread = threading.Thread(target=self.deploy_app, args=(branch,))
                thread.start()

                self.send_response(202)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "accepted",
                    "message": f"Деплой ветки {branch} запущен"
                }).encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ignored"}).encode())

        except json.JSONDecodeError:
            logging.error("Неверный JSON")
            self.send_response(400)
            self.end_headers()
        except Exception as e:
            logging.error(f"Ошибка обработки: {str(e)}")
            self.send_response(500)
            self.end_headers()

    def deploy_app(self, branch):
        """Основная функция деплоя"""
        lock_file = "/tmp/deploy.lock"
        lock_acquired = False
        for attempt in range(5):
            if not os.path.exists(lock_file):
                try:
                    with open(lock_file, 'w') as f:
                        f.write(str(os.getpid()))
                    lock_acquired = True
                    break
                except:
                    pass
            logging.warning(f"Деплой уже выполняется, ожидание... (попытка {attempt+1}/5)")
            time.sleep(2)
        if not lock_acquired:
            logging.error("Не удалось получить блокировку, пропускаем")
            return

        try:
            logging.info(f"Начинаем деплой ветки: {branch}")

            # Клонирование, если репозитория нет
            if not os.path.exists(os.path.join(APP_DIR, '.git')):
                logging.info("Клонирование репозитория...")
                result = subprocess.run(
                    ["git", "clone", REPO_URL, APP_DIR],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode != 0:
                    logging.error(f"Ошибка клонирования: {result.stderr}")
                    return
                logging.info(f"Clone: {result.stdout}")

            os.chdir(APP_DIR)

            # Получаем все ветки
            logging.info("Fetch всех веток...")
            result = subprocess.run(
                ["git", "fetch", "--all"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logging.error(f"Ошибка fetch: {result.stderr}")
                return
            logging.info(f"Fetch: {result.stdout}")

            # ПРОВЕРЯЕМ, ЕСТЬ ЛИ ВЕТКА НА ORIGIN
            result = subprocess.run(
                ["git", "ls-remote", "--heads", "origin", branch],
                capture_output=True, text=True, timeout=10
            )
            branch_exists = branch in result.stdout
            
            if not branch_exists:
                logging.warning(f"Ветка '{branch}' не найдена на origin, используем 'lab1'")
                branch = "lab1"

            # ПЕРЕКЛЮЧАЕМСЯ ПРАВИЛЬНО:
            # 1. Создаём локальную ветку, отслеживающую origin/branch
            logging.info(f"Создаём локальную ветку {branch} из origin/{branch}")
            checkout_cmd = ["git", "checkout", "-B", branch, f"origin/{branch}"]
            result = subprocess.run(
                checkout_cmd,
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0:
                logging.error(f"Ошибка checkout: {result.stderr}")
                # Если не получилось, пробуем просто сбросить
                logging.info("Пробуем простой reset...")
                result = subprocess.run(
                    ["git", "reset", "--hard", f"origin/{branch}"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode != 0:
                    logging.error(f"Ошибка reset: {result.stderr}")
                    return
            logging.info(f"Checkout результат: {result.stdout}")

            # Получаем текущий SHA
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            logging.info(f"Текущий SHA: {sha} (ветка {branch})")

            # Записываем SHA в файл для приложения
            try:
                with open(os.path.join(APP_DIR, ".deploy_ref"), "w") as f:
                    f.write(f"DEPLOY_REF={sha}\n")
                logging.info(f"Обновлён deploy ref: {sha}")
            except Exception as e:
                logging.error(f"Не удалось записать deploy ref: {e}")

            # Установка зависимостей (если есть)
            req_file = os.path.join(APP_DIR, "requirements.txt")
            if os.path.exists(req_file):
                logging.info("Установка Python-зависимостей...")
                pip_path = os.path.join(VENV_DIR, "bin", "pip")
                if os.path.exists(pip_path):
                    result = subprocess.run(
                        [pip_path, "install", "-r", req_file],
                        capture_output=True, text=True, timeout=120
                    )
                    if result.returncode != 0:
                        logging.error(f"Pip install error: {result.stderr}")
                    else:
                        logging.info(f"Pip: {result.stdout}")
                else:
                    logging.error(f"pip не найден в {pip_path}")

            # Перезапуск сервиса приложения
            logging.info("Перезапуск сервиса catty-reminders...")
            result = subprocess.run(
                ["sudo", "systemctl", "restart", "catty-reminders"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logging.error(f"Ошибка перезапуска: {result.stderr}")
                return
            logging.info(f"Перезапуск выполнен: {result.stdout}")

            # Логирование успеха
            with open(DEPLOY_LOG, 'a') as f:
                f.write(f"{datetime.datetime.now()} - Деплой ветки {branch} успешен\n")
            logging.info(f"Деплой завершён для ветки {branch}")

        except subprocess.TimeoutExpired as e:
            logging.error(f"Таймаут: {e}")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logging.error(f"Ошибка деплоя: {error_msg}")
            with open(DEPLOY_LOG, 'a') as f:
                f.write(f"{datetime.datetime.now()} - Деплой ветки {branch} провален: {error_msg}\n")
        except Exception as e:
            logging.error(f"Неожиданная ошибка: {str(e)}")
        finally:
            if os.path.exists(lock_file):
                os.remove(lock_file)

    def log_message(self, format, *args):
        logging.info(f"{self.address_string()} - {format % args}")

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    logging.info(f"Запуск webhook сервера на порту {port}")
    print(f"Webhook сервер запущен на порту {port}")
    print("Нажмите Ctrl+C для остановки")

    def signal_handler(sig, frame):
        print("\nОстановка сервера...")
        httpd.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
