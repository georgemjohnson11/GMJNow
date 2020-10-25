# Look into Airflow for scheduling https://www.saturncloud.io/s/job-scheduling-with-python/
import datetime as dt
from datetime import timedelta
from time import sleep
from pandas_datareader import data as web
from pandas_datareader._utils import RemoteDataError
from financeAnalysis.models import StockTicker, StockTickerHistory
from .advanced_analysis import svr_prediction_build_plot
from financeAnalysis.backend.StockScreener import buy_signal_indicator
from financeAnalysis.backend.MLBuySell import do_ml

def backpopulate_stock_history_2015():
    start = dt.datetime(2015, 1, 1)
    end = dt.date(2020, 1, 1)
    do_ml('V', dt.datetime(2020, 10, 21))
    buy_signal_indicator('V', dt.datetime(2020, 10, 21))
    # for stock in StockTicker.objects.filter(updated_time__lte=end):
    #     if not StockTickerHistory.objects.filter(symbol=stock.id, updated_on__gt=end).first():
    #         write_stock_history_to_database(stock.id, start)


def write_stock_history_to_database(row, start):
    end = dt.datetime.now()
    if start is None:
        start=end - timedelta(days=5)
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
        stockticker = StockTicker.get_stock_ticker_from_symbol(row)
        if stockticker:
            stockticker.updated_time = dt.datetime.now()
            stockticker.last_sale = StockTickerHistory.objects.get_or_create(symbol_id=row, updated_on=dt.date.today()).values('adjusted_close')
            stockticker.save()
    except RemoteDataError:
        print('remote error ' + row)
    except KeyError:
        print('key error ' + row)

