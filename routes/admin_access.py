from flask import Flask, Blueprint, render_template, redirect, url_for, request, session, jsonify
from classes.account import Account
import alpaca_trade_api as tradeapi
import classes.config as config
import pymongo
from pymongo import MongoClient
import json

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

# Blueprints
edit_account_blueprint = Blueprint('edit_account', __name__)

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