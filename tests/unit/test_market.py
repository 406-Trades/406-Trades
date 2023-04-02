import os
import pytest
from flask import Flask, url_for, session

from app import create_app, app


# @pytest.fixture
# def app():
#     app = create_app()
#     return app

app = Flask('testing')
app.secret_key = '406-trades'

@pytest.fixture
def client():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['username'] = 'Email@email.com'

        yield client

# def test_login_screen():
#     flask_app = create_app('flask_test.cfg')

#     response = flask_app.test_client().get('/login')

#     assert response.status_code == 200
#     assert b"Don't have an account yet?" in response.data


def test_search_aapl(client):      

    # , data={'username':'Email@email.com'}
    # data={'username':'Email@email.com'}
    # follow_redirects=True,
    # , username='Email@email.com'

    # username='Email@email.com', symbol='AAPL', time=30
    # data={'username':'Email@email.com', 'symbol':'AAPL', 'time':30}

    with client.session_transaction() as session:
        with app.test_request_context('/market'):
            # with client.session_transaction() as session:
            #     session['username'] = 'test_user'

            # flask_app = create_app('flask_test.cfg')

            # response = flask_app.test_client().post(url_for('search_stock.search_stock'))

            response = client.get(url_for('search_stock.search_stock'), content_type='text')

            # assert response.status_code == 200
            assert session.get('username') == 'Email@email.com'
            assert b"AAPL" in response.data

# def test_incorrect_login():
#     with app.test_client() as client:
    
#         response = client.post('/login', data=dict(username='wrongUser', password='wrongPass'))

#         assert response.status_code == 200
#         assert b"Invalid username or password" in response.data