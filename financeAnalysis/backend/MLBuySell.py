from collections import Counter
from sklearn import svm, model_selection, neighbors
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.model_selection import cross_validate
import numpy as np
import pandas as pd
from django.conf import settings
from datetime import datetime
from financeAnalysis.backend.portfolioManagement import getPortfolio
from financeAnalysis.models import StockTickerHistory, StockTicker
import bs4 as bs
import requests
import pandas as pd
import numpy as np


#Percent Change based ML algorithm to BUY/Sell

def save_sp500_tickers():
    wikipediaLink = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    resp = requests.get(wikipediaLink)
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    dates = []
    start = datetime(2010, 1, 1)
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        date = row.findAll('td')[6].text
        if(date):
            StockTicker.objects.update_or_create(id=ticker[:-1],
                                                 defaults={ 'active': True,
                                                            'is_currency':False,
                                                            'ipo_year': datetime.strptime(date[:10], "%Y-%m-%d") })
        tickers.append(ticker[:-1])
    tickersDF = pd.DataFrame()
    tickersDF['Ticker'] = tickers.replace('.','-')
    return tickersDF

#Market Cap = Value = (number of outstanding Shares * Price)

def compile_data_to_columns():
    tickers = save_sp500_tickers()
    main_df = pd.DataFrame()
    for count, ticker in enumerate(tickers['Ticker']):
        df = getPortfolio(ticker)
        df.rename(columns = {'symbol__stocktickerhistory__adjusted_close': ticker}, inplace=True)
        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')
    return main_df

def process_data_for_labels(ticker):
    hm_days = 7
    df = compile_data_to_columns()
    tickers = df.columns.values.tolist()
    df.fillna(0, inplace=True)

    for i in range(1, hm_days+1):
        #Value of percent change for (two days from now minus todays)/ today
        df['{}_{}d'.format(ticker,i)] = (df[ticker].shift(-i) -df[ticker])/ df[ticker]

    df.fillna(0, inplace=True)
    return tickers, df

def buy_sell_hold(*args):
    cols = [c for c in args]
    requirement = 0.02
    for col in cols:
        if col > requirement:
            return "BUY"
        if col < -requirement:
            return "SELL"
    return "HOLD"

def extract_feature_sets(ticker):
    tickers, df = process_data_for_labels(ticker)
    df['{}_target'.format(ticker)] = list(map(buy_sell_hold,
                                              df['{}_1d'.format(ticker)],
                                              df['{}_2d'.format(ticker)],
                                              df['{}_3d'.format(ticker)],
                                              df['{}_4d'.format(ticker)],
                                              df['{}_5d'.format(ticker)],
                                              df['{}_6d'.format(ticker)],
                                              df['{}_7d'.format(ticker)]))

    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]

    df.fillna(0, inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(inplace=True)

    #percent change from previous day
    df_vals = df[[ticker for ticker in tickers]].pct_change()
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)

    X = df_vals.values
    y = df['{}_target'.format(ticker)].values

    return X, y, df

def do_ml(ticker, date=datetime.today()):
    df = compile_data_to_columns()
    if ticker in df.columns:
        X, y, df = extract_feature_sets(ticker)

        X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size = 0.20)

        #clf =  neighbors.KNeighborsClassifier()
        clf = VotingClassifier([('lsvc', svm.LinearSVC()),
                                ('knn', neighbors.KNeighborsClassifier()),
                                ('rfor', RandomForestClassifier())])
        #Passing in the percent change and the
        clf.fit(X_train, y_train)
        confidence = clf.score(X_test, y_test)

        predictions = clf.predict(X_test)
        StockTickerHistory.objects.update_or_create(id=ticker, updated_on=date,
                                                    defaults={'ml_confidence': confidence, 'ml_predictions': Counter(predictions)})
    else:
        confidence = "N/A"
        predictions = "N/A"
    return predictions, confidence

