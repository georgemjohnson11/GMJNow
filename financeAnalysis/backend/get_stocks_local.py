# Look into Airflow for scheduling adn Media Root https://www.saturncloud.io/s/job-scheduling-with-python/
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
import matplotlib.pyplot as plt
from matplotlib import style
from pandas_datareader._utils import RemoteDataError

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
    tickersDF['Ticker'] = tickers
    with open("sp500tickers.pickle", "wb") as f:
        pickle.dump(tickersDF, f)
    return tickersDF

def save_nasdaq_ticker():
    tickersDF = pd.read_csv('nasdaq-listed-symbols_csv.csv')
    with open("nasdaqtickers.pickle", "wb") as f:
        pickle.dump(tickersDF, f)
    return tickersDF["Symbol"].replace('.','-')

def save_nyse_ticker():
    tickersDF = pd.read_csv('nyse-listed_csv.csv')
    with open("nasdaqtickers.pickle", "wb") as f:
        pickle.dump(tickersDF, f)
    return tickersDF["ACT Symbol"].replace('.','-')

def get_data_from_yahoo(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open("stock_dfs/sp500tickers.pickle", "rb") as f:
            tickers = pickle.load(f)


    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    start = dt.datetime(2015, 1, 1)
    end = dt.datetime.now()
    for row in save_nyse_ticker():
        if not os.path.exists('stock_dfs/{}.csv'.format(row)):
            try:
                df = web.DataReader(row, data_source='yahoo', start=start, end=end)
                df.fillna(inplace=True)
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

    for row in save_nasdaq_ticker():
        if not os.path.exists('stock_dfs/{}.csv'.format(row)):
            try:
                df = web.DataReader(row, data_source='yahoo', start=start, end=end)
                df.fillna(inplace=True)
                df.reset_index(inplace=True)
                df.set_index("Date", inplace=True)
                df.to_csv('stock_dfs/{}.csv'.format(row))
                with open("stock_dfs/{}.pickle".format(row), "wb") as f:
                    pickle.dump(df, f)
                    sleep(1)

            except RemoteDataError:
                print('remote error '+ row)

            except KeyError:
                print('key error ' + row)
        else:
            print('Already have {}'.format(row))
    for row in tickers.iterrows():
        tickerName = row[1]['Ticker'].replace('.','-')
        print(tickerName)
        # just in case your connection breaks, we'd like to save our progress!
        if not os.path.exists('stock_dfs/{}.csv'.format(row)):
            df = web.DataReader(tickerName, data_source='yahoo', start=row[1]['StartDate'], end=end)
            df.reset_index(inplace=True)
            df.set_index("Date", inplace=True)
            df.to_csv('stock_dfs/{}.csv'.format(row[1]['Ticker']))
            with open("stock_dfs/{}.pickle".format(tickerName), "wb") as f:
                pickle.dump(df, f)
        else:
            print('Already have {}'.format(tickerName))

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
    main_df.to_csv('stock_dfs/sp500_adjcloses.csv')

def visualize_correlation_data():
    df = pd.read_csv('stock_dfs/sp500_adjcloses.csv')

    #ToDo take correlations to correlate related and disrelated stocks
    df_corr = df.corr()

    #Setup Figure for heatmap
    data = df_corr.values
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_corr.columns
    row_labels = df_corr.index

    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap.set_clim(-1,1)
    plt.tight_layout()
    plt.show()
def visualize_covariance_data():
    df = pd.read_csv('stock_dfs/sp500_adjcloses.csv')

    #ToDo take covariance to correlate related and disrelated stocks
    df_cov = df.cov()

    #Setup Figure for heatmap
    data = df_cov.values
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_cov.columns
    row_labels = df_cov.index

    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


get_data_from_yahoo()
