"""
This module builds shared parts for other modules.
"""

import json
import os
import subprocess
from fastapi.templating import Jinja2Templates

# Читаем конфигурацию
with open('/opt/catty-reminders/config.json') as config_json:
    config = json.load(config_json)
    users = config['users']
    db_path = config['db_path']

# DEPLOY_REF - читаем из файла, который обновляет CD
try:
    with open('/opt/catty-reminders/deploy_ref.txt', 'r') as f:
        DEPLOY_REF = f.read().strip()
except:
    DEPLOY_REF = "NA"

# Секретный ключ
secret_key = config['secret_key']

# Шаблоны
templates = Jinja2Templates(directory="/opt/catty-reminders/templates")
