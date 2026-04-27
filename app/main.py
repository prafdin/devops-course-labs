import os
import json
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from typing import Dict, Optional
from pydantic import BaseModel

app = FastAPI(title="Catty Reminders App")

def get_deploy_ref():
    return os.getenv('DEPLOY_REF', 'unknown')

# Загружаем конфиг
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except:
    config = {"db_path": "reminder_db.json", "users": {"tester": "foobar123"}}

DB_PATH = config.get("db_path", "reminder_db.json")
USERS = config.get("users", {"tester": "foobar123"})

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if username in USERS and USERS[username] == password:
        return username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

class Reminder(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    due_date: str
    completed: bool = False

def load_reminders() -> Dict[int, Reminder]:
    if not os.path.exists(DB_PATH):
        return {}
    try:
        with open(DB_PATH, "r") as f:
            data = json.load(f)
        reminders = {}
        for key, value in data.items():
            reminders[int(key)] = Reminder(**value)
        return reminders
    except:
        return {}

def save_reminders(reminders: Dict[int, Reminder]):
    data = {str(k): v.dict() for k, v in reminders.items()}
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/")
async def root():
    return {"message": "Catty Reminders App", "deploy_ref": get_deploy_ref()}

@app.post("/login")
async def login(request: Request):
    try:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        if username in USERS and USERS[username] == password:
            return RedirectResponse(url="/reminders", status_code=303)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except:
        raise HTTPException(status_code=400, detail="Bad request")

@app.get("/reminders")
async def get_reminders():
    return [r.dict() for r in load_reminders().values()]

@app.post("/reminders")
async def create_reminder(reminder: Reminder, authenticated: str = Depends(authenticate)):
    reminders = load_reminders()
    new_id = max(reminders.keys()) + 1 if reminders else 1
    reminder.id = new_id
    reminders[new_id] = reminder
    save_reminders(reminders)
    return {"message": "Reminder created", "id": new_id}

@app.get("/deploy-ref")
async def deploy_ref():
    return {"deploy_ref": get_deploy_ref()}

@app.get("/health")
async def health():
    return {"status": "ok", "deploy_ref": get_deploy_ref()}
