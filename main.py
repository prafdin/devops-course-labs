#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import subprocess

PORT = 8181
REPO_DIR = "/home/ct/catty-reminders-app"

def get_commit_sha():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()[:8]
    except:
        return "unknown"

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        commit_sha = get_commit_sha()
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Webhook Demo App</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>🚀 Webhook Demo Application</h1>
            <p>Приложение успешно развернуто через webhook!</p>
            <p>Время: {datetime.now()}</p>
            <p>Deploy ref: {commit_sha}</p>
        </body>
        </html>
        '''
        self.wfile.write(html.encode())

def main():
    print(f"Starting app on port {PORT}")
    server = HTTPServer(('0.0.0.0', PORT), SimpleHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
