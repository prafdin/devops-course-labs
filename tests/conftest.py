import pytest
from typing import Dict, Any
import json
import os

def load_test_data():
    """Load test data from inputs.json"""
    try:
        with open('/opt/catty-reminders/inputs.json', 'r') as f:
            return json.load(f)
    except:
        return {"users": [{"username": "test", "password": "test"}]}

@pytest.fixture
def user():
    """Return test user"""
    data = load_test_data()
    user_data = data.get('users', [{}])[0]
    
    class User:
        def __init__(self, username, password):
            self.username = username
            self.password = password
    
    return User(
        username=user_data.get('username', 'test'),
        password=user_data.get('password', 'test')
    )

@pytest.fixture
def alt_user():
    """Return alternative test user"""
    data = load_test_data()
    users = data.get('users', [{}])
    user_data = users[1] if len(users) > 1 else users[0]
    
    class User:
        def __init__(self, username, password):
            self.username = username
            self.password = password
    
    return User(
        username=user_data.get('username', 'test2'),
        password=user_data.get('password', 'test2')
    )
