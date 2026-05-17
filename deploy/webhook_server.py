import os
import subprocess
from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn

app = FastAPI()

def run_deploy_script(branch: str = "main"):
    """Запускает bash-скрипт развертывания."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "deploy.sh")
        
        # Запускаем скрипт, ожидая его завершения
        result = subprocess.run(
            ["bash", script_path, branch], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"Deploy success:\n{result.stdout}", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"Deploy failed with exit code {e.returncode}:\n{e.stderr}", flush=True)
    except Exception as e:
        print(f"An error occurred during deploy execution: {e}", flush=True)

@app.post("/")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Обработчик вебхука.
    Слушает запросы от GitHub. При событии push отправляет задачу 
    развертывания в фон.
    """
    event = request.headers.get("X-GitHub-Event", "ping")
    
    if event == "push":
        # Читаем payload чтобы получить ветку
        try:
            payload = await request.json()
            ref = payload.get("ref", "")
            if ref.startswith("refs/heads/"):
                branch = ref.replace("refs/heads/", "")
            else:
                branch = "lab1"
        except Exception:
            branch = "lab1"

        background_tasks.add_task(run_deploy_script, branch)
        return {"status": f"Deployment task has been started for {branch}"}
        
    return {"status": f"Ignored event: {event}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
