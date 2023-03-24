from flask import Flask, Blueprint, render_template, redirect, url_for, request, session, jsonify
from classes.account import Account
import alpaca_trade_api as tradeapi
import classes.config as config
import json

# Connect to the Alpaca API
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, "https://paper-api.alpaca.markets/")
headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

# Blueprints
update_balance_blueprint = Blueprint('update_balance', __name__)
buy_stock_blueprint = Blueprint('buy_stock', __name__)
sell_stock_blueprint = Blueprint('sell_stock', __name__)
save_stock_blueprint = Blueprint('save_stock', __name__)
search_stock_blueprint = Blueprint('search_stock', __name__)
filter_stock_blueprint = Blueprint('filter_stock', __name__)

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
        return render_template('home.html',username=username,b=acc.get_balance(),i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved(), companies={})
    amount = 0

# Purchase Stock
@buy_stock_blueprint.route('/buy_stock', methods=['GET', 'POST'])
def buy_stock():
    # GET's User Data
    username = request.args.get('username')
    acc = Account(username)
    symbol = request.args.get('symbol')
    source = request.args.get('from')
    if source == 'filter':
        shares = int(request.form['filter-amount'])
    elif source == 'search':
        shares = int(request.form['search-amount'])
    else:
        shares = 0
    # Calculates Value of Stocks User Wishes to Buy 
    amount = float(api.get_latest_trade(symbol).price) * shares
    if (shares > 0 and shares <= acc.get_balance()):
        # Updates Owned Stocks in Account Object and DB
        acc.buy_stock(symbol, shares)
        acc.withdraw(amount)
        return redirect(url_for('market', username=username, symbol=symbol, companies={}))
    else:
        # Error Handling
        if (shares < 0):
            return render_template('market.html', username=username, error='Invalid Stock Quantity', errorSymbol=symbol, companies={})
        elif (amount > acc.get_balance()):
            return render_template('market.html', username=username, error='Insufficient Balance', errorSymbol=symbol, companies={})

# Sell Stock
@sell_stock_blueprint.route('/sell_stock', methods=['GET', 'POST'])
def sell_stock():
    # GET's User Data
    username = request.args.get('username')
    acc = Account(username)
    symbol = request.args.get('symbol')

    source = request.args.get('from')
    if source == 'filter':
        shares = int(request.form['filter-amount'])
    elif source == 'search':
        shares = int(request.form['search-amount'])
    else:
        shares = 0
    # Calculates Value of Stocks User Wishes to Sell 
    amount = float(api.get_latest_trade(symbol).price) * shares
    print(acc.get_shares(symbol))
    if (shares <= acc.get_shares(symbol)):
        # Updates Owned Stocks in Account Object and DB
        acc.sell_stock(symbol, shares)
        acc.deposit(amount)
        return redirect(url_for('market', username=username, symbol=symbol, companies={}))
    else:
        # Error Handling
        if (shares < 0):
            return render_template('market.html', username=username, error='Invalid Stock Quantity', errorSymbol=symbol, companies={})
        elif (shares > acc.get_shares(symbol)):
            return render_template('market.html', username=username, error='Insufficient Shares', errorSymbol=symbol, companies={})


    return redirect(url_for('market'))

# Save Stock
@save_stock_blueprint.route('/save_stock', methods=['GET', 'POST'])
def save_stock():
    # GET's User Data
    username = request.args.get('username')

    acc = Account(username)
    symbol = request.args.get('symbol')

    # Save stock to user's watchlist
    acc.save_stock(symbol)

    return render_template('market.html', username=username, symbol=symbol, companies={})

# Search Stock
@search_stock_blueprint.route('/search_stock', methods=['GET', 'POST'])
def search_stock():
    # GET's User Data
    username = request.args.get('username')
    symbol = request.form['stock_search'].upper()

    # Checks for if the stock exists. If it does, it displays buy, sell and save options
    try:
        get_stock = api.get_latest_trade(symbol.upper()).price
        stock_name = api.get_asset(symbol).name

        return render_template('market.html', username=username, showStock="True", symbol=symbol.upper(), price=get_stock, name=stock_name, companies={})
    # Otherwise, an error is outputted
    except:
        return render_template('market.html', username=username, error='Stock not found', errorSymbol=symbol, companies={})

# Filter Stock
@filter_stock_blueprint.route('/filter_stock', methods=['GET', 'POST'])
def filter_stock():
    # GET's User Data
    username = request.args.get('username')
    exchange = request.args.get('exchange')
    active_assets = api.list_assets(status="active")
    matching_stocks = {}

    if exchange == "Any":
        assets = active_assets
    else:
        assets = [a for a in active_assets if a.exchange == exchange]

    for asset in assets[:50]:
        try:
            price = api.get_latest_trade(asset.symbol).price
            matching_stocks[asset.symbol] = [asset.name, price]
        except:
            continue


    return render_template('market.html', username=username, companies=matching_stocks)