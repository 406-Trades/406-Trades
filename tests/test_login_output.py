import os
import pytest
from flask import Flask

from app import create_app, app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_login_screen():
    flask_app = create_app('flask_test.cfg')

    response = flask_app.test_client().get('/login')

    assert response.status_code == 200
    assert b"Don't have an account yet?" in response.data

def test_login():
    
    with app.test_client() as client:

        response = client.post('/login', data=dict(username='Email@email.com', password='Test1234'))

        assert response.status_code == 302
        assert response.location == '/home'

def test_incorrect_login():
    with app.test_client() as client:
    
        response = client.post('/login', data=dict(username='wrongUser', password='wrongPass'))

        assert response.status_code == 200
        assert b"Invalid username or password" in response.data