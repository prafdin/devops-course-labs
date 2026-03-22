#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import os

PORT = 8181
ENV_FILE = "/home/ct/catty-reminders-app/.env.deploy"

def get_deploy_ref():
    try:
        with open(ENV_FILE, 'r') as f:
            for line in f:
                if line.startswith('DEPLOY_REF='):
                    return line.strip().split('=')[1][:8]
    except:
        pass
    return "unknown"

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        deploy_ref = get_deploy_ref()
        
        if self.path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<html><body>Login page</body></html>')
            return
        
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
            <p>Deploy ref: {deploy_ref}</p>
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
