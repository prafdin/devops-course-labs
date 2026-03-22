#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

PORT = 8181

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
