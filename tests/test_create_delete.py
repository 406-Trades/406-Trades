import os
import pytest
from flask import Flask, url_for, session

import pymongo
from pymongo import MongoClient

from app import create_app, app

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

app = Flask('testing')
app.secret_key = '406-trades'

@pytest.fixture
def client():
    with app.test_request_context():
        flask_app = create_app('flask_test.cfg')
        with flask_app.test_client() as client:
            with client.session_transaction() as session:
                session['username'] = 'try@gmail.com'

            yield client

def test_create(client):
    response = client.post('/create', data=dict(username='try@gmail.com', password='Abc123', passwordTwo='Abc123'), follow_redirects=True)
    accounts = db["Accounts"]
    acc = accounts.find_one({'username': 'try@gmail.com'})
    assert acc['username'] == 'try@gmail.com'


def test_delete_account(client):
    response = client.post('/del_account')

    accounts = db["Accounts"]
    acc = accounts.find_one({'username': 'try@gmail.com'})
        
    assert acc is None