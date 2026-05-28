#!/usr/bin/env python3
import os
import json
import subprocess
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080


APP_DIR = os.path.dirname(os.path.abspath(__file__))


class WebhookHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Webhook server works")

    def do_POST(self):

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:

            payload = json.loads(body.decode())

            event_type = self.headers.get("X-GitHub-Event", "")

            print("\n======================")
            print(f"Time: {datetime.now()}")
            print(f"Event: {event_type}")

            if event_type == "push":

                print("Deploy started")

                subprocess.run(
                    ["bash", "deploy.sh"],
                    cwd=APP_DIR,
                    check=True
                )

                print("Deploy completed")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as e:

            print(e)

            self.send_response(500)
            self.end_headers()


def main():

    print(f"Webhook server started on port {PORT}")

    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)

    server.serve_forever()


if __name__ == "__main__":
    main()
