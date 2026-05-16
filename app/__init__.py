"""This module builds shared parts for other modules."""

import json
import os
from fastapi.templating import Jinja2Templates

# Read Configuration
with open('config.json') as config_json:
    config = json.load(config_json)
    users = config.get('users', {})
    db_config = config.get('db_config', {})
    secret_key = config.get('secret_key', 'default-secret-key')

DEPLOY_REF = os.getenv("DEPLOY_REF", "NA")

# Templates
templates = Jinja2Templates(directory="templates")
