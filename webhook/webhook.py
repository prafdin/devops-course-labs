#!/usr/bin/env python3

import subprocess
import json
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
WORKSPACE = "/home/ubuntu/devops/catty-reminders-app"
TEST_SCRIPT = f"{WORKSPACE}/webhook/test.sh"
DEPLOY_SCRIPT = f"{WORKSPACE}/webhook/deploy.sh"

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length)

        try:
            data = json.loads(raw.decode('utf-8'))
            event = self.headers.get('X-GitHub-Event', '')

            if event == 'push':
                self._handle_push(data)
            else:
                print(f"📡 Unhandled event: {event}")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')

        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f'{{"status": "error", "message": "{str(e)}"}}'.encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"""
        <html>
        <body style="font-family: monospace; padding: 20px;">
            <h2>Webhook Listener</h2>
            <p>Status: <b>running</b></p>
            <p>Port: {PORT}</p>
            <p>Workspace: {WORKSPACE}</p>
            <p>Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <h3>Service Status:</h3>
            <pre>App Service: {'Active' if self._check_service() else 'Inactive'}</pre>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def _check_service(self):
        try:
            result = subprocess.run(['systemctl', 'is-active', 'app.service'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def _handle_push(self, data):
        branch = data.get('ref', '').replace('refs/heads/', '')
        commit = data.get('after')
        author = data.get('pusher', {}).get('name', 'unknown')
        commits_count = len(data.get('commits', []))

        print(f"\n🔔 Push received:")
        print(f"   🌿 Branch: {branch}")
        print(f"   🧑 Author: {author}")
        print(f"   📦 Commits: {commits_count}")
        print(f"   🆔 Commit: {commit}")

        if not commit:
            print("   ⚠️ No commit SHA, skipping")
            return

        # Запускаем тесты
        print("   🧪 Running tests...")
        try:
            result = subprocess.run([TEST_SCRIPT, branch], check=True, 
                                  capture_output=True, text=True, timeout=300)
            print(f"   📤 Test output:\n{result.stdout[-500:]}")  # Последние 500 символов
            print("   ✅ Tests passed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Tests failed with code {e.returncode}")
            print(f"   📤 Output:\n{e.stdout[-500:] if e.stdout else 'No output'}")
            print(f"   📤 Error:\n{e.stderr[-500:] if e.stderr else 'No error'}")
            raise  # Re-raise to trigger the exception handler
        except subprocess.TimeoutExpired:
            print("   ❌ Tests timeout after 300 seconds")
            raise

        # Деплоим
        print("   🚀 Deploying...")
        try:
            result = subprocess.run([DEPLOY_SCRIPT, branch], check=True,
                                  capture_output=True, text=True, timeout=120)
            print(f"   📤 Deploy output:\n{result.stdout[-500:]}")
            print("   ✅ Deploy complete")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Deploy failed with code {e.returncode}")
            print(f"   📤 Output:\n{e.stdout[-500:] if e.stdout else 'No output'}")
            print(f"   📤 Error:\n{e.stderr[-500:] if e.stderr else 'No error'}")
            raise
        except subprocess.TimeoutExpired:
            print("   ❌ Deploy timeout after 120 seconds")
            raise


if __name__ == '__main__':
    print(f"🚀 Webhook server started")
    print(f"📡 Port: {PORT}")
    print(f"📁 Workspace: {WORKSPACE}")
    print(f"🔧 Test script: {TEST_SCRIPT}")
    print(f"🚀 Deploy script: {DEPLOY_SCRIPT}")
    print(f"\n👉 Press Ctrl+C to stop\n")

    try:
        HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
