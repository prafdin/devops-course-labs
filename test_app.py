#!/usr/bin/env python3
import unittest
import os
import sys

# Добавляем путь к папке с приложением
APP_DIR = "/opt/catty-reminders-app"

class TestApp(unittest.TestCase):
    
    def test_main_exists(self):
        """Проверка, что файл main.py существует"""
        self.assertTrue(os.path.exists(f'{APP_DIR}/app/main.py'), 
                       "app/main.py не найден")
    
    def test_webhook_exists(self):
        """Проверка, что webhook_server.py существует"""
        self.assertTrue(os.path.exists(f'{APP_DIR}/webhook_server.py'), 
                       "webhook_server.py не найден")
    
    def test_requirements_exists(self):
        """Проверка, что requirements.txt существует"""
        self.assertTrue(os.path.exists(f'{APP_DIR}/requirements.txt'), 
                       "requirements.txt не найден")
    
    def test_python_syntax_main(self):
        """Проверка синтаксиса app/main.py"""
        try:
            with open(f'{APP_DIR}/app/main.py', 'r') as f:
                compile(f.read(), 'app/main.py', 'exec')
        except SyntaxError as e:
            self.fail(f"Синтаксическая ошибка в app/main.py: {e}")
    
    def test_python_syntax_webhook(self):
        """Проверка синтаксиса webhook_server.py"""
        try:
            with open(f'{APP_DIR}/webhook_server.py', 'r') as f:
                compile(f.read(), 'webhook_server.py', 'exec')
        except SyntaxError as e:
            self.fail(f"Синтаксическая ошибка в webhook_server.py: {e}")

if __name__ == '__main__':
    unittest.main()
