#!/usr/bin/env python3
import subprocess
import os
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
REPO_DIR = "/home/yui1337/my_project"
DEPLOY_SCRIPT = f"{REPO_DIR}/deploy.sh"

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode('utf-8'))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "received"}')

            self._process_webhook(payload)

        except json.JSONDecodeError:
            print("❌ Error parsing JSON")
            self.send_response(400)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = f"<h1>🚀 Webhook Server is Running</h1><p>Time: {datetime.now()}</p><p>Port: {PORT}</p>"
        self.wfile.write(html.encode('utf-8'))

    def _process_webhook(self, payload):
        event_type = self.headers.get('X-GitHub-Event', 'unknown')
        
        if event_type == 'push':
            branch = payload.get('ref', '').replace('refs/heads/', '')
            pusher = payload.get('pusher', {}).get('name', 'unknown')
            
            print(f"\n🔔 Push: {branch} by {pusher}")
            self._run_deploy(branch)

def _run_deploy(self, branch):
        print(f"🚀 Running deploy for: {branch}...")
        try:
            result = subprocess.run(
                ["bash", DEPLOY_SCRIPT, branch],
                check=True,
                capture_output=True,
                text=True,
                stderr=subprocess.STDOUT
            )
            print("✅ Deploy success!")
            print(f"Output:\n{result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ DEPLOY FAILED!")
            print(f"Full Log:\n{e.stdout}")

def main():
    try:
        server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped")

if __name__ == '__main__':
    main()
