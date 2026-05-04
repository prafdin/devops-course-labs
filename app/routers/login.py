"""
This module provides routes for authentication.
"""

from app import templates
from app.utils.auth import AuthCookie, get_login_form_creds, get_auth_cookie
from app.utils.exceptions import UnauthorizedPageException

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
deploy_ref_path = os.path.join(BASE_DIR, '.deploy_ref')

router = APIRouter()


@router.get(
    path="/login",
    summary="Gets the login page",
    tags=["Pages", "Authentication"],
    response_class=HTMLResponse
)
async def get_login(
    request: Request,
    invalid: Optional[bool] = None,
    logged_out: Optional[bool] = None,
    unauthorized: Optional[bool] = None):

    # Чтение deploy_ref из файла
    deploy_ref = None
    try:
        with open(deploy_ref_path, 'r') as f:
            content = f.read().strip()
            if '=' in content:
                deploy_ref = content.split('=', 1)[1]
    except:
        pass

    context = {
        'request': request,
        'deploy_ref': deploy_ref,
        'invalid': invalid,
        'logged_out': logged_out,
        'unauthorized': unauthorized
    }
    return templates.TemplateResponse("pages/login.html", context)


@router.post(
    path="/login",
    summary="Logs into the app",
    tags=["Authentication"]
)
async def post_login(cookie: Optional[AuthCookie] = Depends(get_login_form_creds)):
    if cookie:
        response = RedirectResponse('/reminders', status_code=302)
        response.set_cookie(key=cookie.name, value=cookie.token)
    else:
        response = RedirectResponse('/login?invalid=True', status_code=302)
    return response


logout = dict(
    path="/logout",
    summary="Logs out of the app",
    tags=["Authentication"]
)


@router.get(**logout)
@router.post(**logout)
async def logout_handler(cookie: Optional[AuthCookie] = Depends(get_auth_cookie)):
    if not cookie:
        raise UnauthorizedPageException()
    response = RedirectResponse('/login?logged_out=True', status_code=302)
    response.set_cookie(key=cookie.name, value=cookie.token, expires=-1)
    return response
