from collections import Counter
from sklearn import svm, model_selection, neighbors
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.model_selection import cross_validate
import numpy as np
import pandas as pd
import pickle


#Percent Change based ML algorithm to BUY/Sell


def process_data_for_labels(ticker):
    hm_days = 7
    df = pd.read_csv('stock_dfs/sp500_adjcloses.csv', index_col=0)
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

def do_ml(ticker):
    with open("stock_dfs/sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)
    df = pd.read_csv('stock_dfs/sp500_adjcloses.csv', index_col=0)
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
        #pickle the predictions to save them for future training

        print('Predicted spread: ', Counter(predictions))
    else:
        confidence = "N/A"
        predictions = "N/A"
    return confidence, Counter(predictions)

