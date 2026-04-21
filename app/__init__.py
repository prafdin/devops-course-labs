"""
This module builds shared parts for other modules.
"""

import json
import os

from fastapi.templating import Jinja2Templates

# --------------------------------------------------------------------------------
# Read Configuration
# --------------------------------------------------------------------------------

with open('config.json') as config_json:
  config = json.load(config_json)
  users = config['users']
  db_config = config['db_config']

# Позволяем переопределить хост БД через переменную окружения
if os.getenv("DB_HOST"):
  db_config["host"] = os.getenv("DB_HOST", db_config["host"])

DEPLOY_REF = os.getenv("DEPLOY_REF", "NA")

# --------------------------------------------------------------------------------
# Establish the Secret Key
# --------------------------------------------------------------------------------

secret_key = config['secret_key']

# --------------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------------

templates = Jinja2Templates(directory="templates")