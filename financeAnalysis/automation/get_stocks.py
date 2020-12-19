# Look into Airflow for scheduling https://www.saturncloud.io/s/job-scheduling-with-python/
import datetime as dt
from pandas_datareader import data as web
from pandas_datareader._utils import RemoteDataError
from financeAnalysis.models import StockTicker, StockTickerHistory
from .advanced_analysis import advanced_analysis, decisionTreePrediction,show_buy_sell_points, svr_prediction_build_plot, ticker_overview, showRSI
from financeAnalysis.backend.StockScreener import buy_signal_indicator
from financeAnalysis.backend.MLBuySell import do_ml
from financeAnalysis.backend.portfolioManagement import getPortfolio

def backpopulate_stock_history_2020(date=dt.datetime(2015,1,1)):
    ten_days_ago = dt.datetime.today()- dt.timedelta(days=15)
    for ticker in StockTicker.objects.filter(updated_time__lt=ten_days_ago).order_by('id'):
        backwrite_stock_history_to_database(ticker.id, date)
        ticker.update(updated_time=dt.datetime.today()).save()
    do_ml()

def backpopulate_ticker_history(stock_ticker_symbol, date=dt.datetime(2020,4,30)):
    backwrite_stock_history_to_database(stock_ticker_symbol, date)

def populate_todays_history(today=dt.datetime.today()):
    twodays_ago = (today - dt.timedelta(days = 2)).date()
    threedays_ago = (today - dt.timedelta(days = 3)).date()
    fourdays_ago = (today - dt.timedelta(days = 4)).date()

    yesterday = (today - dt.timedelta(days=1)).date()
    for ticker in StockTicker.objects.filter(updated_time__lt=today.date()):
        if not StockTickerHistory.objects.filter(symbol_id=ticker.id).filter(updated_on__date=fourdays_ago):
            backwrite_stock_history_to_database(ticker.id, fourdays_ago)
        elif not StockTickerHistory.objects.filter(symbol_id=ticker.id).filter(updated_on__date=threedays_ago):
            backwrite_stock_history_to_database(ticker.id, threedays_ago)
        elif not StockTickerHistory.objects.filter(symbol_id=ticker.id).filter(updated_on__date=twodays_ago):
            backwrite_stock_history_to_database(ticker.id, twodays_ago)
        elif not StockTickerHistory.objects.filter(symbol_id=ticker.id).filter(updated_on__date=yesterday):
            write_stock_history_to_database(ticker.id, yesterday)
    do_ml()

def write_stock_history_to_database(row, start):
    end = dt.date.today()
    print('Fetching {}  on {}'.format(row, start))
    try:
        df = web.get_data_yahoo(row.replace('.','-'), start=start, end=start)
        df.reset_index(inplace=True)
        df.set_index("Date", inplace=True)
        StockTickerHistory.objects.update_or_create(symbol_id=row, close=df['Close'][0],
                                       low=df['Low'][0], high=df['High'][0],
                                       open=df['Open'][0], volume=df['Volume'][0],
                                       adjusted_close=df['Adj Close'][0], updated_on=df.index[0])
        StockTicker.objects.filter(id=row).update(updated_time=start, last_sale=df['Close'][0])
        advanced_analysis(row, df.index[0])
        buy_signal_indicator(row, df.index[0])
    except RemoteDataError:
        StockTicker.objects.filter(id=row).update(updated_time=end)
        print('remote error ' + row)
    except KeyError:
        StockTicker.objects.filter(id=row).update(updated_time=end)
        print('key error ' + row)

#The date was already updated during the initial population of dates
    #This should not update the stockticker updated time as that keeps track of the last time
    #populate dates was ran for a ticker successfully
def repopulate_todays_history(date=dt.datetime.today()):
    for ticker in StockTickerHistory.objects.filter(updated_on__date=date).order_by('id'):
        repopulate_stock_history(ticker, ticker.updated_on)

def repopulate_stock_history(history, date=dt.datetime.today()):
    date = date.date()
    if history.updated_on.date() == date:
        tickers = getPortfolio(history.symbol_id, date)
        if not history.plot:
            ticker_overview(history.symbol_id, date)
        if not history.rsi:
            showRSI(history.symbol_id, tickers, date)
        if not history.svr_plot:
            svr_prediction_build_plot(history.symbol_id, tickers, date)
        if not history.decision_tree_plot:
            decisionTreePrediction(history.symbol_id, tickers, date)
        if not history.sma_plot:
            show_buy_sell_points(history.symbol_id, tickers, date)


def backwrite_stock_history_to_database(row, start):
    end = dt.date.today()
    if start is None:
        start=dt.datetime(2020,10,21)
    print('Fetching {}  on {}'.format(row, start))
    StockTicker.objects.filter(id=row).update(updated_time=end)
    try:
        df = web.get_data_yahoo(row.replace('.','-'), start=start, end=end)
        df.reset_index(inplace=True)
        df.set_index("Date", inplace=True)
        for i in df.iterrows():
            StockTickerHistory.objects.update_or_create(symbol_id=row, close=i[1]['Close'],
                                           low=i[1]['Low'], high=i[1]['High'],
                                           open=i[1]['Open'], volume=i[1]['Volume'],
                                           adjusted_close=i[1]['Adj Close'], updated_on=i[0])

        advanced_analysis(row, i[0])
        buy_signal_indicator(row, i[0])
    except RemoteDataError:
        StockTicker.objects.filter(id=row).update(updated_time=end)
        print('remote error ' + row)
    except KeyError:
        StockTicker.objects.filter(id=row).update(updated_time=end)
        print('key error ' + row)

