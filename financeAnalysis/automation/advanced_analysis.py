import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from mplfinance.original_flavor import candlestick_ohlc
from sklearn.svm import SVR
import datetime as dt
import time
import os
import pandas as pd
import numpy as np
from io import BytesIO
from financeAnalysis.models import StockTickerHistory, StockTicker
from financeAnalysis.backend.decisionTree import decisionTreePredictPrice
from financeAnalysis.backend.portfolioManagement import getPortfolio, getPortfolioDateTime, getPortfolioAdvanced
import base64

def advanced_analysis(stock_ticker_symbol, date=dt.date.today()):
    now = dt.date.today()
    try:
        print('starting buy sell points')
        show_buy_sell_points(stock_ticker_symbol, date)
    except Exception as ex:
      print(ex)
    try:
        print('starting rsi')
        showRSI(stock_ticker_symbol, date)
    except Exception as ex:
      print(ex)
    try:
        print('starting svr prediction')
        svr_prediction_build_plot(stock_ticker_symbol, date)
    except Exception as ex:
      print(ex)
    try:
        print('starting ticker overview')
        ticker_overview(stock_ticker_symbol, date)
    except Exception as ex:
        print(ex)
    try:
        print('starting decision tree prediction')
        decisionTreePrediction(stock_ticker_symbol, date)
    except Exception as ex:
      print(ex)
    print('Finished advanced analysis')

