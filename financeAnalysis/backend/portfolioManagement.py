#Description: This is a python program for finance to show how to compute
#             simple returns, daily returns, and volatility for a portfolio

import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import pickle
from django.conf import settings
import os.path
from django.db.models.functions import TruncDate
from financeAnalysis.models import StockTicker, StockTickerHistory



#Get the stock symbols for the portfolio
##faang_stocks = ["FB", "AMZN", "AAPL", "NFLX", "GOOG"]
#stockStartDate = '2013-01-01'
#today = datetime.today().strftime('%Y-%m-%d')


#numAssets = len(faang_stocks)
#print('You have ' + str(numAssets) + ' assets in your portfolio.')

#Create a function to get stock prices and portfolio

def getPortfolio(stock_ticker_symbol, date=date.today()):
    df = pd.DataFrame(list(StockTickerHistory.objects
                           .filter(symbol_id = stock_ticker_symbol)
                           .filter(updated_on__lte=date)
                           .annotate(updated_date=TruncDate('updated_on'))
                           .values('updated_date', 'adjusted_close'))).set_index('updated_date')
    return df

def getPortfolioAdvanced(stock_ticker_symbol, date=date.today()):
    df = pd.DataFrame(list(StockTickerHistory.objects
                           .filter(symbol_id = stock_ticker_symbol)
                           .filter(updated_on__lte=date)
                           .values('updated_on', 'high', 'low', 'open', 'volume', 'adjusted_close'))).set_index('updated_on')
    return df

def getPortfolio_ml(stock_ticker_symbol, date=date.today()):
    df = pd.DataFrame(list(StockTickerHistory.objects
                           .filter(symbol_id = stock_ticker_symbol)
                           .filter(updated_on__lte=date)
                           .annotate(updated_date=TruncDate('updated_on'))
                           .values('updated_date', 'adjusted_close')))
    if 'updated_date' in df.columns:
        df.set_index('updated_date')
    return df

def getPortfolioDateTime(stock_ticker_symbol, date=date.today()):
    df = pd.DataFrame(list(StockTickerHistory.objects
                           .filter(symbol_id = stock_ticker_symbol)
                           .filter(updated_on__lte=date)
                           .values('updated_on', 'adjusted_close')))
    if 'updated_on' in df.columns:
        df['updated_on'] = pd.to_datetime(df['updated_on'])
        df.set_index('updated_on', inplace=True)
    return df

def showPortfolioGraph(stocks, col = 'Adj Close'):

    title = 'Portfolio ' + col + ' Price History'
    graphportfolio = getPortfolio(stocks)[col]
    plt.figure(figsize=(12.2, 4.5))

    for c in graphportfolio.columns.values:
        plt.plot(graphportfolio[c], label = c)
    plt.title(title)
    plt.xlabel('Date', fontsize = 18)
    plt.ylabel(col + ' Price USD ($)', fontsize = 18)
    plt.legend(graphportfolio.columns.values, loc = 'upper left')
    plt.show()


#Calculate simple return and other statistics
def simpleReturns(stocks, col = 'adjusted_close'):
    returnsPortfolio = getPortfolio(stocks)[col]
    # calculation is (daily_simple_returns[0] / daily_simple_returns[1]) - 1
    daily_simple_returns = returnsPortfolio.pct_change(1)
    #is there a correlation between stocks going up or down
    #1 means both stocks go up together
    #  -1 means when one goes up another goes down
    correlation = daily_simple_returns.corr()
    #show the covariance matrix which is used to determine an
    #efficient frontier (portfolios with the highest rate of return
    #versus the risk associated with rate
    #Measuarement of spread of data in the set
    covariance = daily_simple_returns.cov()
    #standard deviation for daily simple returns
    #The higher the volatility/std, the higher the return
    standardDeviation = daily_simple_returns.std()
    return daily_simple_returns

def showDailySimpleReturns(stocks, col = 'adjusted_close'):
    daily_simple_returns = simpleReturns(stocks, col = col)
    for c in daily_simple_returns.columns.values:
        plt.plot(daily_simple_returns[c], lw=2, label=c)

    plt.legend(loc='upper right', fontsize=18)
    plt.title('Volatility')
    plt.ylabel('Daily Simple Returns')
    plt.xlabel('Date')
    plt.show()

def showDailyCumulativeSimpleReturns(dailySimpleReturns):
    # Calculate growth of investment
    # (period_1 +1) * (period_2+1)...
    dailyCumulSimplReturn = (dailySimpleReturn + 1).cumprod()
    plt.figure(figsize=(12.2, 4.5))
    for c in dailyCumulSimplReturn.columns.values:
        plt.plot(dailyCumulSimplReturn.index, dailyCumulSimplReturn[c], lw=2, label=c)

    plt.legend(loc='upper right', fontsize=18)
    plt.title('Daily Cumulative Simple Returns')
    plt.ylabel('Growth of $1 Investment')
    plt.xlabel('Date')
    plt.show()


def showMeanDailySimpleReturns(stocks, col = 'Adj Close'):
    daily_simple_returns = simpleReturns(stocks = stocks, col = col)
    dailyMeanSimpleReturns = daily_simple_returns.mean()
    #expected returns FB=40%, AMZN 10%, AAPL 30%, NFLX10% GOOG 10%
    randomWeights = np.array([0.4, 0.1, 0.3, 0.1, 0.1])
    portfolioSimpleReturn = np.sum(dailyMeanSimpleReturns * randomWeights)
    return portfolioSimpleReturn


#dailySimpleReturn = simpleReturns(faang_stocks, stockStartDate, today, 'Adj Close')
#showDailySimpleReturns(faang_stocks, stockStartDate, today, 'Adj Close')

#The daily return of a portfolio
#dailyExpectedReturn = showMeanDailySimpleReturns(faang_stocks, stockStartDate, today, 'Adj Close')
#print('The daily expected portfolio return is ' + str(dailyExpectedReturn))
#print("Expected  annualised portfolio simpole return: " + str(dailyExpectedReturn *253)) #number of trading days


#showDailyCumulativeSimpleReturns(dailySimpleReturn)

