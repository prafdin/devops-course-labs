import os
import subprocess
import logging
from flask import Flask, request, abort

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("webhook-handler")

app = Flask(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DEPLOY_SCRIPT = os.path.join(PROJECT_DIR, "deploy.sh")

@app.route('/', methods=['POST'])
def webhook():
    logger.info("--- Incoming Webhook Request ---")
    
    payload = request.json
    if payload is None:
        logger.warning("Payload error: No JSON received.")
        abort(400)

    ref = payload.get('ref', '')
    branch = ref.split('/')[-1] if ref else "lab1"
    
    logger.info(f"Action: Push detected for branch '{branch}'")

    if not os.path.exists(DEPLOY_SCRIPT):
        logger.error(f"Execution error: {DEPLOY_SCRIPT} not found.")
        return "Deploy script missing", 500

    try:
        logger.info(f"Triggering background deployment for: {branch}")
        subprocess.Popen(['/bin/bash', DEPLOY_SCRIPT, branch], cwd=PROJECT_DIR)
        return f"Deployment for {branch} initiated.", 200
    except Exception as e:
        logger.error(f"System error: {str(e)}")
        return "Internal Error", 500

if __name__ == '__main__':
    logger.info("Webhook server starting on port 8080...")
    app.run(host='0.0.0.0', port=8080)
