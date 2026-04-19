from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

def get_deploy_ref():
    ref_file = os.path.join(os.path.dirname(__file__), '..', '..', 'deploy_ref.txt')
    try:
        with open(ref_file, 'r') as f:
            return f.read().strip()
    except:
        return "unknown"

@router.get("/", response_class=HTMLResponse)
async def read_root():
    deployref = get_deploy_ref()
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Catty Reminders</title></head>
    <body>
        <h1>🐱 Catty Reminders App</h1>
        <p>Deploy Ref: <strong>{deployref}</strong></p>
        <p><a href="/login">Login</a> | <a href="/reminders">Reminders</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
