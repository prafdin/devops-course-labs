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
  db_config = config['db_config']
  password_file = db_config.pop('password_file', None)
  if password_file and os.path.exists(password_file):
    with open(password_file) as db_password:
      db_config['password'] = db_password.read().strip()

DEPLOY_REF = os.getenv("DEPLOY_REF", "NA")

# --------------------------------------------------------------------------------
# Establish the Secret Key
# --------------------------------------------------------------------------------

secret_key = config['secret_key']


# --------------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------------

templates = Jinja2Templates(directory="templates")
