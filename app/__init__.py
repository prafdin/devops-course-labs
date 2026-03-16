"""
This module builds shared parts for other modules.
"""

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

import json
import os

from fastapi.templating import Jinja2Templates


# --------------------------------------------------------------------------------
# Read Configuration
# --------------------------------------------------------------------------------

with open('config.json') as config_json:
  config = json.load(config_json)
  users = config['users']
  db_path = config['db_path']

# Функция для получения времени последнего деплоя
import datetime
import os

def get_deploy_ref():
    """Возвращает время последнего обновления или NA"""
    deploy_time_file = '/opt/catty-reminders/deploy_time.txt'
    try:
        with open(deploy_time_file, 'r') as f:
            return f.read().strip()
    except:
        return "NA"

# --------------------------------------------------------------------------------
# Establish the Secret Key
# --------------------------------------------------------------------------------

secret_key = config['secret_key']


# --------------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------------

templates = Jinja2Templates(directory="templates")