def ticker_overview(stock_ticker_symbol, date=dt.date.today()):
    try:
        stocks = pd.DataFrame()
        plt.style.use('fivethirtyeight')
        img = BytesIO()
        stocks = getPortfolioAdvanced(stock_ticker_symbol, date)[-300:]
        fig, ax1 = plt.subplots(facecolor='#C1DFF0', figsize=(12, 8))  # Create Plots
        ax1.annotate("Last Closing\n Price: $" + str(stocks['adjusted_close'][-1])[0:6],
                     (stocks.index[-1], stocks['adjusted_close'][-1]),
                     xytext=(stocks.index[-1] + dt.timedelta(days=4), stocks['adjusted_close'][-1]), color='#006989', size=10)
        ax1.set_facecolor('#C1DFF0')
        plt.rcParams['figure.facecolor'] = '#C1DFF0'
        smasUsed = [10, 30, 50]  # Choose smas
        # Calculate moving averages
        for x in smasUsed:  # This for loop calculates the SMAs for the stated periods and appends to dataframe
            sma = x
            stocks['SMA' + str(sma)] = stocks['adjusted_close'].rolling(window=sma).mean()  # calcaulates sma and creates col

        # calculate Bollinger Bands
        BBperiod = 15  # choose moving avera
        stdev = 2
        stocks['SMA' + str(BBperiod)] = stocks['adjusted_close'].rolling(
            window=BBperiod).mean()  # calculates sma and creates a column in the dataframe
        stocks['STDEV'] = stocks['adjusted_close'].rolling(
            window=BBperiod).std()  # calculates standard deviation and creates col
        stocks['LowerBand'] = stocks['SMA' + str(BBperiod)] - (stdev * stocks['STDEV'])  # calculates lower bollinger band
        stocks['UpperBand'] = stocks['SMA' + str(BBperiod)] + (stdev * stocks['STDEV'])  # calculates upper band
        stocks["Date"] = mdates.date2num(stocks.index)  # creates a date column stored in number format (for OHCL bars)

        # Calculate 10.4.4 stochastic
        Period = 10  # Choose stoch period
        K = 4  # Choose K parameter
        D = 4  # choose D parameter

        stocks["RolHigh"] = stocks["high"].rolling(window=Period).max()  # Finds high of period
        stocks["RolLow"] = stocks["low"].rolling(window=Period).min()  # finds low of period
        stocks["stok"] = ((stocks["adjusted_close"] - stocks["RolLow"]) / (
                stocks["RolHigh"] - stocks["RolLow"])) * 100  # Finds 10.1 stoch
        stocks["K"] = stocks["stok"].rolling(window=K).mean()  # Finds 10.4 stoch
        stocks["D"] = stocks["K"].rolling(window=D).mean()  # Finds 10.4.4 stoch
        stocks["GD"] = stocks["high"]  # Create GD column to store green dots

        ohlc = []  # Create OHLC array which will store price data for the candlestick chart

        # Delete extra dates
        stocks = stocks.iloc[max(smasUsed):]

        greenDotDate = []  # Stores dates of Green Dots
        greenDot = []  # Stores Values of Green Dots
        lastK = 0  # Will store yesterday's fast stoch
        lastD = 0  # will store yseterdays slow stoch
        lastLow = 0  # will store yesterdays lower
        lastClose = 0  # will store yesterdays close
        lastLowBB = 0  # will store yesterdays lower bband

        # Go through price history to create candlestics and GD+Blue dots
        for i in range(len(stocks['Date'])):
            # append OHLC prices to make the candlestick
            append_me = stocks['Date'][i], stocks["open"][i], stocks["high"][i], stocks["low"][i], stocks["adjusted_close"][i], stocks["volume"][i]
            ohlc.append(append_me)

            # Check for Green Dot
            if stocks['K'][i] > stocks['D'][i] and lastK < lastD and lastK < 60:
                # plt.Circle((stocks["Date"][i],stocks["High"][i]),1)
                # plt.bar(stocks["Date"][i],1,1.1,bottom=stocks["High"][i]*1.01,color='g')
                plt.plot(stocks["Date"][i], stocks["high"][i] + 1, marker="o", ms=4, ls="", color='g')  # plot green dot

                greenDotDate.append(stocks.index[i])  # store green dot date
                greenDot.append(stocks["high"][i])  # store green dot value

            # Check for Lower Bollinger Band Bounce
            if ((lastLow < lastLowBB) or (stocks['low'][i] < stocks['LowerBand'][i])) and (
                    stocks['adjusted_close'][i] > lastClose and stocks['adjusted_close'][i] > stocks['LowerBand'][i]) and lastK < 60:
                plt.plot(stocks['Date'][i], stocks["low"][i] - 1, marker="o", ms=4, ls="", color='b')  # plot blue dot

            # store values
            lastK = stocks['K'][i]
            lastD = stocks['D'][i]
            lastLow = stocks['low'][i]
            lastClose = stocks['adjusted_close'][i]
            lastLowBB = stocks['LowerBand'][i]

        # Plot moving averages and BBands
        for x in smasUsed:  # This for loop calculates the EMAs for te stated periods and appends to dataframe
            sma = x
            stocks['SMA' + str(sma)].plot(label='SMA' + str(sma))
        stocks['UpperBand'].plot(label='Upper Bollinger Band', color='lightgray')
        stocks['LowerBand'].plot(label='Lower Bollinger Band', color='lightgray')

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
        for i in range(len(stocks.index)):  # Iterates through the price history
            currentMax = max(Range,
                             default=0)  # Determines the maximum value of the 10 item array, identifying a potential pivot
            value = round(stocks["high"][i], 2)  # Receives next high value from the dataframe

            Range = Range[1:9]  # Cuts Range array to only the most recent 9 values
            Range.append(value)  # Adds newest high value to the array
            dateRange = dateRange[1:9]  # Cuts Date array to only the most recent 9 values
            dateRange.append(stocks.index[i])  # Adds newest date to the array

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
        ax1.set_title(stock_ticker_symbol + " - Daily", color='#006989')  # set title
        ax1.set_ylim([stocks["low"].min(), stocks["high"].max() * 1.05])  # add margins
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
        plt.close('all')
        img.close()
        StockTickerHistory.objects.update_or_create(symbol_id=stock_ticker_symbol, updated_on=stocks.index[-1],
                                                    defaults={'sma_fifty_day': stocks['SMA50'][-1],
                                                              'green_dot_dates': greenDotDate,
                                                              'green_dot_values': greenDot,
                                                              'plot': plot_url })
        return plot_url
    except Exception as ex:
        print(ex)

