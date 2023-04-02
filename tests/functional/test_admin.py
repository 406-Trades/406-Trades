import os
import pytest
from flask import Flask
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

from app import create_app, app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_admin_login():
    with app.test_client() as client:
        response = client.post('/login', data=dict(username='admin', password='admin'))
        assert response.status_code == 302
        assert response.location == '/admin'

def test_admin_page_incorrect():
    with app.test_client() as client:
        client.post('/login', data=dict(username='nikita2@gmail.com', password='Abc123'))
        response = client.post('/admin')
        assert response.status_code != 200

def test_admin_stock_auth():
    with app.test_client() as client:
        client.post('/login', data=dict(username='admin', password='admin'))
        response = client.post('/stock_authenticate', data=dict(stock='AAPL'))
        assert b"is a valid stock." in response.data

def test_admin_invalid_stock_auth():
    with app.test_client() as client:
        client.post('/login', data=dict(username='admin', password='admin'))
        response = client.post('/stock_authenticate', data=dict(stock='AAPL123123'))
        assert b"does not exist." in response.data

def test_admin_account_auth():
    with app.test_client() as client:
        client.post('/login', data=dict(username='admin', password='admin'))
        response = client.post('/account_authenticate', data=dict(account='Email@email.com'))
        assert b"Email@email.com exists in the database!" in response.data

def test_admin_invalid_account_auth():
    with app.test_client() as client:
        client.post('/login', data=dict(username='admin', password='admin'))
        response = client.post('/account_authenticate', data=dict(account='asd'))
        assert b"asd does not exist in the database." in response.data

def test_admin_delete_invalid_account():
    with app.test_client() as client:
            acc = accounts.find_one({'username': 'nikita2@gmail.com'})
            client.post('/login', data=dict(username='admin', password='admin'))
            username = "123123123123123123"
            response = client.post('/edit_account', data=dict(username='123123123123123123', submit='Delete'))            
            soup = BeautifulSoup(response.data, 'html.parser')
            account_value = str(soup.find('div', {'class': 'bal'}).text.strip())
            account = db.accounts.find_one({'username': username})
            assert account_value.encode() in response.data