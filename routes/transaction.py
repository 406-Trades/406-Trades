from flask import Flask, Blueprint, render_template, redirect, url_for, request, session, jsonify
from classes.account import Account
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
from datetime import date
from datetime import timedelta

import classes.config as config

class Transaction:
    def __init__(self):
        # Connect to the Alpaca API
        self.api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, "https://paper-api.alpaca.markets/")
        self.headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

        # Blueprints
        self.update_balance_blueprint = Blueprint('update_balance', __name__)
        self.buy_stock_blueprint = Blueprint('buy_stock', __name__)
        self.home_buy_blueprint = Blueprint('home_buy', __name__)
        self.sell_stock_blueprint = Blueprint('sell_stock', __name__)
        self.save_stock_blueprint = Blueprint('save_stock', __name__)
        self.search_stock_blueprint = Blueprint('search_stock', __name__)
        self.filter_stock_blueprint = Blueprint('filter_stock', __name__)

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
                return render_template('home.html',username=username,b=b+amount,i=acc.get_invest(), amount=0, stocks=acc.get_stocks(), saved=acc.get_saved(), companies={})
            amount = 0

        # Purchase Stock
        @self.buy_stock_blueprint.route('/buy_stock', defaults={'exchange': {}})
        @self.buy_stock_blueprint.route('/buy_stock', methods=['GET', 'POST'])
        def buy_stock():
            # GET's User Data
            username = request.args.get('username')
            symbol = request.args.get('symbol')
            source = request.args.get('from')
            exchange = request.args.get('exchange')

            isSearch = False
            showStock = False

            if source == 'filter':
                shares = int(request.form['filter-amount'])
                companies = self.render_filter(exchange)
            elif source == 'search':
                shares = int(request.form['search-amount'])
                try:
                    price, name = self.render_search(symbol)
                except:
                    price=None
                    name=None
                isSearch = True
                showStock = True
                companies = {}
            else:
                shares = 0

            if (shares < 0):
                    return render_template('market.html', username=username, showStock=showStock, symbol=symbol, error='Invalid Stock Quantity', errorSymbol=symbol, price=price, name=name, companies=companies, exchange=exchange, isSearch=isSearch)

            if self.check_buy(username, symbol, shares):
                return render_template('market.html', username=username, showStock=showStock, symbol=symbol, companies=companies, exchange=exchange, price=price, name=name, errorSymbol=symbol, success=True, isSearch=isSearch)

            else:
                return render_template('market.html', username=username, showStock=showStock, symbol=symbol, error='Insufficient Balance', errorSymbol=symbol, price=price, name=name, companies=companies, exchange=exchange, isSearch=isSearch)


        # Purchase Stock
        @self.home_buy_blueprint.route('/home_buy', methods=['GET', 'POST'])
        def home_buy():
            # GET's User Data
            username = request.args.get('username')
            acc = Account(username)
            symbol = request.args.get('symbol')
            shares = int(request.form['watchlist-amount'])

            # Calculates Value of Stocks User Wishes to Buy 
            amount = float(self.api.get_latest_trade(symbol).price) * shares
            if (shares > 0 and shares <= acc.get_balance()):
                # Updates Owned Stocks in Account Object and DB
                acc.buy_stock(symbol, shares)
                acc.withdraw(amount)

                # return redirect(url_for('home', username=username, b=acc.get_balance(), i=acc.get_invest(), stocks=acc.get_stocks(), saved=acc.get_saved(), symbol=symbol))
                return render_template('home.html', username=username, b=acc.get_balance(), i=acc.get_invest(), stocks=acc.get_stocks(), saved=acc.get_saved())
            
            else:
                # Error Handling
                if (shares < 0):
                    return render_template('home.html', username=username, error='Invalid Stock Quantity', errorSymbol=symbol, b=acc.get_balance(),
                                            i=acc.get_invest(), stocks=acc.get_stocks(), saved=acc.get_saved())
                elif (amount > acc.get_balance()):
                    return render_template('home.html', username=username, error='Insufficient Balance', errorSymbol=symbol, b=acc.get_balance(), 
                                            i=acc.get_invest(), stocks=acc.get_stocks(), saved=acc.get_saved())
                else:
                    return render_template('home.html', username=username, error='System Error', errorSymbol=symbol, b=acc.get_balance(), 
                                            i=acc.get_invest(), stocks=acc.get_stocks(), saved=acc.get_saved())

        # Sell Stock
        @self.sell_stock_blueprint.route('/sell_stock', defaults={'exchange': {}})
        @self.sell_stock_blueprint.route('/sell_stock', methods=['GET', 'POST'])
        def sell_stock():
            # GET's User Data
            username = request.args.get('username')
            symbol = request.args.get('symbol')
            source = request.args.get('from')
            exchange = request.args.get('exchange')

            isSearch = False
            showStock = False

            if source == 'filter':
                shares = int(request.form['filter-amount'])
                companies = self.render_filter(exchange)
            elif source == 'search':
                shares = int(request.form['search-amount'])
                try:
                    price, name = self.render_search(symbol)
                except:
                    price=None
                    name=None
                showStock = True
                isSearch = True
                companies = {}
            else:
                shares = 0

            if (shares < 0):
                return render_template('market.html', username=username, showStock=showStock, symbol=symbol, error='Invalid Stock Quantity', errorSymbol=symbol, price=price, name=name, companies=companies, exchange=exchange, isSearch=isSearch)

            if self.check_sell(username, symbol, shares):
                return render_template('market.html', username=username, showStock=showStock, symbol=symbol, companies=companies, exchange=exchange, price=price, name=name, errorSymbol=symbol, success=True, isSearch=isSearch)

            else:
                return render_template('market.html', username=username, showStock=showStock, symbol=symbol, error='Insufficient Stock Holdings', errorSymbol=symbol, price=price, name=name, companies=companies, exchange=exchange, isSearch=isSearch)


        # Save Stock
        @self.save_stock_blueprint.route('/save_stock', methods=['GET', 'POST'])
        def save_stock():
            # GET's User Data
            username = request.args.get('username')

            acc = Account(username)
            symbol = request.args.get('symbol')

            source = request.args.get('from')
            exchange = request.args.get('exchange')

            isSearch = False

            if source == 'filter':
                companies = self.render_filter(exchange)
            else:
                try:
                    price, name = self.render_search(symbol)
                except:
                    price=None
                    name=None
                isSearch = True
                companies = {}

            # Save stock to user's watchlist
            acc.save_stock(symbol)

            return render_template('market.html', username=username, showStock=True, symbol=symbol, errorSymbol=symbol, price=price, name=name, success=True, isSearch=isSearch, companies=companies)

        # Search Stock
        @self.search_stock_blueprint.route('/search_stock', methods=['GET', 'POST'])
        def search_stock():
            # GET's User Data
            username = request.args.get('username')
            try:
                symbol = request.form['stock_search'].upper()
            except:
                symbol = request.args.get('symbol')
            time = request.args.get('time')

            get_search = self.render_search(symbol)

            isSearch = True

            # Check if error occurs when finding stock
            if get_search == None:
                
                return render_template('market.html', username=username, symbol=symbol, error='Stock not found', errorSymbol=symbol, isSearch=isSearch, companies={}, time=time)
            # Otherwise the stock exists. Displays buy, sell and save options
            else:
                price = get_search[0]
                name = get_search[1]
                get_chart = self.render_chart(symbol, time)

                if get_chart == None:
                    labels = []
                    values = []
                else:
                    labels, values = get_chart

                return render_template('market.html', username=username, showStock=True, symbol=symbol, price=price, name=name, isSearch=isSearch, companies={}, labels=labels, values=values, showChart=True, time=time)

        # Filter Stock
        @self.filter_stock_blueprint.route('/filter_stock', methods=['GET', 'POST'])
        def filter_stock():
            # GET's User Data
            username = request.args.get('username')
            exchange = request.args.get('exchange')
            
            # Get matching stocks and render them
            matching_stocks = self.render_filter(exchange)

            return render_template('market.html', username=username, companies=matching_stocks, exchange=exchange)
            

    def check_buy(self, username, symbol, shares):
        # GET's User Data
        acc = Account(username)

        # Calculates Value of Stocks User Wishes to Buy 
        amount = float(self.api.get_latest_trade(symbol).price) * shares
        if (shares > 0 and amount <= acc.get_balance()):
            acc.buy_stock(symbol, shares)
            acc.withdraw(amount)
            
            return True
        else:
            return False

    def check_sell(self, username, symbol, shares):
         # GET's User Data
        acc = Account(username)

        # Calculates Value of Stocks User Wishes to Buy 
        amount = float(self.api.get_latest_trade(symbol).price) * shares
        if (shares > 0 and shares <= acc.get_shares(symbol)):
            # Updates Owned Stocks in Account Object and DB
            acc.sell_stock(symbol, shares)
            acc.deposit(amount)
            
            return True
        else:
            return False
    
    def render_filter(self, exchange):
        active_assets = self.api.list_assets(status="active")
        matching_stocks = {}

        if exchange == "Any":
            assets = active_assets
        else:
            assets = [a for a in active_assets if a.exchange == exchange]

        for asset in assets[:50]:
            try:
                price = self.api.get_latest_trade(asset.symbol).price
                matching_stocks[asset.symbol] = [asset.name, '{0:.2f}'.format(price)]
            except:
                continue

        return matching_stocks

    def render_search(self, symbol):
        symbol = symbol.upper()

        try:
            get_price = self.api.get_latest_trade(symbol.upper()).price
            get_name = self.api.get_asset(symbol).name

            return get_price, get_name
        except:
            return None
        
    def render_chart(self, symbol, time):
        symbol = symbol.upper()

        try:
            labels = []
            values = []
            get_history = self.api.get_bars(symbol, TimeFrame.Day, start=date.today() - timedelta(days = int(time)), end=date.today() - timedelta(days = 1), adjustment='raw')
            for h in get_history:
                labels.append(str(h.t)[:10])
                values.append(round(h.c, 2))

            return labels, values
        except:
            return None