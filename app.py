from flask import Flask, request, url_for, redirect, render_template, session
import pymongo
from pymongo import MongoClient
import json
import alpaca_trade_api as tradeapi
import classes.config as config
from classes.mypylib import log as pylog

# Imported Classes
from classes.authentication import Authentication
from classes.admin import Admin
from classes.account import Account
from classes.stock import Stock

# Blueprints for Flask routes
from routes.transaction import Transaction
from routes.admin_access import Admin_Access

# Configure App
app = Flask(__name__) 

# Declare blueprints
transaction = Transaction()
app.register_blueprint(transaction.update_balance_blueprint)
app.register_blueprint(transaction.buy_stock_blueprint)
app.register_blueprint(transaction.sell_stock_blueprint)
app.register_blueprint(transaction.save_stock_blueprint)
app.register_blueprint(transaction.search_stock_blueprint)
app.register_blueprint(transaction.filter_stock_blueprint)
admin_access = Admin_Access()
app.register_blueprint(admin_access.edit_account_blueprint)
app.register_blueprint(admin_access.stock_authenticate_blueprint)
app.register_blueprint(admin_access.account_authenticate_blueprint)

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
             # Login for Admin
            if username == 'admin' and password == 'admin':
                adminObj = Admin(username)
                return redirect(url_for('admin'))
            else:
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
                # Instantiate new Account Object and update DB with new account entry
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
        return render_template('market.html', username=session['username'], companies={})

# FAQ Page
@app.route("/faq") 
def faq():
    # Checks if account is logged it or not
    if not ('username' in session and session['username'] is not None and len(session['username']) > 0):
        return redirect(url_for('login'))
    else:
        return render_template('faq.html', username=session['username'])

# Account Profile Page
@app.route("/account") 
def account():
    # Checks if account is logged it or not
    if not ('username' in session and session['username'] is not None and len(session['username']) > 0):
        return redirect(url_for('login'))
    else:
        return render_template('account.html', username=session['username'])

# Generate Report for User in session
@app.route("/report", methods=['GET', 'POST'])
def report():
     # Checks if account is logged it or not
    if not ('username' in session and session['username'] is not None and len(session['username']) > 0):
        return redirect(url_for('login'))
    else:
        username=session['username']
        acc = accounts.find_one({'username': username})
        return render_template('report.html', acc=acc, i=acc['investments'], b=acc['balance'], stocks=acc['stocks'], saved=acc['saved'])


# Removes Session When User Logs Out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Delete Account from DB
@app.route('/del_account')
def del_account():
    # print(session)
    # session.get('username', None)
    # user = accounts.find({"username" : session.get('username', None)})
    # pylog(user[0], "USER-PRE")
    accounts.delete_one({"username" : session.get('username', None)})
    return redirect(url_for('create'))

# Update Customer Account Data
@app.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    if request.method == 'POST':
        if 'changeUsr' in request.form:
            username = request.form['username']
            if Authentication.new_user(username):
                accounts.update_one({"username" : session['username']}, {"$set" : {"username" : username}})
                session['username'] = username

        elif 'changePass' in request.form:
            oldPass = request.form['password']
            newPass = request.form['passwordTwo']
            if Authentication.new_pass(newPass):
                acc = accounts.find_one({'username': session['username']})
                if acc["password"] == oldPass:
                    accounts.update_one({"username" : session['username']}, {"$set" : {"password" : newPass}})


    return render_template('account_settings.html', username=session['username'])

# Routes for Admin Pages
# Admin Home Page
@app.route('/admin')
def admin():
    if session['username'] == 'admin':
        allAccounts = accounts.find({'username': {'$ne': 'admin'}})
        return render_template('admin/admin_accounts.html', username=session['username'], allAccounts=allAccounts)
    else:
        return redirect(url_for('home', username=session['username']))
    
# Round floats to 2 Decimals --> $XXXX.XX
@app.template_filter('price')
def format_price(value):
    return f"${value:,.2f}"

if __name__ == "__main__":
    app.run()