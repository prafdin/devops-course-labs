import subprocess
import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080

BASE_DIR = "/mnt/c/Users/Sergo/Documents/prog/university/catty-reminders-app"

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
            try:
                self.wfile.write(b'{"status": "success"}')
            except BrokenPipeError:
                pass 
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.send_response(500)
            self.end_headers()

    def _process_webhook(self, payload):
        event_type = self.headers.get('X-GitHub-Event', 'unknown')
        if event_type == 'push':
            branch = payload.get('ref', '').replace('refs/heads/', '')
            sha = payload.get('after')
            print(f"\n🔔 Push в {branch}, SHA: {sha}")
            
            try:
                # 1. ТЕСТЫ
                print("🚀 Запуск тестов...")
                subprocess.run(["bash", f"{BASE_DIR}/deploy/test.sh", branch], check=True)
                print("✅ Тесты пройдены!")

                # 2. ДЕПЛОЙ
                print("🚀 Запуск деплоя...")
                subprocess.run(["bash", f"{BASE_DIR}/deploy/deploy.sh", branch, sha], check=True)
                print("✅ Деплой завершен!")

            except subprocess.CalledProcessError:
                print("❌ Ошибка в скриптах! Проверь логи.")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Server is running")

if __name__ == '__main__':
    print(f"📡 Сервер на порту {PORT}...")
    HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()