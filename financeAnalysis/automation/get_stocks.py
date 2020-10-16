# Look into Airflow for scheduling https://www.saturncloud.io/s/job-scheduling-with-python/
import bs4 as bs
import pickle
import requests
import datetime as dt
from datetime import timedelta
from time import sleep
import os
import pandas as pd
import numpy as np
from pandas_datareader import data as web
from pandas_datareader._utils import RemoteDataError
from financeAnalysis.models import StockTicker, StockTickerHistory
from .get_plots import make_plots

def save_sp500_tickers():
    wikipediaLink = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(wikipediaLink)
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    dates = []
    start = dt.datetime(2010, 1, 1)
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        date = row.findAll('td')[6].text
        if(date):
            date = dt.datetime.strptime(date[:10], "%Y-%m-%d")
        else:
            date = start
        tickers.append(ticker[:-1])
        dates.append(date)
    tickersDF = pd.DataFrame()
    tickersDF['StartDate'] = dates
    tickersDF['Ticker'] = tickers.replace('.','-')
    tickersDF.to_pickle("stock_dfs/sp500tickers.pickle")
    return tickersDF

def backpopulate_stock_history_2015():
    start = dt.datetime(2015, 1, 1)
    for stock in StockTicker.objects.all():
        if not StockTickerHistory.objects.filter(symbol_id=stock.id).first():
            write_stock_history_to_database(stock.id, start)

def write_stock_history_to_database(row, start):
    end = dt.datetime.now()
    if start is None:
        start=end - timedelta(days=5)
    print('Fetching {}  on {}'.format(row, start))
    try:
        df = web.get_data_yahoo(row.replace('.','-'), start=start, end=end)
        df.reset_index(inplace=True)
        df.set_index("Date", inplace=True)
        for i in df.iterrows():
            stock_history = StockTickerHistory(symbol_id=row, close=i[1]['Close'],
                                           low=i[1]['Low'], high=i[1]['High'],
                                           open=i[1]['Open'], volume=i[1]['Volume'],
                                           adjusted_close=i[1]['Adj Close'], updated_on=i[0])
            stock_history.save()
    except RemoteDataError:
        print('remote error ' + row)
    except KeyError:
        print('key error ' + row)

#Market Cap = Value = (number of outstanding Shares * Price)

def compile_data_to_columns():
    with open("stock_dfs/sp500tickers.pickle","rb") as f:
        tickers = pickle.load(f)
    main_df = pd.DataFrame()
    for count, ticker in enumerate(tickers['Ticker']):
        with open('stock_dfs/{}.pickle'.format(ticker),"rb") as f:
          df = pickle.load(f)
        df.set_index('Date', inplace=True)

        df.rename(columns = {'Adj Close': ticker}, inplace=True)
        df.drop(['Open','High','Low','Close','Volume'], 1, inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')
    if not os.path.exists('stock_dfs/sp500_adjcloses.csv'):
        main_df.to_csv('stock_dfs/sp500_adjcloses.csv')
    else:
        os.remove('stock_dfs/sp500_adjcloses.csv')
        main_df.to_csv('stock_dfs/sp500_adjcloses.csv')
