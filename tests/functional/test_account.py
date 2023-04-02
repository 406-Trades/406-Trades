import os
import pytest
from flask import Flask, url_for, session, render_template, Blueprint

from routes.report import Report
from app import create_app, app

from app import format_price

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
