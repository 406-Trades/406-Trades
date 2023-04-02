import os
import pytest
from flask import Flask, url_for, session, render_template, Blueprint

from routes.report import Report
from app import create_app, app
from app import format_price
import pymongo
from pymongo import MongoClient

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

app = Flask('testing')
app.secret_key = '406-trades'
app.debug = True

report = Report()
app.register_blueprint(report.generate_report_blueprint)
# app.register_blueprint(price_blueprint)
# app.jinja_env.filters['price'] = price_blueprint

@pytest.fixture
def client():
    app.jinja_env.filters['price'] = format_price

    with app.test_client() as client:

        with client.session_transaction() as session:
            session['username'] = 'Email@email.com'

        yield client

# Testing report generation
def test_generate_report(client):    
    with app.app_context():
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

        with client.session_transaction() as session:
            session['username'] = 'Email@email.com'

        response = client.get('/report')

        assert response.status_code == 200
        assert bytes(session.get('username'), encoding='utf8') in response.data

def test_delete_account():
    with app.test_client() as client:
        client.post('/create', data=dict(username='1@gmail.com', password='Abc123', passwordTwo='Abc123'))
        client.post('/login', data=dict(username='1@gmail.com', password='Abc123'))
        client.post('/login', data=dict(username='admin', password='admin'))
        acc = accounts.find_one({'username': '1@gmail.com'})
        response = client.post('/edit_account?username=1@gmail.com&id={}'.format(str(acc['_id'])), data=dict(username='1@gmail.com', submit='Delete'))
        assert response.status_code == 200
        assert accounts.find_one({'username': '1@gmail.com'}) is None
    
def test_edit_account():
    with app.test_client() as client:
        client.post('/create', data=dict(username='2@gmail.com', password='Abc123', passwordTwo='Abc123'))
        client.post('/login', data=dict(username='2@gmail.com', password='Abc123'))
        client.post('/login', data=dict(username='admin', password='admin'))
        acc = accounts.find_one({'username': '2@gmail.com'})
        client.post('/edit_account?username=2%40gmail.com&id={}'.format(str(acc['_id'])), data=dict(username=acc['username'], investments=acc['investments'], stocks=str(acc['stocks']), saved=acc['saved'], balance='123', submit='Save'))
        updated_acc = accounts.find_one({'username': '2@gmail.com'})
        assert updated_acc['balance'] == 123