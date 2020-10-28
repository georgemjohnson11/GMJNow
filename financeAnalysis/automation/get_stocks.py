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

def populate_todays_history(date=dt.datetime(2020,10,26)):
    for ticker in StockTicker.objects.filter(updated_time__lte=date):
        write_stock_history_to_database(ticker.id, date)
    do_ml()

def backpopulate_stock_history_2015():
    start = dt.datetime(2015, 1, 1)
    end = dt.date(2020, 1, 1)
    populate_todays_history()
    # for stock in StockTicker.objects.filter(updated_time__lte=end):
    #     if not StockTickerHistory.objects.filter(symbol=stock.id, updated_on__gt=end).first():
    #


def write_stock_history_to_database(row, start):
    end = dt.datetime(2020,10,27)
    if start is None:
        start=dt.datetime(2020,10,26)
    print('Fetching {}  on {}'.format(row, start))
    try:
        df = web.get_data_yahoo(row.replace('.','-'), start=start, end=end)
        df.reset_index(inplace=True)
        df.set_index("Date", inplace=True)
        for i in df.iterrows():
            StockTickerHistory.objects.update_or_create(symbol_id=row, close=i[1]['Close'],
                                           low=i[1]['Low'], high=i[1]['High'],
                                           open=i[1]['Open'], volume=i[1]['Volume'],
                                           adjusted_close=i[1]['Adj Close'], updated_on=i[0])
        advanced_analysis(row, start)
        StockTicker.objects.filter(id=row).update(updated_time=start)
        advanced_analysis(row, end)
        StockTicker.objects.filter(id=row).update(updated_time=end)
        buy_signal_indicator(row, start)
        buy_signal_indicator(row, end)
        print('starting last sell update')
    except RemoteDataError:
        StockTicker.objects.filter(id=row).update(updated_time=start)
        print('remote error ' + row)
    except KeyError:
        StockTicker.objects.filter(id=row).update(updated_time=start)
        print('key error ' + row)

