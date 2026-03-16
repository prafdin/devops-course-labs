#!/usr/bin/env python3
"""
Webhook handler for catty-reminders-app
Automatic deployment on push events
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os
import threading
import logging
import datetime
import signal
import sys
import getpass

# Configuration
REPO_URL = "git@github.com:TimurMif/catty-reminders-app.git"
APP_DIR = "/opt/catty-reminders"
VENV_DIR = os.path.join(APP_DIR, "venv")
LOG_FILE = "/var/log/webhook/webhook.log"
DEPLOY_LOG = "/var/log/webhook/deployments.log"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        """Handle POST requests from GitHub"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode('utf-8'))
            event = self.headers.get('X-GitHub-Event', 'unknown')
            logging.info(f"Received {event} event")

            # Check if it's a push event
            if event == 'push':
                branch = payload.get('ref', '').replace('refs/heads/', '')
                logging.info(f"Push event detected for branch: {branch}")

                # Get commit info
                commits = payload.get('commits', [])
                if commits:
                    last_commit = commits[-1]
                    commit_msg = last_commit.get('message', '')
                    committer = last_commit.get('committer', {}).get('name', '')
                    logging.info(f"Commit: {commit_msg} by {committer}")

                # Run deployment in background thread
                thread = threading.Thread(target=self.deploy_app, args=(branch,))
                thread.start()

                # Send immediate response
                self.send_response(202)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "accepted",
                    "message": f"Deployment started for branch {branch}"
                }).encode())
            else:
                # Ignore other events
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ignored"}).encode())

        except json.JSONDecodeError:
            logging.error("Invalid JSON payload")
            self.send_response(400)
            self.end_headers()
        except Exception as e:
            logging.error(f"Error processing webhook: {str(e)}")
            self.send_response(500)
            self.end_headers()

    def deploy_app(self, branch):
        """Deploy the application"""
        try:
            logging.info(f"Starting deployment for branch: {branch}")

            # Create a lock file to prevent concurrent deployments
            lock_file = "/tmp/deploy.lock"
            if os.path.exists(lock_file):
                logging.warning("Deployment already in progress, skipping...")
                return

            # Create lock
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))

            # Clone or update repository
            if not os.path.exists(os.path.join(APP_DIR, '.git')):
                logging.info("Cloning repository...")
                result = subprocess.run([
                    "git", "clone", REPO_URL, APP_DIR
                ], check=True, capture_output=True, text=True)
                logging.info(f"Clone output: {result.stdout}")

            # Update code
            logging.info(f"Updating code for branch: {branch}")
            os.chdir(APP_DIR)

            logging.info(f"Git operations running as user: {getpass.getuser()}")

            # Fetch all branches and reset
            result = subprocess.run([
                "git", "fetch", "--all"
            ], check=True, capture_output=True, text=True)
            logging.info(f"Fetch output: {result.stdout}")

            # Reset to the specific branch
            result = subprocess.run([
                "git", "reset", "--hard", f"origin/{branch}"
            ], check=True, capture_output=True, text=True)
            logging.info(f"Reset output: {result.stdout}")

            try:
                sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=APP_DIR, text=True).strip()
                with open(os.path.join(APP_DIR, ".deploy_ref"), "w") as f:
                    f.write(f"DEPLOY_REF={sha}\n")
                logging.info(f"Updated deploy ref: {sha}")
            except Exception as e:
                logging.error(f"Failed to write deploy ref: {e}")
            # Install dependencies using virtual environment
            requirements_file = os.path.join(APP_DIR, "requirements.txt")
            if os.path.exists(requirements_file):
                logging.info("Installing Python dependencies...")
                pip_path = os.path.join(VENV_DIR, "bin", "pip")
                if os.path.exists(pip_path):
                    result = subprocess.run([
                        pip_path, "install", "-r", requirements_file
                    ], check=True, capture_output=True, text=True)
                    logging.info(f"Pip install output: {result.stdout}")
                else:
                    logging.error(f"Virtual environment pip not found at {pip_path}")

            # Restart the application service
            logging.info("Restarting application service...")
            result = subprocess.run([
                "sudo", "systemctl", "restart", "catty-reminders"
            ], check=True, capture_output=True, text=True)

            # Log successful deployment
            with open(DEPLOY_LOG, 'a') as f:
                f.write(f"{datetime.datetime.now()} - Deployed branch {branch} successfully\n")

            logging.info(f"Deployment completed successfully for branch: {branch}")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logging.error(f"Deployment failed: {error_msg}")
            with open(DEPLOY_LOG, 'a') as f:
                f.write(f"{datetime.datetime.now()} - Deploy failed for branch {branch}: {error_msg}\n")
        except Exception as e:
            logging.error(f"Unexpected error during deployment: {str(e)}")
        finally:
            # Remove lock file
            if os.path.exists(lock_file):
                os.remove(lock_file)

    def log_message(self, format, *args):
        logging.info(f"{self.address_string()} - {format % args}")

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    logging.info(f"Starting webhook server on port {port}")
    print(f"Webhook server running on port {port}")
    print(f"Press Ctrl+C to stop")

    def signal_handler(sig, frame):
        print("\nShutting down server...")
        httpd.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
