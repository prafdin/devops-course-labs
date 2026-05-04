"""
This module builds shared parts for other modules.
"""

import json
import os
import subprocess
from fastapi.templating import Jinja2Templates

# Определяем базовую директорию (где находится текущий файл)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Путь к config.json (лежит в корне проекта)
config_path = os.path.join(BASE_DIR, 'config.json')

# Читаем конфигурацию
with open(config_path) as config_json:
    config = json.load(config_json)
    users = config['users']
    db_path = config['db_path']

# DEPLOY_REF - читаем из файла, если он есть
deploy_ref_path = os.path.join(BASE_DIR, 'deploy_ref.txt')
try:
    with open(deploy_ref_path, 'r') as f:
        DEPLOY_REF = f.read().strip()
except:
    DEPLOY_REF = "NA"

# Секретный ключ
secret_key = config['secret_key']

# Путь к шаблонам
templates_dir = os.path.join(BASE_DIR, 'templates')
templates = Jinja2Templates(directory=templates_dir)
