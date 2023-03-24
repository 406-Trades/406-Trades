from flask import Flask, request, url_for, redirect, render_template, session
import pymongo
from pymongo import MongoClient
import json
import alpaca_trade_api as tradeapi
import classes.config as config

# Imported Classes
from classes.authentication import Authentication
from classes.account import Account
from classes.stock import Stock

# Configure App
app = Flask(__name__) 

# Blueprints for Flask routes
from routes.transaction import update_balance_blueprint
from routes.transaction import buy_stock_blueprint
from routes.transaction import sell_stock_blueprint
from routes.transaction import save_stock_blueprint
from routes.transaction import search_stock_blueprint
from routes.transaction import filter_stock_blueprint
from routes.admin_access import edit_account_blueprint

# Configure App
app = Flask(__name__) 

# Declare blueprints
app.register_blueprint(update_balance_blueprint)
app.register_blueprint(buy_stock_blueprint)
app.register_blueprint(sell_stock_blueprint)
app.register_blueprint(save_stock_blueprint)
app.register_blueprint(search_stock_blueprint)
app.register_blueprint(filter_stock_blueprint)
app.register_blueprint(edit_account_blueprint)

# # Connect to the Alpaca API
# api = tradeapi.REST(config.API_KEY, config.SECRET_KEY)
# headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

# Connect to MongoDB with Accounts
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

# Session key
app.secret_key = '406-trades'

# Login Redirect Everytime User Opens The Website
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('create'))

# Login Page Form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Checks if username and password match up to an existing account
        acc = accounts.find_one({'username': username})
        if acc and acc["password"] == password:
            # Adds user to the session, so they can re-login 
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')

# Create Account Page
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        passwordTwo = request.form['passwordTwo']
        # Creates an Account object
        auth = Authentication(username, password, passwordTwo)
        # Validates credentials as 
        if auth.valid_create():
            # Checks if user already exists
            if accounts.find_one({'username': username}):
                return render_template('create.html', error='Username already exists')
            # Adds user to DB if they are unique
            else:
                # Template for New Account
                acc = {
                    "username" : username,
                    "password" : password,
                    "balance" : 2000,
                    "investments" : 0,
                    "stocks" : {},
                    "saved" : []
                }
                accounts.insert_one(acc)

                accountObj = Account(username)

                return redirect(url_for('login'))
        else:
            return render_template('create.html', error='Invalid Username or Password')
    else:
        return render_template('create.html')

# Home Page
@app.route("/home") 
def home():
    # Checks if account is logged it or not
    if not ('username' in session and session['username'] is not None and len(session['username']) > 0):
        return redirect(url_for('login'))
    else:
        username=session['username']
        acc = accounts.find_one({'username': username})

        user = Account(username)
        user.get_invest()

        return render_template('home.html', username=username, acc=acc, i=round(acc['investments'], 2), b=round(acc['balance'], 2), stocks=acc['stocks'], saved=acc['saved'])

# Stock Market Page
@app.route("/market") 
def market():
    # Checks if account is logged it or not
    if not ('username' in session and session['username'] is not None and len(session['username']) > 0):
        return redirect(url_for('login'))
    else:
        return render_template('market.html', username=session['username'])

# FAQ Page
@app.route("/faq") 
def faq():
    # Checks if account is logged it or not
    if not ('username' in session and session['username'] is not None and len(session['username']) > 0):
        return redirect(url_for('login'))
    else:
        return render_template('faq.html')

# Account Profile Page
@app.route("/account") 
def account():
    # Checks if account is logged it or not
    if not ('username' in session and session['username'] is not None and len(session['username']) > 0):
        return redirect(url_for('login'))
    else:
        return render_template('account.html')

# Removes Session When User Logs Out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()