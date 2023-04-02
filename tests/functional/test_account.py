import os
import pytest
from flask import Flask, url_for, session, render_template, Blueprint

from routes.report import Report
from app import create_app, app

from app import app

app = create_app()
app.secret_key = '406-trades'
app.debug = True

report = Report()
app.register_blueprint(report.generate_report_blueprint)
# app.register_blueprint(price_blueprint)
# app.jinja_env.filters['price'] = price_blueprint

@pytest.fixture
def client():
    app = create_app()
    app.secret_key = '406-trades'

    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

    # with app.test_client() as client:

    #     with client.session_transaction() as session:
    #         session['username'] = 'Email@email.com'

    #     yield client

# Testing report generation
def test_generate_report(client):
    with client.session_transaction() as session:
        # with app.test_request_context():

            response = client.get('/report', content_type='text', follow_redirects=True)

            # rendered_template = app.jinja_env.from_string(
            #     '{{(b+i)|price}}').render()

            assert response.status_code == 200
            assert b'Saved' in response.data
            # assert bytes(session.get('username'), encoding='utf8') in response.data