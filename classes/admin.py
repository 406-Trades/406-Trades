from classes.account import Account
import classes.config as config
import alpaca_trade_api as tradeapi
import requests
import pymongo
from pymongo import MongoClient

# Accounts DB
cluster = MongoClient("mongodb+srv://Abhari:Abhari@cluster0.pqgawmw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["406-Trades"]
accounts = db["Accounts"]

# Connect to the Alpaca API
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY)
headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

# Admin Class, inherits Account Class Functionality
class Admin(Account):
    def __init__ (self, username):
        super().__init__(username)

    # Admin Access to All Accounts in DB
    def get_accounts(self):
        return list(accounts.find())
    
    # Admin Access to Authenticate Stock
    def auth_stock(self, symbol):
        response = requests.get(config.BASE_URL + f'/v2/assets/{symbol}', headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False