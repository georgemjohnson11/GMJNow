from .backend.MLBuySell import do_ml
from .backend.StockScreener import movingAverageAnalysis
from .backend.GL_loop import GL_calculator
from .backend.plots import *
from financeAnalysis.finance_form import FinanceForm
from django.shortcuts import render, get_object_or_404
import os
from django.conf import settings
from django.urls import reverse
from django.views.generic import DetailView
font_dict = {'family': 'serif',
             'color': 'black',
             'size': 15}


class financeAnalysisDetail():

    def analysis_page(request):
        errors = ""
        args = {}
        if request.method == "POST":
            try:
                form = FinanceForm(request.POST)
                if form.is_valid():
                    stock_ticker_symbol = form.cleaned_data['stock_ticker_symbol']
                    stock_pickle = os.path.join(settings.BASE_DIR, 'stock_dfs', stock_ticker_symbol + '.pickle')
                    portfolio_plot = retrieve_base64_ticker_overview_fig(stock_ticker_symbol)
                    print("portfolio complete")
                    svr_prediction_plot = retrieve_base64__svr_prediction_build_fig(stock_ticker_symbol)
                    rsi_plot = retrieve_base64_rsi_fig(stock_ticker_symbol)
                    decision_tree_plot = retrieve_base64_decisionTreePrediction_fig(stock_ticker_symbol)
                    buy_sell_moving_avg_plot = retrieve_base64__buy_sell_points_fig(stock_ticker_symbol)
                    print("Retrieveing Plots complete")
                    if os.path.exists(stock_pickle):

                        simpleStatsTable = movingAverageAnalysis(stock_ticker_symbol)
                        print("simplestats complete")
                        list_green_line_values = GL_calculator(stock_ticker_symbol)
                        print("GL complete")
                        args['result'] = retrieve_machine_learning_prediction(stock_ticker_symbol)
                        args['confidence'] = retrieve_machine_learning_confidence(stock_ticker_symbol)
                        print("machine learning complete")
                        args['simpleStats'] = simpleStatsTable.to_html(classes='table-dark')
                        # args['otherData'] = otherDataTable.to_html(classes='table-dark')
                        args['stock_ticker_symbol'] = stock_ticker_symbol
                        args['viewSVR'] = svr_prediction_plot
                        args['viewShowRSI'] = rsi_plot
                        args['viewdecisionTree'] = decision_tree_plot
                        args['view_portfolio_plot'] = portfolio_plot
                        args['viewBuySellMA'] = buy_sell_moving_avg_plot
                        args['green_line_values'] = list_green_line_values.to_html(classes='table-dark')
                        print("Processing complete")
                        return render(request, 'financeHome.html', args)
            except Exception as e:
                args['errors'] = "Please try another ticker"
                return render(request, 'websiteBackbone/includes/404.html', args)
        else:
            args['errors'] = "Please try another ticker"
            return render(request, 'websiteBackbone/includes/404.html', args)
