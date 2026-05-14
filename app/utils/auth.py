"""
This module handles authentication for the app.
"""

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

import jwt
import secrets
from app import users, secret_key, db_config
from app.utils.exceptions import UnauthorizedException, UnauthorizedPageException
from app.utils.mysql_storage import MySQLStorage
from fastapi import Cookie, Depends, Form
from fastapi.security import HTTPBasic
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import RedirectResponse
from typing import Optional

# --------------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------------

class AuthCookie(BaseModel):
    username: str

# --------------------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------------------

def generate_token(username: str) -> str:
    """Generates a JWT token for the user."""
    return jwt.encode({"username": username}, secret_key, algorithm="HS256")

def decode_token(token: str) -> Optional[str]:
    """Decodes a JWT token and returns the username if valid."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload.get("username")
    except jwt.InvalidTokenError:
        return None

def get_auth_cookie(cookie: Optional[str] = Cookie(None, alias="auth")) -> Optional[AuthCookie]:
    """Extracts the auth cookie from the request."""
    if cookie:
        username = decode_token(cookie)
        if username:
            return AuthCookie(username=username)
    return None

def get_username_for_api(auth: Optional[AuthCookie] = Depends(get_auth_cookie)) -> str:
    """Gets the username from the auth cookie for API routes."""
    if not auth:
        raise UnauthorizedException()
    return auth.username

def get_username_for_page(auth: Optional[AuthCookie] = Depends(get_auth_cookie)) -> str:
    """Gets the username from the auth cookie for page routes."""
    if not auth:
        raise UnauthorizedPageException()
    return auth.username

def get_storage_for_api(username: str = Depends(get_username_for_api)) -> MySQLStorage:
    """Returns a MySQL storage instance for API routes."""
    return MySQLStorage(owner=username, db_config=db_config)

def get_storage_for_page(username: str = Depends(get_username_for_page)) -> MySQLStorage:
    """Returns a MySQL storage instance for page routes."""
    return MySQLStorage(owner=username, db_config=db_config)

# --------------------------------------------------------------------------------
# Login and Logout
# --------------------------------------------------------------------------------

async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handles login form submission."""
    if username in users and users[username] == password:
        token = generate_token(username)
        response = RedirectResponse(url="/reminders", status_code=303)
        response.set_cookie(key="auth", value=token, httponly=True)
        return response
    return RedirectResponse(url="/login?error=Invalid credentials", status_code=303)

async def logout(request: Request):
    """Handles logout."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("auth")
    return response
