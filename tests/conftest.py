import pytest
import requests

BASE_URL = "http://127.0.0.1:8181"

def login(username="heisenberg", password="P@ssw0rd"):
    session = requests.Session()
    session.post(f"{BASE_URL}/login", data={"username": username, "password": password})
    return session

@pytest.fixture
def session():
    return login()
