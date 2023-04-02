import os
import pytest
from flask import Flask, url_for, session, render_template

import alpaca_trade_api as tradeapi

from routes.transaction import Transaction
from app import create_app, app

import classes.config as config

app = Flask('testing')
app.secret_key = '406-trades'

transaction = Transaction()
app.register_blueprint(transaction.search_stock_blueprint)

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, "https://paper-api.alpaca.markets/")
headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

@pytest.fixture
def client():
    with app.test_client() as client:

        with client.session_transaction() as session:
            session['username'] = 'Email@email.com'

        yield client

def test_search_aapl(client):
    aSymbol = 'AAPL'

    with client.session_transaction() as session:
        with app.test_request_context():

            flask_app = create_app('flask_test.cfg')

            response = flask_app.test_client().post(url_for('search_stock.search_stock', username=session.get('username'), symbol=aSymbol, time=30),
                                                       content_type='text', follow_redirects=True)

            get_price = str(round(api.get_latest_trade(aSymbol).price, 2))

            assert response.status_code == 200
            assert session.get('username') == 'Email@email.com'
            assert bytes(get_price, encoding='utf8') in response.data
            assert b"AAPL" in response.data
