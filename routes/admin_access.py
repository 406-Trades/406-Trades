from flask import Flask, Blueprint, render_template, redirect, url_for, request, session, jsonify
from classes.account import Account
import alpaca_trade_api as tradeapi
import classes.config as config
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import requests

class Admin_Access():
    def __init__(self):
        # Accounts DB
        self.cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.cluster["406-Trades"]
        self.accounts = self.db["Accounts"]

        # Connect to the Alpaca API
        self.api = tradeapi.REST(config.API_KEY, config.SECRET_KEY)
        self.headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

        # Blueprints
        self.edit_account_blueprint = Blueprint('edit_account', __name__)
        self.stock_authenticate_blueprint = Blueprint('stock_authenticate', __name__)
        self.account_authenticate_blueprint = Blueprint('account_authenticate', __name__)

        # Admin Edit/Delete Account / Stocks for all Accounts in DB
        @self.edit_account_blueprint.route('/edit_account', methods=['GET', 'POST'])
        def edit_account():
            # username = request.args.get('username')
            id = request.args.get('id')
            # account = self.accounts.find_one({'_id': ObjectId(id)})
            if request.method == 'POST':
                # Deletes account from DB
                if request.form['submit'] == 'Delete':
                    self.accounts.delete_one({'_id': ObjectId(id)})
                # Update the account in MongoDB
                elif request.form['submit'] == 'Save':
                    self.accounts.update_one({'_id': ObjectId(id)}, {'$set': {
                        'username': request.form['username'],
                        'balance': float(request.form['balance']),
                        'investments': float(request.form['investments']),
                        'stocks': json.loads(request.form['stocks'].replace("'", "\"")),
                        'saved': request.form['saved'].strip('][').split(', ')
                    }})
            allAccounts = self.accounts.find({'username': {'$ne': 'admin'}})
            return render_template('admin/admin_accounts.html', username=session['username'], allAccounts=allAccounts)

        # Admin Authenticate Stock
        @self.stock_authenticate_blueprint.route('/stock_authenticate', methods=['POST'])
        def stock_authenticate():
            stock = request.form["stock"].upper()
            response = requests.get(config.BASE_URL + f'/v2/assets/{stock}', headers=self.headers)
            if response.status_code == 200:
                return f"<p style='color: green;'>{stock} is a valid stock.</p>"
            else:
                return f"<p style='color: red;'>{stock} does not exist.</p>"
            
        # Admin Authenticate Account
        @self.account_authenticate_blueprint.route('/account_authenticate', methods=['POST'])
        def account_authenticate():
            username = request.form["account"]
            account = self.accounts.find_one({'username': username})
            if account:
                return f"<p style='color: green;'>{username} exists in the database!</p>"
            else:
                return f"<p style='color: red;'>{username} does not exist in the database.</p>"