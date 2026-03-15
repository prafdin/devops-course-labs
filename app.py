#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import datetime

class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = f"""
        <html>
        <head><title>DevOps Demo</title></head>
        <body style="font-family:Arial; max-width:600px; margin:50px auto; padding:20px;">
            <h1>🚀 Привет!</h1>
            <p>Это моё приложение на порту 8181</p>
            <p><b>Версия:</b> 1.15</p>
            <p><b>Обновлено:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Работает через frp: app.shtengauer.course.prafdin.ru</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        # Тихий лог, чтобы не спамить в консоль
        pass

if __name__ == '__main__':
    print(f"🚀 App started on port 8181")
    HTTPServer(('0.0.0.0', 8181), AppHandler).serve_forever()
EOF
