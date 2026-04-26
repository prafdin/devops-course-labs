#!/usr/bin/env python3
import json, subprocess, os, sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler


PORT = 8080
BASE_DIR = "/home/qzm/Desktop/catty-reminders-app"


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body.decode('utf-8'))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "accepted"}')
            
            self._process_webhook(payload)
        except Exception as e:
            print(f"Ошибка обработки: {e}")
            self.send_response(400)
            self.end_headers()


    def _process_webhook(self, payload):
        event_type = self.headers.get('X-GitHub-Event', 'unknown')
        if event_type == 'push':
            branch = payload.get('ref', '').split('/')[-1]
            print(f"\n[{datetime.now()}] Получен PUSH в ветку: {branch}")
            self._run_pipeline(branch)


    def _run_pipeline(self, branch):
        print(f"Запуск тестов для {branch}...")
        try:
            subprocess.run([f"{BASE_DIR}/webhook/test.sh", branch], check=True)
            print("--> Тесты пройдены! Переходим к деплою.")
            
            subprocess.run([f"{BASE_DIR}/webhook/deploy.sh", branch], check=True)
            print("--> Деплой завершен.")
            
            subprocess.run([f"{BASE_DIR}/webhook/commit_status.sh", "success", "DevOps pipeline passed"], check=False)
        except subprocess.CalledProcessError:
            print("[X] Ошибка пайплайна!")
            subprocess.run([f"{BASE_DIR}/webhook/commit_status.sh", "failure", "Pipeline failed"], check=False)


if __name__ == '__main__':
    print(f"Запуск webhook listener на порту {PORT}")
    HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()


    