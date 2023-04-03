import os
import pytest
from flask import Flask
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
from unittest.mock import patch

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

def test_admin_delete_account():
    with app.test_client() as client:
        client.post('/create', data=dict(username='1@gmail.com', password='Abc123', passwordTwo='Abc123'))
        client.post('/login', data=dict(username='1@gmail.com', password='Abc123'))
        client.post('/login', data=dict(username='admin', password='admin'))
        acc = accounts.find_one({'username': '1@gmail.com'})
        response = client.post('/edit_account?username=1@gmail.com&id={}'.format(str(acc['_id'])), data=dict(username='1@gmail.com', submit='Delete'))
        assert response.status_code == 200
        assert accounts.find_one({'username': '1@gmail.com'}) is None
    
def test_admin_edit_account():
    with app.test_client() as client:
        client.post('/create', data=dict(username='2@gmail.com', password='Abc123', passwordTwo='Abc123'))
        client.post('/login', data=dict(username='2@gmail.com', password='Abc123'))
        client.post('/login', data=dict(username='admin', password='admin'))
        acc = accounts.find_one({'username': '2@gmail.com'})
        client.post('/edit_account?username=2@gmail.com&id={}'.format(str(acc['_id'])), data=dict(username=acc['username'], investments=acc['investments'], stocks=str(acc['stocks']), saved=acc['saved'], balance='123', submit='Save'))
        updated_acc = accounts.find_one({'username': '2@gmail.com'})
        assert updated_acc['balance'] == 123