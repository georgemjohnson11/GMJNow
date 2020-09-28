import pickle as pl

def retrieve_base64_decisionTreePrediction_fig(ticker):
    filename = 'stock_dfs/' + ticker + '_decisionTreePrediction_fig.pickle'
    return convert_fig_to_base64(filename)

def retrieve_base64__svr_prediction_build_fig(ticker):
    filename = 'stock_dfs/' + ticker + '_svr_prediction_build_fig.pickle'
    return convert_fig_to_base64(filename)

def retrieve_base64__buy_sell_points_fig(ticker):
    filename = 'stock_dfs/' + ticker + '_buy_sell_points_fig.pickle'
    return convert_fig_to_base64(filename)


def retrieve_base64_rsi_fig(ticker):
    filename = 'stock_dfs/' + ticker + '_rsi_fig.pickle'
    return convert_fig_to_base64(filename)


def retrieve_base64_ticker_overview_fig(ticker):
    filename = 'stock_dfs/' + ticker + '_ticker_overview_fig.pickle'
    return convert_fig_to_base64(filename)


def convert_fig_to_base64(filename):
    with open(filename, 'rb') as f:
        fig = pl.load(f)
        return fig
