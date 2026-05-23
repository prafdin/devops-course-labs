import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("=== Webhook received! Starting deploy.sh ===")
        try:
            # Запускаем наш скрипт деплоя
            process = subprocess.Popen(["/home/alexander/deploy.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            print("Deploy Script Output:\n", stdout.decode())
            
            if process.returncode == 0:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Deployment successful!")
            else:
                print("Deploy Script Error:\n", stderr.decode())
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Deployment failed during build/test")
        except Exception as e:
            print("Error executing deploy.sh:", str(e))
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

    def do_GET(self):
        # Для проверок работоспособности (ping)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"ok")

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), WebhookHandler)
    print("Webhook listener running on port 8080...")
    server.serve_forever()
