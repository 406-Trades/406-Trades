from flask import Flask, Blueprint, render_template, redirect, url_for, request, session, jsonify
from classes.account import Account
import alpaca_trade_api as tradeapi
import classes.config as config
import pymongo
from pymongo import MongoClient
import json
import requests

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

# Connect to the Alpaca API
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY)
headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

# Blueprints
edit_account_blueprint = Blueprint('edit_account', __name__)
stock_authenticate_blueprint = Blueprint('stock_authenticate', __name__)
account_authenticate_blueprint = Blueprint('account_authenticate', __name__)

# Admin Edit/Delete Account / Stocks for all Accounts in DB
@edit_account_blueprint.route('/edit_account', methods=['GET', 'POST'])
def edit_account():
    username = request.args.get('username')
    id = request.args.get('id')
    account = db.accounts.find_one({'username': username})
    allAccounts = accounts.find()
    if request.method == 'POST':
        # Deletes account from DB
        if request.form['submit-button'] == 'Delete':
            accounts.delete_one({'username': username})
        # Update the account in MongoDB
        elif request.form['submit-button'] == 'Save':
            accounts.update_one({'username': username}, {'$set': {
                'username': request.form['username'],
                'balance': request.form['balance'],
                'investments': request.form['investments'],
                'stocks': request.form['stocks'],
                'saved': request.form['saved']
            }})
        return render_template('admin/admin_accounts.html', username=session['username'], allAccounts=allAccounts)

# Admin Authenticate Stock
@stock_authenticate_blueprint.route('/stock_authenticate', methods=['POST'])
def stock_authenticate():
    stock = request.form["stock"].upper()
    response = requests.get(config.BASE_URL + f'/v2/assets/{stock}', headers=headers)
    if response.status_code == 200:
        return f"{stock} is a valid stock."
    else:
        return f"{stock} does not exist."
    
# Admin Authenticate Account
@account_authenticate_blueprint.route('/account_authenticate', methods=['POST'])
def account_authenticate():
    username = request.form["account"]
    account = accounts.find_one({'username': username})
    if account:
        return f"{username} exists in the database!"
    else:
        return f"{username} does not exist in the database."