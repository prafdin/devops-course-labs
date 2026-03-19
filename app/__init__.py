"""
This module builds shared parts for other modules.
"""

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

import json
import os
from pathlib import Path

from fastapi.templating import Jinja2Templates


# --------------------------------------------------------------------------------
# Read Configuration
# --------------------------------------------------------------------------------

with open('config.json') as config_json:
  config = json.load(config_json)
  users = config['users']
  db_path = config['db_path']

with open('config.json') as config_json:
  config = json.load(config_json)
  users = config['users']
  db_path = config['db_path']
  
def get_deploy_ref_from_file():
    deploy_file = Path("/home/mappy/Desktop/catty-reminders-app/.env.deploy")
    if deploy_file.exists():
        try:
            with open(deploy_file) as f:
                for line in f:
                    if line.startswith("DEPLOY_REF="):
                        return line.strip().split("=")[1]
        except:
            return "NA"
    return "NA"

DEPLOY_REF = get_deploy_ref_from_file()

# --------------------------------------------------------------------------------
# Establish the Secret Key
# --------------------------------------------------------------------------------

secret_key = config['secret_key']


# --------------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------------

templates = Jinja2Templates(directory="templates")
