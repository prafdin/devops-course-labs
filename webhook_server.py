#!/usr/bin/env python3
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

APP_DIR = "/opt/catty-reminders-app"

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/webhook':
            print("Получен webhook запрос от GitHub!")
            
            # 1. Обновляем код
            print("  → Обновление кода из репозитория...")
            subprocess.run(["git", "-C", APP_DIR, "pull"], check=False)
            
            # 2. Устанавливаем зависимости
            print("  → Установка зависимостей...")
            subprocess.run(["pip3", "install", "-r", f"{APP_DIR}/requirements.txt"], check=False)
            
            # 3. Запускаем тесты
            print("  → Запуск тестов...")
            result = subprocess.run(["python3", f"{APP_DIR}/test_app.py"], capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                print("  ❌ ТЕСТЫ НЕ ПРОШЛИ! Деплой остановлен.")
                print(result.stderr)
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'Tests failed')
                return
            
            print("  ✅ Тесты прошли успешно!")
            
            # 4. Перезапускаем приложение
            print("  → Перезапуск приложения...")
            subprocess.run(["sudo", "systemctl", "restart", "catty-app"], check=False)
            
            print("✅ Webhook обработан успешно!")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    print("Запуск webhook сервера на порту 8080")
    server = HTTPServer(('', 8080), WebhookHandler)
    server.serve_forever()
