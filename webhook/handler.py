from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import os

PORT = 8080
DEPLOY_SCRIPT = "/home/anzorcode/webhook/deploy.sh"

class WebhookHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Webhook server is running. Send POST requests to trigger deployment.")
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        event_type = self.headers.get('X-GitHub-Event', '')
        
        print(f"Received {event_type} event")
        
        if event_type == 'ping':
            print("  -> Ping from GitHub")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'pong')
            return
        
        if event_type == 'push':
            try:
                data = json.loads(body.decode('utf-8'))
                ref = data.get('ref', '')
                branch = ref.replace('refs/heads/', '')
                print(f"  -> Push event for branch: {branch}")
                
                subprocess.Popen([DEPLOY_SCRIPT, branch])
                
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Deployment started')
            except Exception as e:
                print(f"  -> Error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'Internal error')
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')

def run():
    print(f"Starting webhook server on port {PORT}")
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == '__main__':
    run()
