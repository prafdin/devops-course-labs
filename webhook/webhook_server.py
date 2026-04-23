#!/usr/bin/env python3

import tempfile
import subprocess
import os
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

PORT = 8080
APP_DIR = os.path.expanduser("~/devops-lab/app")
SERVICE_NAME = "devops-app"

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
            print("Ошибка парсинга JSON")
            self.send_response(400)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Webhook Server Running</h1>')

    def _process_webhook(self, payload):
        event_type = self.headers.get('X-GitHub-Event', 'unknown')
        print(f"\nПолучено событие: {event_type}")
        if event_type == 'push':
            self._handle_push_event(payload)

    def _handle_push_event(self, payload):
        branch = payload.get('ref', '').replace('refs/heads/', '')
        clone_url = payload.get('repository', {}).get('clone_url', 'unknown')
        print(f"Push в ветку: {branch}")

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                subprocess.run(["git", "clone", clone_url, tmpdir], check=True, capture_output=True)
                subprocess.run(["git", "checkout", branch], cwd=tmpdir, check=True, capture_output=True)
                
                result = subprocess.run(["./test.sh"], cwd=tmpdir, capture_output=True, text=True)
                if result.returncode == 0:
                    print("Тесты пройдены, обновляем приложение")
                    if os.path.exists(os.path.join(APP_DIR, '.git')):
                        subprocess.run(["git", "-C", APP_DIR, "pull"], check=True, capture_output=True)
                    else:
                        subprocess.run(["git", "clone", clone_url, APP_DIR], check=True, capture_output=True)
                    
                    if os.path.exists(os.path.join(APP_DIR, "requirements.txt")):
                        subprocess.run(["pip3", "install", "-r", "requirements.txt"], cwd=APP_DIR, check=True, capture_output=True)
                    
                    subprocess.run(["sudo", "systemctl", "restart", SERVICE_NAME], check=True, capture_output=True)
                    print("Приложение перезапущено")
                else:
                    print("Тесты не пройдены")
            except Exception as e:
                print(f"Ошибка: {e}")

def main():
    print(f"Webhook сервер на порту {PORT}")
    HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()

if __name__ == '__main__':
    main()
