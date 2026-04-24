#!/usr/bin/env python3

import tempfile
import subprocess
import json
import os
import shutil
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080

# Автоматическое определение путей
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
TEST_SCRIPT = os.path.join(SCRIPT_DIR, "test.sh")
DEPLOY_SCRIPT = os.path.join(SCRIPT_DIR, "deploy.sh")

# Для отладки - выводим пути при запуске
print(f"=== Webhook Configuration ===")
print(f"SCRIPT_DIR: {SCRIPT_DIR}")
print(f"APP_DIR: {APP_DIR}")
print(f"TEST_SCRIPT: {TEST_SCRIPT}")
print(f"TEST_SCRIPT exists: {os.path.exists(TEST_SCRIPT)}")
print(f"TEST_SCRIPT executable: {os.access(TEST_SCRIPT, os.X_OK)}")
print(f"DEPLOY_SCRIPT: {DEPLOY_SCRIPT}")
print(f"DEPLOY_SCRIPT exists: {os.path.exists(DEPLOY_SCRIPT)}")
print(f"DEPLOY_SCRIPT executable: {os.access(DEPLOY_SCRIPT, os.X_OK)}")
print(f"=============================\n")


class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode('utf-8'))
            self.process_webhook(payload)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')

        except Exception as e:
            print(f"Error processing webhook: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"status": "error"}')

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Webhook Server</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .status {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>🚀 Webhook Server</h1>
            <p class="status">✅ Server is running</p>
            <p>Port: {PORT}</p>
            <p>Time: {datetime.now()}</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

    def process_webhook(self, payload):
        event = self.headers.get('X-GitHub-Event', '')
        branch = payload.get('ref', '').replace('refs/heads/', '')
        repo = payload.get('repository', {}).get('full_name', '')
        clone_url = payload.get('repository', {}).get('clone_url')

        print("\n" + "="*50)
        print("=== WEBHOOK RECEIVED ===")
        print(f"Time: {datetime.now()}")
        print(f"Event: {event}")
        print(f"Repository: {repo}")
        print(f"Branch: {branch}")
        print(f"Clone URL: {clone_url}")
        print("="*50)

        # Проверяем что это push событие
        if event != "push":
            print(f"ℹ️  Skipping event: {event} (not a push event)")
            return

        # Проверяем существование скриптов
        if not os.path.exists(TEST_SCRIPT):
            print(f"❌ ERROR: test.sh not found at {TEST_SCRIPT}")
            return
        
        if not os.path.exists(DEPLOY_SCRIPT):
            print(f"❌ ERROR: deploy.sh not found at {DEPLOY_SCRIPT}")
            return

        # Проверяем права на выполнение
        if not os.access(TEST_SCRIPT, os.X_OK):
            print(f"⚠️  test.sh is not executable, fixing...")
            os.chmod(TEST_SCRIPT, 0o755)
        
        if not os.access(DEPLOY_SCRIPT, os.X_OK):
            print(f"⚠️  deploy.sh is not executable, fixing...")
            os.chmod(DEPLOY_SCRIPT, 0o755)

        # Создаем временную директорию
        tmpdir = tempfile.mkdtemp()
        print(f"📁 Temporary directory: {tmpdir}")

        try:
            # Клонируем репозиторий
            print(f"📦 Cloning repository...")
            result = subprocess.run(
                ["git", "clone", clone_url, tmpdir],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Clone failed: {result.stderr}")
                return
            print(f"✅ Clone successful")

            # Переключаемся на нужную ветку
            print(f"🌿 Checking out branch: {branch}")
            result = subprocess.run(
                ["git", "checkout", branch],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Checkout failed: {result.stderr}")
                return
            print(f"✅ Checkout successful")

            # Запускаем тесты
            print(f"\n🧪 Running tests...")
            print("-" * 40)
            try:
                result = subprocess.run(
                    [TEST_SCRIPT, branch],
                    cwd=tmpdir,
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"✅ TESTS PASSED!")
                if result.stdout:
                    print(f"Test output:\n{result.stdout}")
                
                # Запускаем деплой
                print(f"\n🚀 Deploying...")
                print("-" * 40)
                result = subprocess.run(
                    [DEPLOY_SCRIPT, branch],
                    cwd=tmpdir,
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"✅ DEPLOYMENT SUCCESSFUL!")
                if result.stdout:
                    print(f"Deploy output:\n{result.stdout}")

            except subprocess.CalledProcessError as e:
                print(f"❌ TESTS FAILED! Deployment skipped.")
                if e.stdout:
                    print(f"stdout: {e.stdout}")
                if e.stderr:
                    print(f"stderr: {e.stderr}")
                return

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        finally:
            # Очищаем временную директорию
            shutil.rmtree(tmpdir, ignore_errors=True)
            print(f"🗑️  Cleaned up temporary directory")
        
        print("\n✅ Webhook processing completed successfully!")


def main():
    print(f"\n{'='*50}")
    print(f"🚀 STARTING WEBHOOK SERVER")
    print(f"{'='*50}")
    print(f"Port: {PORT}")
    print(f"URL: http://0.0.0.0:{PORT}")
    print(f"Working directory: {os.getcwd()}")
    print(f"{'='*50}\n")
    
    # Проверяем что скрипты существуют и executable
    if not os.path.exists(TEST_SCRIPT):
        print(f"⚠️  WARNING: test.sh not found at {TEST_SCRIPT}")
        print(f"   Please create it with: touch {TEST_SCRIPT} && chmod +x {TEST_SCRIPT}")
    elif not os.access(TEST_SCRIPT, os.X_OK):
        print(f"⚠️  WARNING: test.sh is not executable")
        print(f"   Run: chmod +x {TEST_SCRIPT}")
    
    if not os.path.exists(DEPLOY_SCRIPT):
        print(f"⚠️  WARNING: deploy.sh not found at {DEPLOY_SCRIPT}")
        print(f"   Please create it with: touch {DEPLOY_SCRIPT} && chmod +x {DEPLOY_SCRIPT}")
    elif not os.access(DEPLOY_SCRIPT, os.X_OK):
        print(f"⚠️  WARNING: deploy.sh is not executable")
        print(f"   Run: chmod +x {DEPLOY_SCRIPT}")
    
    print(f"\n👂 Listening for webhook events...")
    print(f"💡 Press Ctrl+C to stop\n")
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n\n🛑 Server stopped by user")
        server.server_close()


if __name__ == '__main__':
    main()
