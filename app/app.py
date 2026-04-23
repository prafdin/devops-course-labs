#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import json

PORT = 8181

class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'<h1>DevOps App</h1><p>{datetime.now()}</p>'.encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)

def main():
    HTTPServer(('0.0.0.0', PORT), AppHandler).serve_forever()

if __name__ == '__main__':
    main()
