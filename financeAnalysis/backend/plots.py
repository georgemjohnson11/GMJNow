import pickle as pl
import os
import pandas as pd
from django.conf import settings

def retrieve_base64_decisionTreePrediction_fig(ticker):
    filename = settings.BASE_DIR + '/stock_dfs/' + ticker + '_decisionTreePrediction_fig.pickle'
    return convert_fig_to_base64(filename)

def retrieve_base64__svr_prediction_build_fig(ticker):
    filename = settings.BASE_DIR +  '/stock_dfs/' + ticker + '_svr_prediction_build_fig.pickle'
    return convert_fig_to_base64(filename)

def retrieve_base64__buy_sell_points_fig(ticker):
    filename = settings.BASE_DIR +  '/stock_dfs/' + ticker + '_buy_sell_points_fig.pickle'
    return convert_fig_to_base64(filename)


def retrieve_base64_rsi_fig(ticker):
    filename = settings.BASE_DIR +  '/stock_dfs/' + ticker + '_rsi_fig.pickle'
    return convert_fig_to_base64(filename)


def retrieve_base64_ticker_overview_fig(ticker):
    filename = settings.BASE_DIR +  '/stock_dfs/' + ticker + '_ticker_overview_fig.pickle'
    return convert_fig_to_base64(filename)

def retrieve_machine_learning_prediction(ticker):
    filename = os.path.join(settings.BASE_DIR, "stock_dfs", ticker + "_ml_predictions.pickle")
    if os.path.exists(filename):
        fig = pd.read_pickle(filename)
        if fig is not None:
            return fig
        else:
            return 'N/A'
    else:
        return 'N/A'

def retrieve_machine_learning_confidence(ticker):
    filename = os.path.join(settings.BASE_DIR, "stock_dfs", ticker + "_ml_confidence.pickle")
    if os.path.exists(filename):
        fig = pd.read_pickle(filename)
        if fig is not None:
            return fig
        else:
            return 'N/A'
    else:
        return 'N/A'

def convert_fig_to_base64(filename):
    with open(filename, 'rb') as f:
        fig = pl.load(f)
        if fig is not None:
            return fig
        else:
            return 'N/A'
