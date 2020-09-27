
import numpy as np
import pandas as pd
import pandas_datareader as web

from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pickle

def decisionTreePredictPrice(ticker):
    # collect the data
    with open("stock_dfs/{}.pickle".format(ticker), "rb") as f:
        tickers = pickle.load(f)
    future_days = 25
    #Create a new column (target) shifted 'x' units/days up
    tickers['Prediction'] = tickers['Adj Close'].shift(-future_days)
    #print(df.head(4))
    #print(df.tail(4))

    #Create the feature set and convert it to numpy array and remove the last 'x' days
    X = np.array(tickers.drop(['Prediction'], 1))[:-future_days]

    #Create target data set (y) and convert to numpy array and get all target values except last 'x' days
    y = np.array(tickers['Prediction'])[:-future_days]

    #split data into 75% training and 25% testing
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

    #create the decisiontree regressor model and linear regression model
    tree = DecisionTreeRegressor().fit(x_train, y_train)
    lr = LinearRegression().fit(x_train, y_train)

    #Get the last 'x' rows of the feature data set
    x_future = tickers.drop(['Prediction'], 1)[:-future_days]
    x_future = x_future.tail(future_days)
    x_future = np.array(x_future)

    #show the model tree prediction
    tree_prediction = tree.predict(x_future)
    #Show the model linear regression prediction
    lr_prediction = lr.predict(x_future)

    #Visualize the data
    predictions = tree_prediction

    valid = tickers[X.shape[0]:]
    valid['Predictions'] = predictions
    return tickers, valid

#plt.show()