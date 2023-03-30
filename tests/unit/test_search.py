import os
import pytest
from flask import Flask

from app import create_app, app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# def test_start_login(app):
#     flask_app = create_app('flask_test.cfg')

#     with flask_app.test_client() as test_client:

#         response = test_client.get('/login')
#         # assert response.status_code == 200
#         assert b"Don't" in response.data

def test_login_screen(client):
    flask_app = create_app('flask_test.cfg')

    response = flask_app.test_client().get('/login')

    print(response.data)
    print("*****************************************************************************")

    assert response.status_code == 200
    assert b"Don't have an account yet?" in response.data













# import os,sys,inspect, pytest
# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0,parentdir)

# import stocks

# @pytest.fixture
# def app():
#     app = stocks.app
#     yield app

# def test_login_screen(client):
#     flask_app = create_app

#     url = "/login"
#     response = client.get(url)

#     print(response.data)
#     print("*****************************************************************************")

#     assert b"Don't have an account yet?" in response.data

# # import os
# # import tempfile

# # import pytest
# # from flask import Flask

# # import stocks

# # # from tradesApp import market
# # # from routes.transaction import 

# # @pytest.fixture
# # def client():
# #     db_fd, stocks.app.config['DATABASE'] = tempfile.mkstemp()
# #     stocks.app.config['TESTING'] = True

# #     with stocks.app.test_client() as client:
# #         with stocks.app.app_context():
# #             stocks.init_db()
# #         yield client

# #     os.close(db_fd)
# #     os.unlink(stocks.app.config['DATABASE'])

# # def test_login_screen(client):
# #     flask_app = create_app

# #     url = "/login"
# #     response = client.get(url)

# #     print(response.data)
# #     print("*****************************************************************************")

# #     assert b"Don't have an account yet?" in response.data


# # def test_search_default():
# #     app = Flask(__name__)
# #     client = app.test_client()
# #     url = "/market"
# #     response = client.get(url)

# #     print(response.data)

# #     assert b'Search for a stock' in response.data