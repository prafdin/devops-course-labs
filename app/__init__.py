"""
This module builds shared parts for other modules.
"""

import json
import os
from fastapi.templating import Jinja2Templates

# Определяем базовую директорию
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Читаем конфигурацию
config_path = os.path.join(BASE_DIR, 'config.json')
with open(config_path) as config_json:
    config = json.load(config_json)
    users = config['users']
    db_path = config['db_path']

# DEPLOY_REF - читаем из файла, который обновляет CD
deploy_ref_path = '/opt/catty-reminders/deploy_ref.txt'
try:
    with open(deploy_ref_path, 'r') as f:
        DEPLOY_REF = f.read().strip()
except:
    DEPLOY_REF = "NA"

# Секретный ключ
secret_key = config['secret_key']

# Шаблоны - используем относительный путь
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)
