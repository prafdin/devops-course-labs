from playwright.sync_api import Page, expect
import re

BASE_URL = "http://127.0.0.1:8181"

def test_login_page_loads(page: Page):
    page.goto(f"{BASE_URL}/login")
    expect(page).to_have_title(re.compile("Login"))

def test_login_success(page: Page):
    page.goto(f"{BASE_URL}/login")
    page.fill("input[name='username']", "heisenberg")
    page.fill("input[name='password']", "P@ssw0rd")
    page.click("button[type='submit']")
    expect(page).to_have_url(f"{BASE_URL}/reminders")

def test_login_wrong_password(page: Page):
    page.goto(f"{BASE_URL}/login")
    page.fill("input[name='username']", "heisenberg")
    page.fill("input[name='password']", "wrongpassword")
    page.click("button[type='submit']")
    # Редирект на /login с параметром invalid=True — правильное поведение
    expect(page).to_have_url(re.compile(r"/login"))
    expect(page).to_have_url(re.compile(r"invalid=True"))

def test_reminders_page_requires_login(page: Page):
    page.goto(f"{BASE_URL}/reminders")
    # Должен редиректить на /login (с любыми query параметрами)
    expect(page).to_have_url(re.compile(r"/login"))
