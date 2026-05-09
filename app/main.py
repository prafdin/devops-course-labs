"""
This module is the main module for the FastAPI app.
"""

from app.utils.exceptions import UnauthorizedPageException
from app.routers import api, login, reminders, root
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
import os

app = FastAPI()
# app.include_router(root.router)   # закомментировано для проверок
app.include_router(api.router)
app.include_router(login.router)
app.include_router(reminders.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(UnauthorizedPageException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedPageException):
    return RedirectResponse('/login?unauthorized=True', status_code=302)

@app.exception_handler(404)
async def page_not_found_exception_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith('/api/'):
        return JSONResponse({'detail': exc.detail}, status_code=exc.status_code)
    else:
        return RedirectResponse('/not-found')

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    description = "Catty is a web app for tracking reminders."
    openapi_schema = get_openapi(
        title="Catty: The Reminders App",
        version="1.0.0",
        description=description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "static/img/logos/catty-500px.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
def home_for_check():
    deploy_ref = os.getenv("DEPLOY_REF", "unknown")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="deployref" content="{deploy_ref}">
        <title>Catty Reminders</title>
    </head>
    <body>
        <h1>Catty Reminders</h1>
        <p>Deploy ref: {deploy_ref}</p>
        <p><a href="/reminders">Go to reminders</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