def decisionTreePrediction(stock_ticker_symbol, date=dt.date.today()):
    try:
        tickers = pd.DataFrame()
        valid = pd.DataFrame()
        valid = decisionTreePredictPrice(stock_ticker_symbol)
        if tickers is not None and valid is not None:
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
          tickers = getPortfolio(stock_ticker_symbol)
          plt.plot(tickers['adjusted_close'][-200:])
          plt.plot(valid[['adjusted_close', 'Predictions'][-200:]])
          plt.legend(['Original', 'Valid', 'Prediction'], loc='best', prop={'size': 8})
          ax1.set_facecolor('#C1DFF0')
          plt.rcParams['figure.facecolor'] = '#C1DFF0'
          plt.savefig(img, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
          img.seek(0)
          plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
          StockTickerHistory.objects.update_or_create(symbol_id=stock_ticker_symbol, updated_on=date,
                                                      defaults={'decision_tree_plot': plot_url})
          plt.close('all')
          img.close()
          return plot_url
    except Exception as ex:
        print(ex)


def showRSI(stock_ticker_symbol, date=dt.date.today()):
    try:
        tickers = pd.DataFrame()
        tickers = getPortfolio(stock_ticker_symbol, date)[-500:]
        # Calculate RSI
        # Get the difference in daily price
        if tickers is not None:
          diff = tickers['adjusted_close'].diff(1).dropna()
          up_chg = 0 * diff
          down_chg = 0 * diff

          # up change is equal to the positive difference, otherwise equal to zero
          up_chg[diff > 0] = diff[ diff>0 ]

          # down change is equal to negative deifference, otherwise equal to zero
          down_chg[diff < 0] = diff[ diff < 0 ]
          time_window = 14
          up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
          down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    # Calculate Relative Strength (RS)
          tickers['RS'] = abs(up_chg_avg/down_chg_avg)
          tickers['RSI'] = 100.0 - (100.0 / (1.0 + tickers['RS']))
        # Calculate RSI
          img = BytesIO()

          plt.figure(figsize=(12, 8))
          fig, ax1 = plt.subplots(facecolor='#C1DFF0', figsize=(12, 8))  # Create Plots
          plt.plot(mdates.date2num(tickers.index), tickers['RSI'], label=stock_ticker_symbol, alpha=0.35, color='#5BAAD7')
          plt.axhline(0, linestyle='--', alpha=0.5, color='grey')
          plt.axhline(10, linestyle='--', alpha=0.5, color='green')
          plt.axhline(20, linestyle='--', alpha=0.5, color='orange')
          plt.axhline(30, linestyle='--', alpha=0.5, color='red')
          plt.axhline(70, linestyle='--', alpha=0.5, color='red')
          plt.axhline(80, linestyle='--', alpha=0.5, color='orange')
          plt.axhline(90, linestyle='--', alpha=0.5, color='green')
          plt.axhline(100, linestyle='--', alpha=0.5, color='grey')
          plt.style.use('fivethirtyeight')
          plt.title(stock_ticker_symbol + ' RSI values and Significant Levels')
          xlabel = tickers.index[0].strftime("%b %d %Y") + '-' + tickers.index[-1].strftime("%b %d %Y")
          plt.xlabel(xlabel)
          plt.ylabel('RSI')
          plt.legend(loc='best', prop={'size': 8})
          ax1.set_facecolor('#C1DFF0')
          plt.rcParams['figure.facecolor'] = '#C1DFF0'
          plt.savefig(img, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
          img.seek(0)
          plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
          StockTickerHistory.objects.update_or_create(symbol_id=stock_ticker_symbol, updated_on=tickers.index[-1],
                                                      defaults={'rsi_plot': plot_url, 'rsi': tickers['RSI'][-1]})
          plt.close('all')
          img.close()
        return plot_url
    except Exception as ex:
        print(ex)

#Work on adding datetime values as NaT
def show_buy_sell_points(stock_ticker_symbol, date=dt.date.today()):
    try:
        tickers = pd.DataFrame()
        tickers = getPortfolioDateTime(stock_ticker_symbol, date)[-600:]
        signalPriceBuy = []
        signalPriceSell = []

        smasUsed = [30, 100, 200]  # Choose smas
        # Calculate moving averages
        for x in smasUsed:  # This for loop calculates the SMAs for the stated periods and appends to dataframe
            sma = x
            tickers['SMA' + str(sma)] = tickers['adjusted_close'].rolling(window=sma).mean()  # calcaulates sma and creates col
            tickers['SMA' + str(sma)] = tickers['SMA' + str(sma)].dropna()
        flag = -1
        for i in range(len(tickers.index)):
            if tickers['SMA30'][i] > tickers['SMA100'][i]:
                if flag != 1:
                    signalPriceBuy.append(tickers.index[i])
                    signalPriceSell.append(pd.NaT)
                    flag = 1
                else:
                    signalPriceBuy.append(pd.NaT)
                    signalPriceSell.append(pd.NaT)
            elif tickers['SMA30'][i] < tickers['SMA100'][i]:
                if flag != 0:
                    signalPriceSell.append(tickers.index[i])
                    signalPriceBuy.append(pd.NaT)
                    flag = 0
                else:
                    signalPriceSell.append(pd.NaT)
                    signalPriceBuy.append(pd.NaT)
            else:
                signalPriceSell.append(pd.NaT)
                signalPriceBuy.append(pd.NaT)

        tickers['Buy_Signal_Price'] = signalPriceBuy
        tickers['Sell_Signal_Price'] = signalPriceSell

        plt.style.use('fivethirtyeight')
        img = BytesIO()
        plt.figure(figsize=(12, 8))
        fig, ax1 = plt.subplots(facecolor='#C1DFF0', figsize=(12, 8))  # Create Plots
        plt.plot(tickers['adjusted_close'], label=stock_ticker_symbol, alpha=0.35, color='#2B9720')
        for x in smasUsed:  # This for loop calculates the EMAs for te stated periods and appends to dataframe
            sma = x
            tickers['SMA' + str(sma)].plot(label='SMA' + str(sma), alpha=0.35)
        # plt.scatter(tickers.index, tickers['Buy_Signal_Price'], label='BUY', marker='^', s=32, color='#5BAAD7')
        # plt.scatter(tickers.index, tickers['Sell_Signal_Price'], label='SELL', marker='v', s=32, color='#006989')
        plt.title(stock_ticker_symbol + ' Adj. Close Price History with Buy and Sell Signals')
        plt.xlabel(tickers.index[0].strftime("%b %d %Y") + ' - ' + tickers.index[-1].strftime("%b %d %Y"))
        plt.ylabel('Adj. Close Price USD ($)')
        plt.legend(loc='best', prop={'size': 8})
        ax1.set_facecolor('#C1DFF0')
        plt.rcParams['figure.facecolor'] = '#C1DFF0'
        plt.savefig(img, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
        StockTickerHistory.objects.update_or_create(symbol_id=stock_ticker_symbol, updated_on=tickers.index[-1],
                                                    defaults={'sma_plot': plot_url,
                                                              'sma_thirty_day': tickers['SMA30'][-1],
                                                              'sma_hundred_fifty_day': tickers['SMA30'][-1],
                                                              'sma_two_hundred_day': tickers['SMA30'][-1],})
        plt.close('all')
        img.close()
        return plot_url
    except Exception as ex:
        print(ex)


# function to make predictions using 3 different support vector regression models with 3 different kernals
def svr_prediction_build_plot(stock_ticker_symbol, date=dt.date.today()):
    try:
        tickers = pd.DataFrame()
        now = dt.datetime.today()
        DD = dt.timedelta(days=1)
        tomorrow = [(now + DD).day]

        tickers = getPortfolio(stock_ticker_symbol, date)

        dates = tickers.index[-20:]
        closing_price = tickers.loc[:, 'adjusted_close'][-20:]
        dates = np.reshape(dates.values, (len(dates.values), 1))  # convert to 1xn dimension
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
        plt.scatter(dates, closing_price, color='#006989', label=stock_ticker_symbol)
        plt.plot(dates, svr_lin.predict(dates_list), color='red', label='SVR Linear Model')
        plt.plot(dates, svr_poly.predict(dates_list), color='#5BAAD7', label='SVR Poly Model')
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
        StockTickerHistory.objects.update_or_create(symbol_id=stock_ticker_symbol, updated_on=tickers.index[-1],
                                                    defaults={'svr_plot': plot_url})
        plt.close('all')
        img.close()
        return plot_url
    except Exception as ex:
        print(ex)
