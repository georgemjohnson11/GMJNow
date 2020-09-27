from .backend.MLBuySell import do_ml
from .backend.StockScreener import movingAverageAnalysis
from .backend.GL_loop import GL_calculator
from .backend.plots import *
from .finance_form import FinanceForm
from django.shortcuts import render, get_object_or_404
import os
from django.urls import reverse
from django.views.generic import DetailView
font_dict = {'family': 'serif',
             'color': 'black',
             'size': 15}


class financeAnalysisDetail():
    template_name = 'financeHome.html'

    def analysis_page(request):
        errors = ""
        if request.method == "POST":
            form = FinanceForm(request.POST)
            if form.is_valid():
                stock_ticker_symbol = form.cleaned_data['stock_ticker_symbol']
            if os.path.exists('stock_dfs/{}.csv'.format(stock_ticker_symbol)):
                portfolio_plot = displayPortfolioGraph(stock_ticker_symbol)
                print("portfolio complete")
                svr_prediction_plot = svr_prediction_build_plot(stock_ticker_symbol)
                print("svr learning complete")
                simpleStatsTable, otherDataTable = movingAverageAnalysis(stock_ticker_symbol)
                print("simplestats complete")
                decision_tree_plot = decisionTreePrediction(stock_ticker_symbol)
                buy_sell_moving_avg_plot = showBuySellPoints(stock_ticker_symbol)
                rsi_plot = showRSI(stock_ticker_symbol)
                list_green_line_values = GL_calculator(stock_ticker_symbol)
                confidence, result = do_ml(stock_ticker_symbol)
                print("machine learning complete")
                # context = {
                #     "result": result,
                #     "confidence": confidence,
                #     "simpleStats": simpleStatsTable.to_html(classes='table-dark'),
                #     "otherData": otherDataTable.to_html(classes='table-dark'),
                #     "stock_ticker_symbol": stock_ticker_symbol,
                #     "viewSVR": svr_prediction_plot,
                #     "viewShowRSI": rsi_plot,
                #     "viewdecisionTree": decision_tree_plot,
                #     "view_portfolio_plot": portfolio_plot,
                #     "viewBuySellMA": buy_sell_moving_avg_plot,
                #     "green_line_values": list_green_line_values,
                # }
                args = {}
                args['result'] = result
                args['confidence'] = confidence
                args['simpleStats'] = simpleStatsTable.to_html(classes='table-dark')
                args['otherData'] = otherDataTable.to_html(classes='table-dark')
                args['stock_ticker_symbol'] = stock_ticker_symbol
                args['viewSVR'] = svr_prediction_plot
                args['viewShowRSI'] = rsi_plot
                args['viewdecisionTree'] = decision_tree_plot
                args['view_portfolio_plot'] = portfolio_plot
                args['viewBuySellMA'] = buy_sell_moving_avg_plot
                args['green_line_values'] = list_green_line_values.to_html(classes='table-dark')
                print("Processing complete")
                return render(request, 'financeHome.html', args)
            else:
                return render(request, 'websiteBackbone/includes/404.html', {'context': form.errors})
            return render(request, 'financeHome.html', context)