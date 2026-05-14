import os
import json
import subprocess
from fastapi.templating import Jinja2Templates

with open('config.json') as config_json:
    config = json.load(config_json)
    users = config['users']
    db_path = config['db_path']

DEPLOY_REF = os.getenv("DEPLOY_REF", "NA")

secret_key = config['secret_key']
templates = Jinja2Templates(directory="templates")

DEPLOY_REF = os.getenv("DEPLOY_REF", "NA")
    if DEPLOY_REF != "NA":
        return DEPLOY_REF
    try:
            ['git', 'rev-parse', '--short', 'HEAD'], 
            cwd=os.path.dirname(os.path.abspath(__file__))
        ).decode('ascii').strip()
    except Exception:
        return "NA"
