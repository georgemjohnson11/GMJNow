# Look into Airflow for scheduling https://www.saturncloud.io/s/job-scheduling-with-python/
import bs4 as bs
import pickle
import requests
import datetime as dt
from datetime import datetime as dt_dt
from time import sleep
import os
import pandas as pd
import numpy as np
import pandas_datareader.data as web
from pandas_datareader._utils import RemoteDataError
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
    with open("stock_dfs/sp500tickers.pickle", "wb") as f:
        pickle.dump(tickersDF, f)
    return tickersDF

def save_nasdaq_ticker():
    tickersDF = pd.read_csv('nasdaq-listed-symbols_csv.csv')
    with open("nasdaqtickers.pickle", "wb") as f:
        pickle.dump(tickersDF["Symbol"].replace('.','-'), f)
    return tickersDF["Symbol"].replace('.','-')

def save_nyse_ticker():
    tickersDF = pd.read_csv('nyse-listed_csv.csv')
    with open("nasdaqtickers.pickle", "wb") as f:
        pickle.dump(tickersDF["ACT Symbol"].replace('.','-'), f)
    return tickersDF["ACT Symbol"].replace('.','-')

def get_data_from_yahoo(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open("stock_dfs/sp500tickers.pickle", "rb") as f:
            tickers = pickle.load(f)


    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    end = dt.datetime.now()
    start = dt.datetime(2015, 1, 1)
    for row in save_nyse_ticker():
        write_to_csv_pickle_no_date(row, start)
        if os.path.exists('stock_dfs/{}.pickle'.format(row)):
            make_plots(row)
    for row in save_nasdaq_ticker():
        write_to_csv_pickle_no_date(row, start)
        if os.path.exists('stock_dfs/{}.pickle'.format(row)):
            make_plots(row)
    for row in tickers.iterrows():
        write_to_csv_pickle_no_date(row[1]['Ticker'], start=row[1]['StartDate'])
        if os.path.exists('stock_dfs/{}.pickle'.format(row)):
            make_plots(row)


def write_to_csv_pickle_no_date(row, start):
    end = dt.datetime.now()
    start = dt.datetime(2015, 1, 1)
    if not os.path.exists('stock_dfs/{}.csv'.format(row)):
        try:
            df = web.DataReader(row, data_source='yahoo', start=start, end=end)
            df.reset_index(inplace=True)
            df.set_index("Date", inplace=True)
            df.to_csv('stock_dfs/{}.csv'.format(row))
            with open("stock_dfs/{}.pickle".format(row), "wb") as f:
                pickle.dump(df, f)
                sleep(1)
        except RemoteDataError:
            print('remote error ' + row)
        except KeyError:
            print('key error ' + row)
    else:
        print('Already have {}'.format(row))
        try:
            os.remove('stock_dfs/{}.csv'.format(row))
            df = web.DataReader(row, data_source='yahoo', start=start, end=end)
            df.reset_index(inplace=True)
            df.set_index("Date", inplace=True)
            df.to_csv('stock_dfs/{}.csv'.format(row))
            with open("stock_dfs/{}.pickle".format(row), "wb") as f:
                pickle.dump(df, f)
                sleep(1)
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
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
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

get_data_from_yahoo()
compile_data_to_columns()
