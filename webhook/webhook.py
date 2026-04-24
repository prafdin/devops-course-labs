#!/usr/bin/env python3

import subprocess
import json
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
            <p>Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

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

        print("   🧪 Running tests...")
        subprocess.run([TEST_SCRIPT, branch], check=True)
        print("   ✅ Tests passed")

        print("   🚀 Deploying...")
        subprocess.run([DEPLOY_SCRIPT, branch], check=True)
        print("   ✅ Deploy complete")


if __name__ == '__main__':
    print(f"🚀 Webhook server started")
    print(f"📡 Port: {PORT}")
    print(f"📁 Workspace: {WORKSPACE}")
    print(f"\n👉 Press Ctrl+C to stop\n")

    try:
        HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
