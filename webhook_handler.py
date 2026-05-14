import http.server
import subprocess

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        subprocess.Popen(["/home/enjoyer/deploy.sh"])
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deploy started")

if __name__ == "__main__":
    server = http.server.HTTPServer(('0.0.0.0', 8080), WebhookHandler)
    print("Webhook handler started on port 8080...")
    server.serve_forever()
