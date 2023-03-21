import pymongo
from pymongo import MongoClient
import alpaca_trade_api as tradeapi
import requests
import classes.config as config

# Connect to the Alpaca API
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY)
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
                updatedInvest += float(api.get_latest_trade(symbol).price) * float(quantity)
        
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
        return self.balance
    
    def get_invest(self):
        return self.acc['investments']
    
    def get_stocks(self):
        return self.stocks

    def get_saved(self):
        return self.saved
    
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

    # Save Stock for given Account
    def save_stock(self, symbol):
        saved = self.saved
        accounts.update_one({"username" : self.username}, {"$set" : {"stocks" : saved.append(symbol)}})