import pymongo
from pymongo import MongoClient
from alpaca.broker import BrokerClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
# import alpaca as tradeapi
import requests
import classes.config as config

# Connect to the Alpaca API
api = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)
# tradeapi.REST(config.API_KEY, config.SECRET_KEY)
headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

# Account Class to create account objects for every new user
class Account:
    def __init__ (self, username):
        self.acc = accounts.find_one({'username': username})
        self.username = username
        self.password = self.acc['password']
        self.balance = self.acc['balance']
        self.stocks = self.acc['stocks']
        self.saved = self.acc['saved']
        self.investments = self.calc_invest()
    
    # Balance Modifier Functions
    def deposit(self, amount):
        accounts.update_one({"username" : self.username}, {"$set" : {"balance" : self.balance + amount}})
        self.balance = self.acc['balance']

    def withdraw(self, amount):
        accounts.update_one({"username" : self.username}, {"$set" : {"balance" : self.balance - amount}})
        self.balance = self.acc['balance']
    
    # Calculate Account Investments
    def calc_invest(self):
        updatedInvest = 0
        for symbol, quantity in self.stocks.items():
            # Handles only valid stock symbols
            if requests.get(config.BASE_URL + f'/v2/assets/{symbol}', headers=headers).status_code == 200:
                # updatedInvest += (float(api.get_stock_latest_quote(symbol).ask_price) * float(quantity))

                multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
                latest_multisymbol_quotes = api.get_stock_latest_quote(multisymbol_request_params)
                latest_ask_price = latest_multisymbol_quotes[symbol].ask_price

                updatedInvest += latest_ask_price
        
        print(updatedInvest)
        # Update Account in DB
        accounts.update_one({"username" : self.username}, {"$set" : {"investments" : updatedInvest}})
        self.investments = updatedInvest

    # Getter Functions
    def get_account(self):
        return self.acc

    def get_username(self):
        return self.username
    
    def get_password(self):
        return self.password
    
    def get_balance(self):
        return round(self.balance, 2)
    
    def get_invest(self):
        return self.acc['investments']
    
    def get_stocks(self):
        return self.stocks

    def get_saved(self):
        return self.saved
    
    def get_shares(self, symbol):
        return self.stocks[symbol]
    
    # Setter Functions
    # Change Username
    def update_username(self, newUsername):
        accounts.update_one({"username" : self.username}, {"$set" : {"username" : newUsername}})
        self.username = newUsername
    # Change Password
    def update_password(self, newPassword):
        if self.password != newPassword:
            accounts.update_one({"password" : self.password}, {"$set" : {"password" : newPassword}})
            self.password = newPassword
    
    # Purchase Stock for given Account
    def buy_stock(self, symbol, shares):
        if shares > 0:
            newDict = self.stocks
            if symbol in self.stocks:
                newDict[symbol] += shares
            else:
                newDict[symbol] = shares
            accounts.update_one({"username" : self.username}, {"$set" : {"stocks" : newDict}})

    # Sell Stock for given Account
    def sell_stock(self, symbol, shares):
        if shares > 0:
            if (symbol in self.stocks) and (shares < newDict[symbol]):
                newDict[symbol] -= shares
            if newDict[symbol] == 0:
                accounts.delete_one({"username" : self.username}, {"$set" : {"stocks" : newDict}})
            else:
                accounts.update_one({"username" : self.username}, {"$set" : {"stocks" : newDict}})