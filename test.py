from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest# Create stock historical data client
from alpaca.data.timeframe import TimeFrame

symbol = 'SQ'

api_key = 'PKKGOJVLCT940S5H4D0Y'
api_secret = 'D9ZeBqR3oo0SqXk3xUF0qMx3GgzOkEygirYpQITM'
client = StockHistoricalDataClient(api_key, api_secret)# Create request
request_params = StockLatestQuoteRequest(symbol_or_symbols=[symbol],
                                         timeframe=TimeFrame.Day
                                        )
latest_ask_price = client.get_stock_latest_trade(request_params)

print(latest_ask_price.get(symbol).price)