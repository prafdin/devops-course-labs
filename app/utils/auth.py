"""
This module handles authentication for the app.
"""

import jwt
import secrets
from fastapi import Cookie, Depends, Form, Request
from fastapi.responses import RedirectResponse
from starlette.responses import Response
from typing import Optional

from app import users, secret_key, db_config
from app.utils.exceptions import UnauthorizedException, UnauthorizedPageException
from app.utils.mysql_storage import MySQLStorage


class AuthCookie:
    def __init__(self, username: str):
        self.username = username


def generate_token(username: str) -> str:
    return jwt.encode({"username": username}, secret_key, algorithm="HS256")


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload.get("username")
    except jwt.InvalidTokenError:
        return None


def get_login_form_creds(
    username: str = Form(...),
    password: str = Form(...)
):
    return username, password


def get_auth_cookie(cookie: Optional[str] = Cookie(None, alias="auth")) -> Optional[AuthCookie]:
    if cookie:
        username = decode_token(cookie)
        if username:
            return AuthCookie(username)
    return None


def get_username_for_api(auth: Optional[AuthCookie] = Depends(get_auth_cookie)) -> str:
    if not auth:
        raise UnauthorizedException()
    return auth.username


def get_username_for_page(auth: Optional[AuthCookie] = Depends(get_auth_cookie)) -> str:
    if not auth:
        raise UnauthorizedPageException()
    return auth.username


def get_storage_for_api(username: str = Depends(get_username_for_api)) -> MySQLStorage:
    return MySQLStorage(owner=username, db_config=db_config)


def get_storage_for_page(username: str = Depends(get_username_for_page)) -> MySQLStorage:
    return MySQLStorage(owner=username, db_config=db_config)


async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in users and users[username] == password:
        token = generate_token(username)
        response = RedirectResponse(url="/reminders", status_code=303)
        response.set_cookie(key="auth", value=token, httponly=True)
        return response
    return RedirectResponse(url="/login?error=Invalid credentials", status_code=303)


async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("auth")
    return response
