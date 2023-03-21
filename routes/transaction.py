from flask import Flask, Blueprint, render_template, redirect, url_for, request, session, jsonify
from classes.account import Account
from alpaca.broker import BrokerClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
import classes.config as config
import json

# Connect to the Alpaca API
api = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)
headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

# Blueprints
update_balance_blueprint = Blueprint('update_balance', __name__)
buy_stock_blueprint = Blueprint('buy_stock', __name__)
sell_stock_blueprint = Blueprint('sell_stock', __name__)

# Updates the Balance of the account (positive amount is deposit and negative is withdraw)
@update_balance_blueprint.route('/update_balance', methods=['GET', 'POST'])
def update_balance():
    username = request.args.get('username')
    acc = Account(username)
    if len(request.form['amount']) > 0:
        amount = float(request.form['amount'])
        # Add money
        if request.form['submit-button'] == 'Increment':
            acc.deposit(amount)
        # Remove money
        else:
            acc.withdraw(amount)
        return render_template('home.html',username=username,b=acc.get_balance(),i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved())
    amount = 0

# Purchase Stock
@buy_stock_blueprint.route('/buy_stock', methods=['GET', 'POST'])
def buy_stock():
    # GET's User Data
    username = request.args.get('username')
    nasdaqData = json.loads(request.args.get('nasdaqData').replace("'", "\""))
    acc = Account(username)
    symbol = request.args.get('symbol')
    shares = int(request.form['nasdaq-amount'])
    # Calculates Value of Stocks User Wishes to Buy 

    multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
    latest_multisymbol_quotes = api.get_stock_latest_quote(multisymbol_request_params)
    latest_ask_price = latest_multisymbol_quotes[symbol].ask_price

    amount = float(latest_ask_price) * shares
    if (shares > 0 and shares <= acc.get_balance()):
        # Updates Owned Stocks in Account Object and DB
        acc.buy_stock(symbol, shares)
        acc.withdraw(amount)
        return redirect(url_for('market', username=username, nasdaqData=nasdaqData))
    else:
        # Error Handling
        if (shares < 0):
            return render_template('market.html', username=username, nasdaqData=nasdaqData, error='Invalid Stock Quantity', errorSymbol=symbol)
        elif (amount > acc.get_balance()):
            return render_template('market.html', username=username, nasdaqData=nasdaqData, error='Insufficient Balance', errorSymbol=symbol)

# Sell Stock
@sell_stock_blueprint.route('/sell_stock', methods=['GET', 'POST'])
def sell_stock():
    # GET's User Data
    username = request.args.get('username')
    nasdaqData = json.loads(request.args.get('nasdaqData').replace("'", "\""))
    acc = Account(username)
    symbol = request.args.get('symbol')
    shares = int(request.form['nasdaq-amount'])
    # Calculates Value of Stocks User Wishes to Sell 
    amount = float(StockLatestQuoteRequest(symbol).price) * shares
    if (shares <= acc.get_balance()):
        # Updates Owned Stocks in Account Object and DB
        acc.sell_stock(symbol, shares)
        acc.deposit(amount)
        return redirect(url_for('market', username=username, nasdaqData=nasdaqData))
    else:
        # Error Handling
        if (shares < 0):
            return render_template('market.html', username=username, nasdaqData=nasdaqData, error='Invalid Stock Quantity', errorSymbol=symbol)
        elif (shares > acc.get_shares(symbol)):
            return render_template('market.html', username=username, nasdaqData=nasdaqData, error='Insufficient Shares', errorSymbol=symbol)


    return redirect(url_for('market'))