#!/usr/bin/env python3
"""
Webhook server for automatic deployment of Catty Reminders
"""

import subprocess
import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
REPO_PATH = '/home/yaroslav/devops-lab/catty-reminders-app'

class WebhookHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            if content_length == 0:
                self.send_response(200)
                self.end_headers()
                return
            payload = json.loads(body.decode('utf-8'))
            
            event_type = self.headers.get('X-GitHub-Event', 'unknown')
            repo_name = payload.get('repository', {}).get('full_name', 'unknown')
            branch = payload.get('ref', '').replace('refs/heads/', '')
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] Webhook: {event_type} - {repo_name} - {branch}")
            
            if event_type == 'push':
                self._deploy(branch)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = f"""
        <h1>Webhook Server Active</h1>
        <p>Time: {datetime.now()}</p>
        <p>Port: {PORT}</p>
        <p>App: Catty Reminders</p>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def _deploy(self, branch):
        print(f"   Deploy branch: {branch}")
        
        print(f"   Stopping app...")
        subprocess.run(['sudo', 'systemctl', 'stop', 'catty-app'], capture_output=True)
        
        time.sleep(3)
        
        print(f"   Updating code...")
        subprocess.run(['git', 'fetch', '--all'], cwd=REPO_PATH, capture_output=True)
        subprocess.run(['git', 'checkout', branch], cwd=REPO_PATH, capture_output=True)
        subprocess.run(['git', 'pull', 'origin', branch], cwd=REPO_PATH, capture_output=True)
        
        print(f"   Starting app...")
        subprocess.run(['sudo', 'systemctl', 'start', 'catty-app'], capture_output=True)
        
        print(f"   Deploy completed!")
    
    def log_message(self, format, *args):
        pass

def main():
    print(f"Starting Webhook Server on port {PORT}")
    print(f"Repository: {REPO_PATH}")
    print(f"Time: {datetime.now()}")
    print(f"\nWaiting for webhook...\n")
    
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\nServer stopped")

if __name__ == '__main__':
    main()
