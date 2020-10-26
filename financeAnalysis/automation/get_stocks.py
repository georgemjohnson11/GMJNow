# Look into Airflow for scheduling https://www.saturncloud.io/s/job-scheduling-with-python/
import datetime as dt
from datetime import timedelta
from time import sleep
from pandas_datareader import data as web
from pandas_datareader._utils import RemoteDataError
from financeAnalysis.models import StockTicker, StockTickerHistory
from .advanced_analysis import advanced_analysis
from financeAnalysis.backend.StockScreener import buy_signal_indicator
from financeAnalysis.backend.MLBuySell import do_ml

def populate_todays_history(date=dt.datetime(2020,10,22)):
    for ticker in StockTicker.objects.filter(updated_time__lte=date):
        if StockTickerHistory.get_todays_history_from_symbol(ticker.id):
            write_stock_history_to_database(ticker.id, date)
            advanced_analysis(ticker.id, date)
            buy_signal_indicator(ticker.id, date)
            print('starting last sell update')
            history = StockTickerHistory.get_todays_history_from_symbol(ticker.id)
            if history:
                ticker.last_sale = history.adjusted_close
                ticker.save()
    do_ml()

def backpopulate_stock_history_2015():
    start = dt.datetime(2015, 1, 1)
    end = dt.date(2020, 1, 1)
    populate_todays_history()
    # for stock in StockTicker.objects.filter(updated_time__lte=end):
    #     if not StockTickerHistory.objects.filter(symbol=stock.id, updated_on__gt=end).first():
    #


def write_stock_history_to_database(row, start):
    end = dt.datetime(2020,10,23)
    if start is None:
        start=end - timedelta(days=5)
    print('Fetching {}  on {}'.format(row, start))
    try:
        df = web.get_data_yahoo(row.replace('.','-'), start=start, end=end)
        df.reset_index(inplace=True)
        df.set_index("Date", inplace=True)
        for i in df.iterrows():
            if i[1]['High']:
                StockTickerHistory.objects.update_or_create(symbol_id=row, close=i[1]['Close'],
                                               low=i[1]['Low'], high=i[1]['High'],
                                               open=i[1]['Open'], volume=i[1]['Volume'],
                                               adjusted_close=i[1]['Adj Close'], updated_on=i[0])
        stockticker = StockTicker.get_stock_ticker_from_symbol(row)
        if stockticker:
            stockticker.updated_time = dt.datetime.now()
            stockticker.save()
    except RemoteDataError:
        print('remote error ' + row)
    except KeyError:
        print('key error ' + row)

