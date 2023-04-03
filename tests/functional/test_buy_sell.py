import os
import time
import pytest
from flask import Flask, url_for
import pymongo
from pymongo import MongoClient
import alpaca_trade_api as tradeapi

from app import create_app, app, format_price

import classes.config as config
from routes.transaction import Transaction

app = Flask('testing')
app.secret_key = '406-trades'

transaction = Transaction()
app.register_blueprint(transaction.home_buy_blueprint)
app.register_blueprint(transaction.buy_stock_blueprint)
app.register_blueprint(transaction.sell_stock_blueprint)

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, "https://paper-api.alpaca.markets/")
headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

@pytest.fixture
def client():
    app.jinja_env.filters['price'] = format_price

    with app.test_client() as client:

        with client.session_transaction() as session:
            session['username'] = 'Email@email.com'

        yield client

# Testing stock purchase from home
def test_home_buy_sq(client):
    aSymbol = 'SQ'

    with client.session_transaction() as session:
        acc = accounts.find_one({'username': session.get('username')})

        with app.test_request_context():         
            bal = acc['balance']

            flask_app = create_app('flask_test.cfg')
            response = flask_app.test_client().post('/home_buy?username=Email@email.com&symbol={}'.format(aSymbol), data={'watchlist-amount':1})

            get_price = round(api.get_latest_trade(aSymbol).price, 2)
            expectedBal = bal - get_price
            
            acc = accounts.find_one({'username': session.get('username')})
            newBal = acc['balance']

            assert response.status_code == 200
            assert expectedBal == newBal
            assert bytes(aSymbol, encoding='utf8') in response.data


# Testing stock purchase from search
def test_buy(client):
    aSymbol = 'SQ'

    with client.session_transaction() as session:
        acc = accounts.find_one({'username': session.get('username')})

        with app.test_request_context():         
            bal = acc['balance']

            flask_app = create_app('flask_test.cfg')
            response = flask_app.test_client().post('/buy_stock?username=Email@email.com&symbol={}&from=search'.format(aSymbol), data={'search-amount':1})

            get_price = round(api.get_latest_trade(aSymbol).price, 2)
            expectedBal = bal - get_price
            
            acc = accounts.find_one({'username': session.get('username')})
            newBal = acc['balance']

            assert response.status_code == 200
            assert expectedBal == newBal
            assert bytes(aSymbol, encoding='utf8') in response.data

# Testing stock sale from search
def test_sell(client):
    aSymbol = 'SQ'

    with client.session_transaction() as session:
        acc = accounts.find_one({'username': session.get('username')})

        with app.test_request_context():         
            bal = acc['balance']

            flask_app = create_app('flask_test.cfg')
            response = flask_app.test_client().post('/sell_stock?username=Email@email.com&symbol={}&from=search'.format(aSymbol), data={'search-amount':2})

            get_price = round(api.get_latest_trade(aSymbol).price, 2)
            expectedBal = bal + (get_price * 2)
            
            acc = accounts.find_one({'username': session.get('username')})
            newBal = acc['balance']

            assert response.status_code == 200
            assert expectedBal == newBal
            assert bytes(aSymbol, encoding='utf8') in response.data