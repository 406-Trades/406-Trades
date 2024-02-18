import os
import pytest
from flask import Flask

from app import create_app, app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_faq_screen():
    with app.test_client() as client:
        client.post('/login', data=dict(username='nikita2@gmail.com', password='Abc123'))
        response = client.post('/faq', follow_redirects=True)
        assert response.status_code == 200
        assert b"How do I create an account?" in response.data