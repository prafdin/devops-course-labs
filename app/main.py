import os
import json
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Catty Reminders App")

# Чтение DEPLOY_REF из файла (фиксируется при сборке)
def get_deploy_ref():
    try:
        with open('/deploy_ref.txt', 'r') as f:
            return f.read().strip()
    except:
        return os.getenv('DEPLOY_REF', 'unknown')

# Монтируем статику и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Загружаем конфиг
with open("config.json", "r") as f:
    config = json.load(f)

DB_PATH = config.get("db_path", "reminder_db.json")
SECRET_KEY = config.get("secret_key", "default_secret")
USERS = config.get("users", {"tester": "foobar123"})

# Базовая аутентификация
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

# Модели
class Reminder(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    due_date: str
    completed: bool = False

# Загрузка напоминаний из JSON
def load_reminders() -> Dict[int, Reminder]:
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r") as f:
        data = json.load(f)
    reminders = {}
    for key, value in data.items():
        reminders[int(key)] = Reminder(**value)
    return reminders

def save_reminders(reminders: Dict[int, Reminder]):
    data = {str(k): v.dict() for k, v in reminders.items()}
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

# API эндпоинты
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "deploy_ref": get_deploy_ref()
    })

@app.get("/deploy-ref")
async def deploy_ref():
    return {"deploy_ref": get_deploy_ref()}

@app.get("/reminders")
async def get_reminders(authenticated: str = Depends(authenticate)):
    reminders = load_reminders()
    return [r.dict() for r in reminders.values()]

@app.post("/reminders")
async def create_reminder(reminder: Reminder, authenticated: str = Depends(authenticate)):
    reminders = load_reminders()
    new_id = max(reminders.keys()) + 1 if reminders else 1
    reminder.id = new_id
    reminders[new_id] = reminder
    save_reminders(reminders)
    return {"message": "Reminder created", "id": new_id}

@app.put("/reminders/{reminder_id}")
async def update_reminder(reminder_id: int, reminder: Reminder, authenticated: str = Depends(authenticate)):
    reminders = load_reminders()
    if reminder_id not in reminders:
        raise HTTPException(status_code=404, detail="Reminder not found")
    reminder.id = reminder_id
    reminders[reminder_id] = reminder
    save_reminders(reminders)
    return {"message": "Reminder updated"}

@app.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: int, authenticated: str = Depends(authenticate)):
    reminders = load_reminders()
    if reminder_id not in reminders:
        raise HTTPException(status_code=404, detail="Reminder not found")
    del reminders[reminder_id]
    save_reminders(reminders)
    return {"message": "Reminder deleted"}

@app.get("/health")
async def health():
    return {"status": "ok", "deploy_ref": get_deploy_ref()}
