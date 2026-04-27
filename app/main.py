import os
import json
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Dict, Optional
from pydantic import BaseModel

app = FastAPI(title="Catty Reminders App")

# Чтение DEPLOY_REF
def get_deploy_ref():
    return os.getenv('DEPLOY_REF', 'unknown')

# Загружаем конфиг
with open("config.json", "r") as f:
    config = json.load(f)

DB_PATH = config.get("db_path", "reminder_db.json")
USERS = config.get("users", {"tester": "foobar123"})

# Аутентификация
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

# Работа с БД
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

# ========== LOGIN ==========
@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return """
    <html>
        <body>
            <form method="post" action="/login">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </body>
    </html>
    """

@app.post("/login")
async def login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    
    if username in USERS and USERS[username] == password:
        return RedirectResponse(url="/reminders", status_code=303)
    return HTMLResponse(content="Invalid credentials", status_code=401)

# ========== API ==========
@app.get("/")
async def root():
    return {"message": "Catty Reminders App", "deploy_ref": get_deploy_ref()}

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
