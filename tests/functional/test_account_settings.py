import os
import pytest
from flask import Flask, session
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
from unittest.mock import patch
import time

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

from app import create_app, app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_logout():
     with app.test_client() as client:
        client.post('/login', data=dict(username='Email@email.com', password='Test1234'))
        response = client.post('/logout')
        assert 'username' not in session

def test_change_user():
    with app.test_client() as client:
        client.post('/create', data=dict(username='4@gmail.com', password='Abc123', passwordTwo='Abc123'))
        client.post('/login', data=dict(username='4@gmail.com', password='Abc123'))
        acc = accounts.find_one({'username': '4@gmail.com'})
        print(acc)
        response = client.post('/account_settings?c=changeUsr', data=dict(username='42@gmail.com'))
        updated_acc = accounts.find_one({'username': '42@gmail.com'})
        print(updated_acc)
        assert b'Account Settings' in response.data
        assert updated_acc
        client.post('/del_account')

def test_change_user_invalid():
    with app.test_client() as client:
        client.post('/create', data=dict(username='4@gmail.com', password='Abc123', passwordTwo='Abc123'))
        client.post('/login', data=dict(username='4@gmail.com', password='Abc123'))
        acc = accounts.find_one({'username': '4@gmail.com'})
        print(acc)
        response = client.post('/account_settings?c=changeUsr', data=dict(username='ABC'))
        updated_acc = accounts.find_one({'username': 'ABC'})
        print(updated_acc)
        assert b'Invalid Username, must be a valid email address' in response.data
        assert updated_acc is None
        client.post('/del_account')

def test_change_password():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['username'] = '4@gmail.com'
        client.post('/create', data=dict(username='4@gmail.com', password='Abc123', passwordTwo='Abc123'))
        client.post('/login', data=dict(username='4@gmail.com', password='Abc123'))
        response = client.post('/account_settings?c=changePass', data=dict(password='Abc123', passwordTwo='New123'))
        assert b'Account Settings' in response.data
        acc = accounts.find_one({'username': '4@gmail.com'})
        assert acc['password'] == 'New123'
        client.post('/del_account')

def test_change_password_invalid():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['username'] = '4@gmail.com'
        client.post('/create', data=dict(username='4@gmail.com', password='Abc123', passwordTwo='Abc123'))
        client.post('/login', data=dict(username='4@gmail.com', password='Abc123'))
        response = client.post('/account_settings?c=changePass', data=dict(password='Abc123', passwordTwo='123'))
        assert b'Account Settings' in response.data
        acc = accounts.find_one({'username': '4@gmail.com'})
        assert acc['password'] == 'Abc123'
        assert b'Invalid Password: Password must contain 1 lowercase, 1 uppercase, and 1 number' in response.data
        client.post('/del_account')