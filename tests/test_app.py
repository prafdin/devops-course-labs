import requests

def test_app_health():
    response = requests.get("http://127.0.0.1:8181/")
    assert response.status_code == 200
