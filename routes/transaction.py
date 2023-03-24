from flask import Flask, Blueprint, render_template, redirect, url_for, request, session, jsonify
from classes.account import Account
import alpaca_trade_api as tradeapi
import classes.config as config
import json

class Transaction:
    def __init__(self):
        # Connect to the Alpaca API
        self.api = tradeapi.REST(config.API_KEY, config.SECRET_KEY)
        self.headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

        # Blueprints
        self.update_balance_blueprint = Blueprint('update_balance', __name__)
        self.buy_stock_blueprint = Blueprint('buy_stock', __name__)
        self.sell_stock_blueprint = Blueprint('sell_stock', __name__)
        self.save_stock_blueprint = Blueprint('save_stock', __name__)

        # Declare Routes for Transaction Class
        # Updates the Balance of the account (positive amount is deposit and negative is withdraw)
        @self.update_balance_blueprint.route('/update_balance', methods=['GET', 'POST'])
        def update_balance():
            username = request.args.get('username')
            acc = Account(username)
            amount = request.form['amount']
            if(amount.isdigit()):
                amount = float(amount)
            else:
                return render_template('home.html',username=username,b=acc.get_balance(),i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved(), error='Invalid Balance Input')
            if amount > 0:
                b = float(request.args.get('b'))
                # Add money
                if request.form['submit-button'] == 'Increment':
                    acc.deposit(amount)
                # Remove money
                else:
                    if amount > acc.get_balance():
                        return render_template('home.html',username=username,b=acc.get_balance(),i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved(), error='Exceeding Balance Funds')
                    else:
                        acc.withdraw(amount)
                        amount= amount * -1
                return render_template('home.html',username=username,b=b+amount,i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved())
            amount = 0

        # Purchase Stock
        @self.buy_stock_blueprint.route('/buy_stock', methods=['GET', 'POST'])
        def buy_stock():
            # GET's User Data
            username = request.args.get('username')
            acc = Account(username)
            symbol = request.args.get('symbol')
            shares = request.form['buy-amount']
            if(not shares.isdigit()):
                return render_template('home.html', username=username, error='Invalid Input', errorSymbol=symbol,b=acc.get_balance(),i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved())
            else:
                print("here")
                shares = int(shares)
                # Calculates Value of Stocks User Wishes to Buy 
                amount = float(self.api.get_latest_trade(symbol).price) * shares
                if (shares > 0 and amount <= acc.get_balance()):
                    # Updates Owned Stocks in Account Object and DB
                    acc.buy_stock(symbol, shares)
                    acc.withdraw(amount)
                    # FIX SO IT REDIRECTS TO PREV PAGE
                    return redirect(request.referrer)
                else:
                    # Error Handling
                    if (shares < 0):
                        return render_template('home.html', username=username, error='Invalid Stock Quantity', errorSymbol=symbol, b=acc.get_balance(),i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved())
                    elif (amount > acc.get_balance()):
                        return render_template('home.html', username=username, error='Insufficient Balance', errorSymbol=symbol, b=acc.get_balance(),i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved())

        # Sell Stock
        @self.sell_stock_blueprint.route('/sell_stock', methods=['GET', 'POST'])
        def sell_stock():

            return redirect(url_for('market'))

        # Save Stock
        @self.save_stock_blueprint.route('/save_stock', methods=['GET', 'POST'])
        def save_stock():

            return redirect(url_for('market'))