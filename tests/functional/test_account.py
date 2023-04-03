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
        assert bytes(session['username'], encoding='utf8') in response.data

def test_delete_account():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['username'] = '3@gmail.com'
        client.post('/create', data=dict(username='3@gmail.com', password='Abc123', passwordTwo='Abc123'), follow_redirects=True)
        client.post('/login', data=dict(username='3@gmail.com', password='Abc123'), follow_redirects=True)
        print(session['username'])
        acc = accounts.find_one({'username': '3@gmail.com'})
        response = client.post('/del_account')
        assert acc is None