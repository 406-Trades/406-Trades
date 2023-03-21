# Stock info class --> stock symbol / price
from alpaca.broker import BrokerClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
# import alpaca_trade_api as tradeapi
import classes.config as config
import requests

# Connect to the Alpaca API
api = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)
headers = {'APCA-API-KEY-ID': config.API_KEY, 'APCA-API-SECRET-KEY': config.SECRET_KEY}

class Stock:
    def __init__ (self, symbol):
        self.symbol = symbol
        self.price = StockLatestQuoteRequest(symbol).price
    
    # Checks for valid stock name
    def verifyStock(self, symbol):
        response = requests.get(config.BASE_URL + f'/v2/assets/{symbol}', headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False

    # Returns stock price
    def getPrice(self):
        return self.price