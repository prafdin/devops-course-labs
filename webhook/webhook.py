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
import time

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

def branch_exists_on_origin(branch):
    """Check if branch exists on remote origin"""
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", branch],
            cwd=APP_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )
        return branch in result.stdout
    except Exception as e:
        logging.error(f"Error checking branch existence: {e}")
        return False

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        """Handle POST requests from GitHub"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode('utf-8'))
            event = self.headers.get('X-GitHub-Event', 'unknown')
            logging.info(f"Received {event} event")

            if event == 'push':
                branch = payload.get('ref', '').replace('refs/heads/', '')
                logging.info(f"Push event detected for branch: {branch}")

                commits = payload.get('commits', [])
                if commits:
                    last_commit = commits[-1]
                    commit_msg = last_commit.get('message', '')
                    committer = last_commit.get('committer', {}).get('name', '')
                    logging.info(f"Commit: {commit_msg} by {committer}")

                # Run deployment in background thread
                thread = threading.Thread(target=self.deploy_app, args=(branch,))
                thread.start()

                self.send_response(202)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "accepted",
                    "message": f"Deployment started for branch {branch}"
                }).encode())
            else:
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
        lock_file = "/tmp/deploy.lock"
        # Try to acquire lock
        lock_acquired = False
        for attempt in range(5):
            if not os.path.exists(lock_file):
                try:
                    with open(lock_file, 'w') as f:
                        f.write(str(os.getpid()))
                    lock_acquired = True
                    break
                except:
                    pass
            logging.warning(f"Deployment already in progress, waiting... (attempt {attempt+1}/5)")
            time.sleep(2)
        if not lock_acquired:
            logging.error("Could not acquire lock after 5 attempts, skipping deployment")
            return

        try:
            logging.info(f"Starting deployment for branch: {branch}")

            # Ensure repository exists
            if not os.path.exists(os.path.join(APP_DIR, '.git')):
                logging.info("Cloning repository...")
                result = subprocess.run(
                    ["git", "clone", REPO_URL, APP_DIR],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode != 0:
                    logging.error(f"Clone failed: {result.stderr}")
                    return
                logging.info(f"Clone output: {result.stdout}")

            os.chdir(APP_DIR)

            # Fetch all branches
            logging.info("Fetching all branches...")
            result = subprocess.run(
                ["git", "fetch", "--all"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logging.error(f"Fetch failed: {result.stderr}")
                return
            logging.info(f"Fetch output: {result.stdout}")

            # Determine which branch to deploy
            target_branch = branch
            if not branch_exists_on_origin(branch):
                logging.warning(f"Branch '{branch}' not found on origin, falling back to 'lab1'")
                target_branch = "lab1"
                # Важно: сразу переходим к развёртыванию lab1
            else:
                logging.info(f"Branch '{branch}' exists on origin, will deploy it")

            # Reset to the target branch
            logging.info(f"Resetting to origin/{target_branch}")
            result = subprocess.run(
                ["git", "reset", "--hard", f"origin/{target_branch}"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logging.error(f"Reset failed: {result.stderr}")
                return
            logging.info(f"Reset output: {result.stdout}")

            # Optionally create local branch for tracking (especially for test branches)
            if target_branch != "lab1":
                logging.info(f"Creating local branch '{target_branch}' tracking origin/{target_branch}")
                subprocess.run(
                    ["git", "checkout", "-B", target_branch, f"origin/{target_branch}"],
                    capture_output=True, text=True, timeout=10
                )
            else:
                # Ensure we are on lab1
                subprocess.run(
                    ["git", "checkout", "lab1"],
                    capture_output=True, text=True, timeout=10
                )

            # Get current SHA
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            logging.info(f"Current commit SHA: {sha} (from branch {target_branch})")

            # Write deploy ref
            try:
                with open(os.path.join(APP_DIR, ".deploy_ref"), "w") as f:
                    f.write(f"DEPLOY_REF={sha}\n")
                logging.info(f"Updated deploy ref: {sha}")
            except Exception as e:
                logging.error(f"Failed to write deploy ref: {e}")

            # Install dependencies
            requirements_file = os.path.join(APP_DIR, "requirements.txt")
            if os.path.exists(requirements_file):
                logging.info("Installing Python dependencies...")
                pip_path = os.path.join(VENV_DIR, "bin", "pip")
                if os.path.exists(pip_path):
                    result = subprocess.run(
                        [pip_path, "install", "-r", requirements_file],
                        capture_output=True, text=True, timeout=120
                    )
                    if result.returncode != 0:
                        logging.error(f"Pip install failed: {result.stderr}")
                        # Continue anyway
                    else:
                        logging.info(f"Pip install output: {result.stdout}")
                else:
                    logging.error(f"Virtual environment pip not found at {pip_path}")

            # Restart the application service
            logging.info("Restarting application service...")
            result = subprocess.run(
                ["sudo", "systemctl", "restart", "catty-reminders"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logging.error(f"Restart failed: {result.stderr}")
                return
            logging.info(f"Restart output: {result.stdout}")

            # Log successful deployment
            with open(DEPLOY_LOG, 'a') as f:
                f.write(f"{datetime.datetime.now()} - Deployed branch {target_branch} (original: {branch}) successfully\n")
            logging.info(f"Deployment completed successfully for branch: {target_branch} (original: {branch})")

        except subprocess.TimeoutExpired as e:
            logging.error(f"Timeout during deployment: {e}")
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
