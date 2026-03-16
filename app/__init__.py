"""
This module builds shared parts for other modules.
"""

import json
import os
import datetime
from fastapi.templating import Jinja2Templates

# Читаем конфигурацию
with open('/opt/catty-reminders/config.json') as config_json:
    config = json.load(config_json)
    users = config['users']
    db_path = config['db_path']

# DEPLOY_REF - время последнего деплоя
DEPLOY_REF = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# Секретный ключ
secret_key = config['secret_key']

# Шаблоны
templates = Jinja2Templates(directory="/opt/catty-reminders/templates")
