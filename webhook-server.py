#!/usr/bin/env python3
"""
Простой webhook сервер для демонстрации Git автоматизации
Показывает как Git события могут запускать автоматические процессы
"""

import requests
import tempfile
import subprocess
import os
import json
import hashlib
import hmac
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import logging

# Конфигурация
PORT = 8080
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        """Обработка POST запросов от GitHub"""

        # Получаем размер данных
        content_length = int(self.headers.get('Content-Length', 0))

        # Читаем данные
        body = self.rfile.read(content_length)

        # Парсим JSON
        try:
            payload = json.loads(body.decode('utf-8'))
            self.payload = payload
            self._process_webhook(payload)

            # Отвечаем успехом
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')

        except json.JSONDecodeError:
            logging.error("❌ Ошибка парсинга JSON")
            self.send_response(400)
            self.end_headers()

    def do_GET(self):
        """Простая страница статуса"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>DevOps Webhook Demo</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }}
                .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #4d90cd; text-align: center; }}
                .info {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 DevOps Webhook Demo Server</h1>
                <div class="info">
                    <p><strong>Статус:</strong> Сервер активен и ожидает webhook события от GitHub</p>
                    <p><strong>Время запуска:</strong> {time}</p>
                    <p><strong>Порт:</strong> {port}</p>
                </div>
                <p>Этот сервер демонстрирует как Git события могут автоматически запускать процессы.</p>
                <p>Каждый push, pull request или release будет логироваться в консоли сервера.</p>
            </div>
        </body>
        </html>
        """.format(time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), port=PORT)

        self.wfile.write(html.encode('utf-8'))

    def _process_webhook(self, payload):
        """Обработка webhook события"""

        # Получаем информацию о событии
        event_type = self.headers.get('X-GitHub-Event', 'unknown')
        repo_name = payload.get('repository', {}).get('full_name', 'unknown')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logging.info(f"\n🔔 Получено webhook событие:")
        logging.info(f"   Время: {timestamp}")
        logging.info(f"   Тип события: {event_type}")
        logging.info(f"   Репозиторий: {repo_name}")

        # Обрабатываем разные типы событий
        if event_type == 'push':
            self._handle_push_event(payload)
        elif event_type == 'pull_request':
            self._handle_pr_event(payload)
        elif event_type == 'release':
            self._handle_release_event(payload)
        else:
            logging.info(f"   ℹ️  Событие '{event_type}' - базовое логирование")

    def _handle_push_event(self, payload):
        """Обработка push события"""
        commits = payload.get('commits', [])
        branch = payload.get('ref', '').replace('refs/heads/', '')
        pusher = payload.get('pusher', {}).get('name', 'unknown')
        clone_url = payload.get('repository', {}).get('clone_url', 'unknown')
        commit_sha = payload.get('after', '')

        logging.info(f"   📝 Push в ветку: {branch}")
        logging.info(f"   👤 Автор: {pusher}")
        logging.info(f"   📊 Коммитов: {len(commits)}")

        # Имитируем автоматические действия
        logging.info(f"   🚀 ЗАПУСКАЕМ АВТОМАТИЗАЦИЮ:")
        logging.info(f"      - Запуск тестов для ветки {branch}")
        logging.info(f"      - Проверка качества кода")

        with tempfile.TemporaryDirectory() as tmpdir:
            logging.info(f"Временная директория: {tmpdir}")

            # Выполняем git clone
            token = os.environ.get('GITHUB_TOKEN')
            clone_url = f"https://{token}@github.com/VictorGolenkov/catty-reminders-app.git"
            subprocess.run(
                ["git", "clone", clone_url, tmpdir],
                check=True
            )

            subprocess.run(
                ["git", "checkout", branch],
                cwd=tmpdir,
                check=True
            )

            # Запускаем тесты перед деплоем
            logging.info(f"      - Запуск тестов...")
            try:
                result = subprocess.run(
                    ["./test.sh"],
                    cwd=tmpdir,
                    check=True,
                    capture_output=True,
                    text=True
                )
                logging.info(f"      ✅ Тесты прошли успешно!")
                logging.info(f"         {result.stdout.strip()}")

                # Только если тесты прошли - запускаем деплой
                logging.info(f"      - Запуск деплоя...")
                try:
                    subprocess.run(
                        ["./deploy.sh", branch],
                        cwd=tmpdir,
                        check=True
                    )
                    self._send_deployment_status(commit_sha, "success", "Deployed successfully")
                except subprocess.CalledProcessError:
                    self._send_deployment_status(commit_sha, "failure", "Deployment failed")
                logging.info(f"      ✅ Деплой завершен успешно!")

            except subprocess.CalledProcessError as e:
                logging.error(f"      ❌ Тесты упали! Деплой ОТМЕНЕН")
                logging.error(f"         {e.stdout if e.stdout else 'Нет вывода'}")
                self._send_deployment_status(commit_sha, "failure", "Deployment failed")
                if e.stderr:
                    logging.error(f"         Ошибка: {e.stderr}")
                return


    def _handle_pr_event(self, payload):
        """Обработка Pull Request события"""
        action = payload.get('action', '')
        pr_number = payload.get('pull_request', {}).get('number', '')
        title = payload.get('pull_request', {}).get('title', '')

        logging.info(f"   🔀 Pull Request #{pr_number}: {action}")
        logging.info(f"   📋 Заголовок: {title}")

    def _handle_release_event(self, payload):
        """Обработка Release события"""
        action = payload.get('action', '')
        tag_name = payload.get('release', {}).get('tag_name', '')

        logging.info(f"   🏷️  Release {tag_name}: {action}")

    def _send_deployment_status(self, commit_sha, state, description="Deployment completed"):
        """Отправка статуса развертывания в GitHub."""
        # Используем self.payload, который был сохранен в do_POST
        repo = self.payload.get('repository', {}).get('full_name', '')
        token = os.environ.get('GITHUB_TOKEN')

        url = f"https://api.github.com/repos/{repo}/statuses/{commit_sha}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "state": state,
            "description": description,
            "context": "deployment/webhook",
            "target_url": "http://app.golenkov.course.prafdin.space"
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            logging.info(f"   ✅ Статус '{state}' отправлен в GitHub для коммита {commit_sha[:7]}")
        except Exception as e:
            logging.error(f"   ❌ Ошибка отправки статуса: {e}")

def main():
    """Запуск webhook сервера"""

    logging.info(f"🚀 Запуск DevOps Webhook Demo Server")
    logging.info(f"📡 Порт: {PORT}")
    logging.info(f"🌐 URL: http://0.0.0.0:{PORT}")
    logging.info(f"🔧 Webhook URL: http://0.0.0.0:{PORT}/webhook")
    logging.info(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"\n👀 Ожидание webhook событий от GitHub...")
    logging.info(f"💡 Для остановки: Ctrl+C\n")

    try:
        server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        logging.error(f"\n🛑 Сервер остановлен")

if __name__ == '__main__':
    main()
