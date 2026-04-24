#!/usr/bin/env python3

import tempfile
import subprocess
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080

APP_DIR = "/home/mzpdqk/devops/catty-reminders-app"
TEST_SCRIPT = f"{APP_DIR}/webhook/test.sh"
DEPLOY_SCRIPT = f"{APP_DIR}/webhook/deploy.sh"


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
            print("error:", e)
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"webhook running")

    def process_webhook(self, payload):
        event = self.headers.get('X-GitHub-Event', '')
        branch = payload.get('ref', '').replace('refs/heads/', '')
        repo = payload.get('repository', {}).get('full_name', '')

        print("\n=== webhook ===")
        print("time:", datetime.now())
        print("event:", event)
        print("repo:", repo)
        print("branch:", branch)

        if event != "push":
            print("skip: not push event")
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            clone_url = payload.get('repository', {}).get('clone_url')

            subprocess.run(["git", "clone", clone_url, tmpdir], check=True)
            subprocess.run(["git", "checkout", branch], cwd=tmpdir, check=True)

            print("run tests...")

            try:
                result = subprocess.run(
                    [TEST_SCRIPT, branch],
                    cwd=tmpdir,
                    check=True,
                    capture_output=True,
                    text=True
                )

                print("tests passed")
                print(result.stdout)

                print("deploy...")
                subprocess.run(
                    [DEPLOY_SCRIPT, branch],
                    cwd=tmpdir,
                    check=True
                )

                print("deploy done")

            except subprocess.CalledProcessError as e:
                print("tests failed, deploy skipped")
                print(e.stdout)
                print(e.stderr)


def main():
    print("Webhook server started on port", PORT)
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
