import subprocess

def get_deploy_ref():
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'], 
            cwd='/home/kali/catty-reminders-app'
        ).decode('ascii').strip()
    except Exception:
        return "no-git-ref"
