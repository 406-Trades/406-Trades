import os
import tempfile

import pytest
from flask import Flask

import stocks

# from tradesApp import market
# from routes.transaction import 

@pytest.fixture
def client():
    db_fd, stocks.app.config['DATABASE'] = tempfile.mkstemp()
    stocks.app.config['TESTING'] = True

    with stocks.app.test_client() as client:
        with stocks.app.app_context():
            stocks.init_db()
        yield client

    os.close(db_fd)
    os.unlink(stocks.app.config['DATABASE'])

def test_login_screen(client):
    flask_app = create_app

    url = "/login"
    response = client.get(url)

    print(response.data)
    print("*****************************************************************************")

    assert b"Don't have an account yet?" in response.data


# def test_search_default():
#     app = Flask(__name__)
#     client = app.test_client()
#     url = "/market"
#     response = client.get(url)

#     print(response.data)

#     assert b'Search for a stock' in response.data