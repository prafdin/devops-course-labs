import requests
import pytest

BASE_URL = "http://127.0.0.1:8181"

@pytest.fixture
def session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/login", data={"username": "heisenberg", "password": "P@ssw0rd"})
    assert r.status_code == 200
    return s

def test_get_reminders_unauthorized():
    r = requests.get(f"{BASE_URL}/api/reminders")
    assert r.status_code == 401

def test_get_reminders_authorized(session):
    r = session.get(f"{BASE_URL}/api/reminders")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_create_reminder_list(session):
    r = session.post(f"{BASE_URL}/api/reminders", json={"name": "Test List"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Test List"
    list_id = data["id"]
    # cleanup
    session.delete(f"{BASE_URL}/api/reminders/{list_id}")

def test_delete_reminder_list(session):
    r = session.post(f"{BASE_URL}/api/reminders", json={"name": "To Delete"})
    list_id = r.json()["id"]
    r = session.delete(f"{BASE_URL}/api/reminders/{list_id}")
    assert r.status_code == 200

def test_create_reminder_item(session):
    r = session.post(f"{BASE_URL}/api/reminders", json={"name": "Item Test List"})
    list_id = r.json()["id"]
    r = session.post(f"{BASE_URL}/api/reminders/{list_id}/items", json={"description": "Buy milk"})
    assert r.status_code == 200
    assert r.json()["description"] == "Buy milk"
    # cleanup
    session.delete(f"{BASE_URL}/api/reminders/{list_id}")
