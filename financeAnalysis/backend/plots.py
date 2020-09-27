import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.animation as animation
from matplotlib import style
from mplfinance.original_flavor import candlestick_ohlc
from sklearn.svm import SVR
import pickle
import datetime as dt
import numpy as np
import pandas as pd
import apiclient
from io import BytesIO
from django.http import HttpResponseRedirect,request
from .decisionTree import decisionTreePredictPrice
from .portfolioManagement import getPortfolio
import base64


def displayPortfolioGraph(stocks):
    plt.style.use('fivethirtyeight')
    img = BytesIO()
    prices = getPortfolio(stocks)[-300:]
    fig, ax1 = plt.subplots(facecolor='#C1DFF0', figsize=(12, 8))  # Create Plots
    ax1.annotate("Last Closing\n Price: $" + str(prices['Adj Close'][-1])[0:6],
                 (prices.index[-1], prices['Adj Close'][-1]),
                 xytext=(prices.index[-1] + dt.timedelta(days=4), prices['Adj Close'][-1]), color='#006989', size=10)
    ax1.set_facecolor('#C1DFF0')
    plt.rcParams['figure.facecolor'] = '#C1DFF0'
    smasUsed = [10, 30, 50]  # Choose smas
    # Calculate moving averages
    for x in smasUsed:  # This for loop calculates the SMAs for the stated periods and appends to dataframe
        sma = x
        prices['SMA' + str(sma)] = prices['Adj Close'].rolling(window=sma).mean()  # calcaulates sma and creates col

    # calculate Bollinger Bands
    BBperiod = 15  # choose moving avera
    stdev = 2
    prices['SMA' + str(BBperiod)] = prices['Adj Close'].rolling(
        window=BBperiod).mean()  # calculates sma and creates a column in the dataframe
    prices['STDEV'] = prices['Adj Close'].rolling(
        window=BBperiod).std()  # calculates standard deviation and creates col
    prices['LowerBand'] = prices['SMA' + str(BBperiod)] - (stdev * prices['STDEV'])  # calculates lower bollinger band
    prices['UpperBand'] = prices['SMA' + str(BBperiod)] + (stdev * prices['STDEV'])  # calculates upper band
    prices["Date"] = mdates.date2num(prices.index)  # creates a date column stored in number format (for OHCL bars)

    # Calculate 10.4.4 stochastic
    Period = 10  # Choose stoch period
    K = 4  # Choose K parameter
    D = 4  # choose D parameter

    prices["RolHigh"] = prices["High"].rolling(window=Period).max()  # Finds high of period
    prices["RolLow"] = prices["Low"].rolling(window=Period).min()  # finds low of period
    prices["stok"] = ((prices["Adj Close"] - prices["RolLow"]) / (
            prices["RolHigh"] - prices["RolLow"])) * 100  # Finds 10.1 stoch
    prices["K"] = prices["stok"].rolling(window=K).mean()  # Finds 10.4 stoch
    prices["D"] = prices["K"].rolling(window=D).mean()  # Finds 10.4.4 stoch
    prices["GD"] = prices["High"]  # Create GD column to store green dots

    ohlc = []  # Create OHLC array which will store price data for the candlestick chart

    # Delete extra dates
    prices = prices.iloc[max(smasUsed):]

    greenDotDate = []  # Stores dates of Green Dots
    greenDot = []  # Stores Values of Green Dots
    lastK = 0  # Will store yesterday's fast stoch
    lastD = 0  # will store yseterdays slow stoch
    lastLow = 0  # will store yesterdays lower
    lastClose = 0  # will store yesterdays close
    lastLowBB = 0  # will store yesterdays lower bband

    # Go through price history to create candlestics and GD+Blue dots
    for i in prices.index:
        # append OHLC prices to make the candlestick
        append_me = prices["Date"][i], prices["Open"][i], prices["High"][i], prices["Low"][i], prices["Adj Close"][i], \
                    prices["Volume"][i]
        ohlc.append(append_me)

        # Check for Green Dot
        if prices['K'][i] > prices['D'][i] and lastK < lastD and lastK < 60:
            # plt.Circle((prices["Date"][i],prices["High"][i]),1)
            # plt.bar(prices["Date"][i],1,1.1,bottom=prices["High"][i]*1.01,color='g')
            plt.plot(prices["Date"][i], prices["High"][i] + 1, marker="o", ms=4, ls="", color='g')  # plot green dot

            greenDotDate.append(i)  # store green dot date
            greenDot.append(prices["High"][i])  # store green dot value

        # Check for Lower Bollinger Band Bounce
        if ((lastLow < lastLowBB) or (prices['Low'][i] < prices['LowerBand'][i])) and (
                prices['Adj Close'][i] > lastClose and prices['Adj Close'][i] > prices['LowerBand'][i]) and lastK < 60:
            plt.plot(prices["Date"][i], prices["Low"][i] - 1, marker="o", ms=4, ls="", color='b')  # plot blue dot

        # store values
        lastK = prices['K'][i]
        lastD = prices['D'][i]
        lastLow = prices['Low'][i]
        lastClose = prices['Adj Close'][i]
        lastLowBB = prices['LowerBand'][i]

    # Plot moving averages and BBands
    for x in smasUsed:  # This for loop calculates the EMAs for te stated periods and appends to dataframe
        sma = x
        prices['SMA' + str(sma)].plot(label='SMA' + str(sma))
    prices['UpperBand'].plot(label='Upper Bollinger Band', color='lightgray')
    prices['LowerBand'].plot(label='Lower Bollinger Band', color='lightgray')

    # plot candlesticks
    candlestick_ohlc(ax1, ohlc, width=.5, colorup='k', colordown='r', alpha=0.75)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # change x axis back to datestamps
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(8))  # add more x axis labels

    ax1.tick_params(axis='x', rotation=45)  # rotate dates for readability

    # Pivot Points
    pivots = []  # Stores pivot values
    dates = []  # Stores Dates corresponding to those pivot values
    counter = 0  # Will keep track of whether a certain value is a pivot
    lastPivot = 0  # Will store the last Pivot value

    Range = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Array used to iterate through stock prices
    dateRange = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Array used to iterate through corresponding dates
    for i in prices.index:  # Iterates through the price history
        currentMax = max(Range,
                         default=0)  # Determines the maximum value of the 10 item array, identifying a potential pivot
        value = round(prices["High"][i], 2)  # Receives next high value from the dataframe

        Range = Range[1:9]  # Cuts Range array to only the most recent 9 values
        Range.append(value)  # Adds newest high value to the array
        dateRange = dateRange[1:9]  # Cuts Date array to only the most recent 9 values
        dateRange.append(i)  # Adds newest date to the array

        if currentMax == max(Range, default=0):  # If statement that checks is the max stays the same
            counter += 1  # if yes add 1 to counter
        else:
            counter = 0  # Otherwise new potential pivot so reset the counter
        if counter == 5:  # checks if we have identified a pivot
            lastPivot = currentMax  # assigns last pivot to the current max value
            dateloc = Range.index(lastPivot)  # finds index of the Range array that is that pivot value
            lastDate = dateRange[dateloc]  # Gets date corresponding to that index
            pivots.append(currentMax)  # Adds pivot to pivot array
            dates.append(lastDate)  # Adds pivot date to date array

    timeD = dt.timedelta(days=30)  # Sets length of dotted line on chart

    for index in range(len(pivots)):  # Iterates through pivot array

        # print(str(pivots[index])+": "+str(dates[index])) #Prints Pivot, Date couple
        ax1.plot_date([dates[index] - (timeD * .075), dates[index] + timeD],  # Plots horizontal line at pivot value
                      [6 +
                       pivots[index], pivots[index]], linestyle="--", linewidth=1, marker=',', color='#006989')
        ax1.annotate(str(pivots[index]), (mdates.date2num(dates[index]), pivots[index]), xytext=(-10, 7),
                     textcoords='offset points', fontsize=10, arrowprops=dict(arrowstyle='-|>'), color='#006989')

    ax1.set_xlabel('Date')  # set x axis label
    ax1.set_ylabel('Price')  # set y axis label
    ax1.legend(loc='best', prop={'size': 8})
    ax1.set_title(stocks + " - Daily", color='#006989')  # set title
    ax1.set_ylim([prices["Low"].min(), prices["High"].max() * 1.05])  # add margins
    ax1.xaxis.label.set_color('#006989')
    ax1.yaxis.label.set_color('#006989')
    ax1.tick_params(axis='x', colors='#006989')
    ax1.tick_params(axis='y', colors='#006989')
    COLOR = '#006989'
    plt.rcParams['axes.facecolor'] = '#C1DFF0'
    plt.rcParams['text.color'] = COLOR
    plt.rcParams['axes.labelcolor'] = COLOR
    plt.rcParams['xtick.color'] = COLOR
    plt.rcParams['ytick.color'] = COLOR
    plt.rcParams['grid.color'] = COLOR
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['axes.titlecolor'] = COLOR
    ax1.set_facecolor('#C1DFF0')
    plt.rcParams['figure.facecolor'] = '#C1DFF0'
    plt.savefig(img, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    return plot_url


def decisionTreePrediction(ticker):
    tickers, valid = decisionTreePredictPrice(ticker)
    img = BytesIO()
    # Plot the models on a graph to see which has the best fit
    plt.figure(figsize=(12, 8))
    fig, ax1 = plt.subplots(facecolor='#C1DFF0', figsize=(12, 8))  # Create Plots
    ax1.annotate("Prediction\n Price: $" + str(valid['Prediction'][-1])[0:8],
                 (valid.index[-1], valid['Prediction'][-1]),
                 xytext=(valid.index[-1] + dt.timedelta(days=4), valid['Prediction'][-1]), color='#006989', size=10)
    plt.style.use('fivethirtyeight')
    plt.title('Decision Tree Prediction')
    plt.xlabel('Days')
    plt.plot(tickers['Close'][-200:])
    plt.plot(valid[['Close', 'Predictions'][-200:]])
    plt.legend(['Original', 'Valid', 'Prediction'], loc='best', prop={'size': 8})
    ax1.set_facecolor('#C1DFF0')
    plt.rcParams['figure.facecolor'] = '#C1DFF0'
    plt.savefig(img, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    return plot_url


def showRSI(ticker):
    tickers = getPortfolio(ticker)[-500:]
    # Calculate RSI
    # Get the difference in daily price
    delta = tickers['Adj Close'].diff(1)
    delta = delta.dropna()
    up = delta.copy()
    down = delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    period = 14
    AVG_GAIN = up.rolling(window=period).mean()
    AVG_LOSS = abs(down.rolling(window=period).mean())

    # Calculate Relative Strength (RS)
    tickers['RS'] = AVG_GAIN / AVG_LOSS
    tickers['RSI'] = 100.0 - (100.0 / (1.0 + tickers['RS']))
    print(tickers['RSI'])
    # Calculate RSI
    img = BytesIO()

    plt.figure(figsize=(12, 8))
    fig, ax1 = plt.subplots(facecolor='#C1DFF0', figsize=(12, 8))  # Create Plots
    plt.plot(tickers.index, tickers['RSI'], label=ticker, alpha=0.35, color='#ED6A5A')
    plt.axhline(0, linestyle='--', alpha=0.5, color='grey')
    plt.axhline(10, linestyle='--', alpha=0.5, color='green')
    plt.axhline(20, linestyle='--', alpha=0.5, color='orange')
    plt.axhline(30, linestyle='--', alpha=0.5, color='red')
    plt.axhline(70, linestyle='--', alpha=0.5, color='red')
    plt.axhline(80, linestyle='--', alpha=0.5, color='orange')
    plt.axhline(90, linestyle='--', alpha=0.5, color='green')
    plt.axhline(100, linestyle='--', alpha=0.5, color='grey')
    plt.style.use('fivethirtyeight')
    plt.title(ticker + ' RSI values and Significant Levels')
    plt.xlabel(str(tickers.index[0]) + ' - ' + str(tickers.index[-1]))
    plt.ylabel('RSI')
    plt.legend(loc='best', prop={'size': 8})
    ax1.set_facecolor('#C1DFF0')
    plt.rcParams['figure.facecolor'] = '#C1DFF0'
    plt.savefig(img, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    return plot_url


def showBuySellPoints(ticker):
    tickers = getPortfolio(ticker)[-600:]
    signalPriceBuy = []
    signalPriceSell = []
    flag = -1

    smasUsed = [30, 100, 200]  # Choose smas
    # Calculate moving averages
    for x in smasUsed:  # This for loop calculates the SMAs for the stated periods and appends to dataframe
        sma = x
        tickers['SMA' + str(sma)] = tickers['Adj Close'].rolling(window=sma).mean()  # calcaulates sma and creates col

    for i in range(len(tickers.index)):
        if tickers['SMA30'][i] > tickers['SMA100'][i]:
            if flag != 1:
                signalPriceBuy.append(tickers['Adj Close'][i])
                signalPriceSell.append(np.nan)
                flag = 1
            else:
                signalPriceBuy.append(np.nan)
                signalPriceSell.append(np.nan)
        elif tickers['SMA30'][i] < tickers['SMA100'][i]:
            if flag != 0:
                signalPriceSell.append(tickers['Adj Close'][i])
                signalPriceBuy.append(np.nan)
                flag = 0
            else:
                signalPriceSell.append(np.nan)
                signalPriceBuy.append(np.nan)
        else:
            signalPriceSell.append(np.nan)
            signalPriceBuy.append(np.nan)

    tickers['Buy_Signal_Price'] = signalPriceBuy
    tickers['Sell_Signal_Price'] = signalPriceSell

    plt.style.use('fivethirtyeight')
    img = BytesIO()
    plt.figure(figsize=(12, 8))
    fig, ax1 = plt.subplots(facecolor='#C1DFF0', figsize=(12, 8))  # Create Plots
    plt.plot(tickers['Adj Close'], label=ticker, alpha=0.35, color='#2B9720')
    for x in smasUsed:  # This for loop calculates the EMAs for te stated periods and appends to dataframe
        sma = x
        tickers['SMA' + str(sma)].plot(label='SMA' + str(sma), alpha=0.35)
    plt.scatter(tickers.index, tickers['Buy_Signal_Price'], label='BUY', marker='^', s=32, color='#ED6A5A')
    plt.scatter(tickers.index, tickers['Sell_Signal_Price'], label='SELL', marker='v', s=32, color='#006989')
    plt.title(ticker + ' Adj Close Price History with Buy and Sell Signals')
    plt.xlabel(str(tickers.index[0]) + ' - ' + str(tickers.index[-1]))
    plt.ylabel('Adj. Close Price USD ($)')
    plt.legend(loc='best', prop={'size': 8})
    ax1.set_facecolor('#C1DFF0')
    plt.rcParams['figure.facecolor'] = '#C1DFF0'
    plt.savefig(img, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    return plot_url


# function to make predictions using 3 different support vector regression models with 3 different kernals
def svr_prediction_build_plot(ticker):
    now = dt.datetime.today()
    DD = dt.timedelta(days=1)
    tomorrow = [(now + DD).day]

    tickers = getPortfolio(ticker)

    dates = tickers.index[-20:].date
    closing_price = tickers.loc[:, 'Adj Close'][-20:]
    dates = np.reshape(dates, (len(dates), 1))  # convert to 1xn dimension
    tomorrow = np.reshape(tomorrow, (len(tomorrow), 1))
    # RBF is the best predictor
    # Create a 3 support vecotor regresstion model
    svr_lin = SVR(kernel='linear', C=1e3)
    svr_poly = SVR(kernel='poly', C=1e3, degree=2)
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)

    dates_list = []
    for i in dates:
        dates_list.append([i[0].day])

    # train the models on the dates and prices
    svr_lin.fit(dates_list, closing_price)
    svr_poly.fit(dates_list, closing_price)
    svr_rbf.fit(dates_list, closing_price)

    img = BytesIO()
    # Plot the models on a graph to see which has the best fit

    fig, ax1 = plt.subplots(facecolor='#C1DFF0', figsize=(13, 8))  # Create Plots
    plt.scatter(dates, closing_price, color='#006989', label=ticker)
    plt.plot(dates, svr_lin.predict(dates_list), color='red', label='SVR Linear Model')
    plt.plot(dates, svr_poly.predict(dates_list), color='#ED6A5A', label='SVR Poly Model')
    plt.plot(dates, svr_rbf.predict(dates_list), color='#2B9720', label='SVR RBF Model')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.xaxis.label.set_color('#006989')
    ax1.yaxis.label.set_color('#006989')
    ax1.set_title('Support Vector Regression', color='#006989')
    plt.legend(loc='best', prop={'size': 8})
    ax1.set_facecolor('#C1DFF0')
    plt.rcParams['figure.facecolor'] = '#C1DFF0'
    plt.savefig(img, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
    return plot_url


