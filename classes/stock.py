# Stock info class --> stock symbol / price
import alpaca_trade_api as tradeapi
import classes.config as config
import requests

# Connect to the Alpaca API
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY)
headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

class Stock:
    # Initializing the stock
    def __init__ (self, symbol):
        self.symbol = symbol
        self.price = api.get_latest_trade(symbol).price
    
    # Checks for valid stock name
    def verify_stock(self, symbol):
        response = requests.get(config.BASE_URL + f'/v2/assets/{symbol}', headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False

    # Returns stock price
    def get_price(self):
        return self.price

    # Returns stock name
    def get_symbol(self):
        return self.symbol