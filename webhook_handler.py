import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # GitHub прислал пуш!
        print("Webhook received! Updating project...")
        
        # Выполняем системные команды
        os.system("cd ~/my_project && git pull")
        os.system("sudo systemctl restart my_app.service") # Перезапуск приложения
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deployed!")

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), WebhookHandler)
    print("Handler started on port 8080...")
    server.serve_forever()
