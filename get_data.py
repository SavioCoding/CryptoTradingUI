# import required module
import os
import pandas as pd
from binance.client import Client
from testnet_api import testnet_api_key, testnet_secret_key
from datetime import date, timedelta
import random
import plotly.express as px
import datetime
import json

def get_returns_df(symToUnits_directory):
    return_dict = {}
    for filename in os.listdir(symToUnits_directory):
        df = pd.read_csv(symToUnits_directory + '/' + filename, index_col=[0])
        strategy = filename[:-4]
        df["total units (usdt)"] = df.sum(axis=1)
        df["portfolio_return"] = df["total units (usdt)"].pct_change()
        df["portfolio_return"] = df["portfolio_return"].fillna(0)
        df["cumulative return"] = (1 + df["portfolio_return"]).pow(len(df.index))
        df["cumulative return"] = df["cumulative return"].round(3)
        return_dict[strategy] = df
    return return_dict

def get_currorders_df(order_directory, symToUnits_directory, testnet_api_key, testnet_secret_key):
    # assign directory
    data_dict = {}
    client = Client(api_key = testnet_api_key, api_secret = testnet_secret_key, tld = "com", testnet = True)
    symbols = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "TRXUSDT", "XRPUSDT"]
    symbolsToPrice = {}

    for symbol in symbols:
        currentPrice = float(client.get_symbol_ticker(symbol=symbol)["price"])
        symbolsToPrice[symbol] = currentPrice
    # iterate over files in
    # that directory

    for filename in os.listdir(order_directory):
        symToUnits = pd.read_csv(symToUnits_directory + '/' + filename, index_col = [0])
        symToUnits_dict = symToUnits.tail(1).to_dict('records')[0]
        symbols = list(symToUnits.columns)
        df = pd.read_csv(order_directory + '/' + filename, index_col=[0])
        strategy = filename[:-4]
        currentPrices = []
        Profit_in_usdt = []
        Return_in_percent = []
        for orderId, row in df.iterrows():
            currentPrice = symbolsToPrice[row["symbol"]]
            currentUSDT = row["quote_units"] * (currentPrice/row["entry_price"])
            profit = currentUSDT - row["quote_units"]
            stratReturn = profit/row["quote_units"] * 100
            currentUSDT = round(currentUSDT, 3)
            profit = round(profit, 3)
            stratReturn = str(round(stratReturn, 3)) + "%"

            currentPrices.append(currentPrice)
            Profit_in_usdt.append(profit)
            Return_in_percent.append(stratReturn)
            symbols.remove(row['symbol'])

        df['quote_units'] = df['quote_units'].round(3)
        df['time'] = df['time'].str[:10]
        df['currentPrice'] = currentPrices
        df['Profit(usdt)'] = Profit_in_usdt
        df['return(%)'] = Return_in_percent

        for i in range(len(symbols)):
            df.loc[i] = [symbols[i], '-', 'NEUTRAL', '-', '-', symToUnits_dict[symbols[i]], strategy, symbolsToPrice[symbols[i]], float(0), '0.000%']

        total_usdt = float(sum(df['quote_units'].to_list()))

        total_profit = float(sum(Profit_in_usdt))
        total_return = (str("{:.3f}".format(round(total_profit/total_usdt * 100, 3)) + '%')) if total_usdt != 0 else '0.000%'
        total_profit = round(total_profit, 3)
        total_usdt = round(total_usdt, 3)
        df = df.astype(str)
        df.loc[len(df.index)] = ['Total', '-', '-', '-', '-', total_usdt, strategy,'-', total_profit, total_return]
        # df['Hold'] = '50.0'
        # df['Hold'].loc[len(df.index)-1] = '300.0'
        df['Profit(usdt)'].loc[len(df.index) - 1] = "{:.3f}".format(df['Profit(usdt)'].loc[len(df.index) - 1])
        data_dict[strategy] = df
        print(df)
    return data_dict












if __name__ == '__main__':
    # directory = '../currOrders'
    # data_dict = get_currorders_df(directory, testnet_api_key, testnet_secret_key)
    print(get_returns_df("../symToUnits"))

