from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
from app.utils.auth import AuthCookie, get_auth_cookie, get_login_form_creds
from app.utils.exceptions import UnauthorizedPageException
from app.utils.storage import templates
import subprocess

router = APIRouter()

def get_deploy_ref():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd="/opt/catty-reminders-app"
        )
        return result.stdout.strip()
    except:
        return "NA"

@router.get("/login", response_class=HTMLResponse)
async def get_login(
    request: Request,
    invalid: Optional[bool] = None,
    logged_out: Optional[bool] = None,
    unauthorized: Optional[bool] = None
):
    context = {
        'request': request,
        'deploy_ref': get_deploy_ref(),
        'invalid': invalid,
        'logged_out': logged_out,
        'unauthorized': unauthorized
    }
    return templates.TemplateResponse("pages/login.html", context)

@router.post("/login")
async def post_login(cookie: Optional[AuthCookie] = Depends(get_login_form_creds)):
    if cookie:
        response = RedirectResponse('/reminders', status_code=302)
        response.set_cookie(key=cookie.name, value=cookie.token)
    else:
        response = RedirectResponse('/login?invalid=True', status_code=302)
    return response

@router.get("/logout")
@router.post("/logout")
async def post_logout(cookie: Optional[AuthCookie] = Depends(get_auth_cookie)):
    if not cookie:
        raise UnauthorizedPageException()
    response = RedirectResponse('/login?logged_out=True', status_code=302)
    response.set_cookie(key=cookie.name, value=cookie.token, expires=-1)
    return response
