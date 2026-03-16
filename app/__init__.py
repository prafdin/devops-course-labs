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

# DEPLOY_REF - хэш текущего коммита
try:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd="/opt/catty-reminders",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=2
    )
    if result.returncode == 0:
        DEPLOY_REF = result.stdout.strip()
    else:
        DEPLOY_REF = "NA"
except:
    DEPLOY_REF = "NA"

# Секретный ключ
secret_key = config['secret_key']

# Шаблоны
templates = Jinja2Templates(directory="/opt/catty-reminders/templates")
