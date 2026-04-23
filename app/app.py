#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import json
import subprocess
import os

PORT = 8181

class AppHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Получаем последний коммит
            commit_hash = "unknown"
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=os.path.dirname(__file__),
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    commit_hash = result.stdout.strip()
            except:
                pass
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>DevOps App</title></head>
            <body>
                <h1>DevOps App</h1>
                <p>Time: {datetime.now()}</p>
                <p>Commit: {commit_hash}</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def main():
    server = HTTPServer(('0.0.0.0', PORT), AppHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
