#!/usr/bin/env python3
import tempfile
import subprocess
import os
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
REPO_PATH = "/home/ubuntu/devops/catty-reminders-app"  # ПАПКА ДЛЯ ПРИЛОЖЕНИЯ
REPO_URL = "https://github.com/mzpdqk/catty-reminders-app"

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body.decode('utf-8'))
            self._process_webhook(payload)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        except json.JSONDecodeError:
            print("❌ Ошибка парсинга JSON")
            self.send_response(400)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"""
        <html><body>
        <h1>Webhook Handler Active</h1>
        <p>Сервер работает на порту 8080</p>
        </body></html>
        """)

    def _process_webhook(self, payload):
        event_type = self.headers.get('X-GitHub-Event', 'unknown')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n🔔 Получено webhook событие: {timestamp}")
        print(f"   Тип: {event_type}")
        
        if event_type == 'push':
            self._handle_push_event(payload)

    def _handle_push_event(self, payload):
        branch = payload.get('ref', '').replace('refs/heads/', '')
        commits = payload.get('commits', [])
        
        print(f"   📝 Push в ветку: {branch}")
        print(f"   📊 Коммитов: {len(commits)}")
        
        # 1. Клонируем или обновляем код
        print(f"   🔄 Обновление кода...")
        if not os.path.exists(REPO_PATH):
            subprocess.run(['git', 'clone', REPO_URL, REPO_PATH], check=True)
        
        # Переключаемся на нужную ветку
        subprocess.run(['git', '-C', REPO_PATH, 'fetch', 'origin'], check=True)
        subprocess.run(['git', '-C', REPO_PATH, 'checkout', branch], check=True)
        subprocess.run(['git', '-C', REPO_PATH, 'pull', 'origin', branch], check=True)
        
        # 2. Установка зависимостей (если есть requirements.txt)
        req_file = os.path.join(REPO_PATH, 'requirements.txt')
        if os.path.exists(req_file):
            print(f"   📦 Установка зависимостей...")
            subprocess.run(['pip', 'install', '-r', req_file], check=True)
        
        # 3. Запуск тестов (если есть test.sh)
        test_script = os.path.join(REPO_PATH, 'test.sh')
        if os.path.exists(test_script):
            print(f"   🧪 Запуск тестов...")
            subprocess.run([test_script], cwd=REPO_PATH, check=True)
        
        # 4. Перезапуск приложения через systemd
        print(f"   🚀 Перезапуск приложения...")
        subprocess.run(['sudo', 'systemctl', 'restart', 'myapp'], check=True)
        
        print(f"   ✅ Деплой завершен успешно!")

def main():
    print(f"🚀 Запуск Webhook Handler на порту {PORT}")
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
