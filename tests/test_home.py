import os
import pytest
from flask import Flask
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient

from app import create_app, app

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_redirect_page():
    flask_app = create_app('flask_test.cfg')

    response = flask_app.test_client().get('/')
    assert response.status_code != 200

def test_home_page_incorrect():
    flask_app = create_app('flask_test.cfg')
    response = flask_app.test_client().get('/home')
    assert response.status_code != 200

def test_home_page_working():
    with app.test_client() as client:
        response = client.post('/home', data=dict(username='Email@email.com', password='Test1234'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

def test_increment_balance():
    with app.test_client() as client:
        acc = accounts.find_one({'username': 'nikita2@gmail.com'})
        client.post('/login', data=dict(username='nikita2@gmail.com', password='Abc123'))
        bal = acc['balance']
        response = client.post('/update_balance?username=nikita2@gmail.com&b={}'.format(bal), data=dict(username='nikita2@gmail.com', password='Abc123', amount='100', submit='Increment'), follow_redirects=True)
        soup = BeautifulSoup(response.data, 'html.parser')
        account_value = str(soup.find('div', {'class': 'bal'}).text.strip())

        acc = accounts.find_one({'username': 'nikita2@gmail.com'})
        newBal = acc['balance']
        assert newBal == (bal + 100)
        assert account_value.encode() in response.data

def test_increment_balance_incorrect():
    with app.test_client() as client:
        acc = accounts.find_one({'username': 'nikita2@gmail.com'})
        client.post('/login', data=dict(username='nikita2@gmail.com', password='Abc123'))
        bal = acc['balance']
        response = client.post('/update_balance?username=nikita2@gmail.com&b={}'.format(bal), data=dict(username='nikita2@gmail.com', password='Abc123', amount='ABC', submit='Increment'), follow_redirects=True)
        soup = BeautifulSoup(response.data, 'html.parser')
        account_value = str(soup.find('div', {'class': 'bal'}).text.strip())

        acc = accounts.find_one({'username': 'nikita2@gmail.com'})
        newBal = acc['balance']
        assert newBal == bal
        assert account_value.encode() in response.data

def test_decrement_balance():
   with app.test_client() as client:
        acc = accounts.find_one({'username': 'nikita2@gmail.com'})
        client.post('/login', data=dict(username='nikita2@gmail.com', password='Abc123'))
        bal = acc['balance']
        response = client.post('/update_balance?username=nikita2@gmail.com&b={}'.format(bal), data=dict(username='nikita2@gmail.com', password='Abc123', amount='100', submit='Decrement'), follow_redirects=True)
        soup = BeautifulSoup(response.data, 'html.parser')
        account_value = soup.find('div', {'class': 'bal'}).text.strip()

        acc = accounts.find_one({'username': 'nikita2@gmail.com'})
        newBal = acc['balance']
        assert newBal == (bal - 100)
        assert account_value.encode() in response.data

def test_decrement_balance_incorrect():
    with app.test_client() as client:
        acc = accounts.find_one({'username': 'nikita2@gmail.com'})
        client.post('/login', data=dict(username='nikita2@gmail.com', password='Abc123'))
        bal = acc['balance']
        response = client.post('/update_balance?username=nikita2@gmail.com&b={}'.format(bal), data=dict(username='nikita2@gmail.com', password='Abc123', amount='ABC', submit='Decrement'), follow_redirects=True)
        soup = BeautifulSoup(response.data, 'html.parser')
        account_value = str(soup.find('div', {'class': 'bal'}).text.strip())

        acc = accounts.find_one({'username': 'nikita2@gmail.com'})
        newBal = acc['balance']
        assert newBal == bal
        assert account_value.encode() in response.data