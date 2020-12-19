from .backend.GL_loop import GL_calculator
from .backend.plots import *
from financeAnalysis.finance_form import FinanceForm
from financeAnalysis.automation.get_stocks import populate_todays_history,backpopulate_ticker_history, backpopulate_stock_history_2020, repopulate_todays_history
from django.shortcuts import render, get_object_or_404
import os
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from financeAnalysis.models import StockTicker, StockTickerHistory
from django.views.generic import ListView
font_dict = {'family': 'serif',
             'color': 'black',
             'size': 15}


class StockTickerListView(ListView):
    context_object_name = "stocktickers"
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stocktickers = StockTicker.objects.all().order_by("id")
        paginator = Paginator(stocktickers, self.paginate_by)
        page = self.request.GET.get('page')

        try:

            stocktickers = paginator.page(page)
        except PageNotAnInteger:
            stocktickers = paginator.page(1)
        except EmptyPage:
            stocktickers = paginator.page(paginator.num_pages)
        except Exception as e:
            print(e)
        context['stocktickers'] = stocktickers
        return context

class financeAnalysisDetail:
    model = StockTickerHistory
    template_name = 'financeHome.html'

    def get_context_data(self, **kwargs):
        context = super(financeAnalysisDetail,self).get_context_data(**kwargs)

    def update(request):
        populate_todays_history()
        return render(request, 'websiteBackbone/home.html')

    def repopulate(request):
        repopulate_todays_history()
        return render(request, 'websiteBackbone/home.html')

    def backpopulate_all(request):
        backpopulate_stock_history_2020()
        return render(request, 'websiteBackbone/home.html')

    def backpopulate(request, stock_ticker_symbol=''):
        backpopulate_ticker_history(stock_ticker_symbol)

    def analysis_page(request, stock_ticker_symbol=''):
        errors = ""
        args = {}
        if request.method == "POST":
            try:
                form = FinanceForm(request.POST)
                if form.is_valid():
                    stock_ticker_symbol = form.cleaned_data['stock_ticker_symbol']
                    stock_history = StockTickerHistory.get_todays_history_from_symbol(stock_ticker_symbol)
                    stock_ticker = StockTicker.get_stock_ticker_from_symbol(stock_ticker_symbol)
                    portfolio_plot = stock_history.plot
                    svr_prediction_plot = stock_history.svr_plot
                    rsi_plot = stock_history.rsi_plot
                    decision_tree_plot = stock_history.decision_tree_plot
                    buy_sell_moving_avg_plot = stock_history.sma_plot
                    if stock_history.ml_predictions:
                        args['result'] = stock_history.ml_predictions
                        args['confidence'] = stock_history.ml_confidence
                    else:
                        args['result'] = 'N/A'
                        args['confidence'] = 'N/A'
                    if stock_history.green_dot_dates:
                        green_dot_dates = stock_history.green_dot_dates
                        green_dot_values = stock_history.green_dot_values
                        args['green_dot_values'] = zip(green_dot_dates, green_dot_values)
                    else:
                        args['green_dot_values'] = 'No green dot values created yet.'
                    args['simpleStats'] = stock_history.simple_stat_buy_signal
                    # args['otherData'] = otherDataTable.to_html(classes='table-dark')
                    args['symbol_id'] = stock_ticker_symbol
                    args['stock_ticker'] = stock_ticker
                    args['viewSVR'] = svr_prediction_plot
                    args['viewShowRSI'] = rsi_plot
                    args['viewdecisionTree'] = decision_tree_plot
                    args['view_portfolio_plot'] = portfolio_plot
                    args['viewBuySellMA'] = buy_sell_moving_avg_plot
                    return render(request, 'financeHome.html', args)
            except Exception as e:
                args['errors'] = "Please try another ticker"
                return render(request, 'websiteBackbone/includes/404.html', args)
        else:
            try:
                stock_history = StockTickerHistory.objects.filter(symbol_id=stock_ticker_symbol).order_by('updated_on').last()
                stock_ticker = StockTicker.objects.filter(id=stock_ticker_symbol).last()
                if stock_history:
                    args['stock_ticker'] = stock_ticker
                if stock_history:
                    portfolio_plot = stock_history.plot
                    svr_prediction_plot = stock_history.svr_plot
                    rsi_plot = stock_history.rsi_plot
                    decision_tree_plot = stock_history.decision_tree_plot
                    buy_sell_moving_avg_plot = stock_history.sma_plot
                    if stock_history.ml_predictions:
                        args['result'] = stock_history.ml_predictions
                        args['confidence'] = stock_history.ml_confidence
                    else:
                        args['result'] = 'N/A'
                        args['confidence'] = 'N/A'
                    if stock_history.green_dot_dates:
                        green_dot_dates = stock_history.green_dot_dates
                        green_dot_values = stock_history.green_dot_values
                        args['green_dot_values'] = zip(green_dot_dates, green_dot_values)
                    else:
                        args['green_dot_values'] = 'No green dot values created yet.'
                    args['simpleStats'] = stock_history.simple_stat_buy_signal
                    # args['otherData'] = otherDataTable.to_html(classes='table-dark')
                    args['symbol_id'] = stock_ticker_symbol
                    args['viewSVR'] = svr_prediction_plot
                    args['viewShowRSI'] = rsi_plot
                    args['viewdecisionTree'] = decision_tree_plot
                    args['view_portfolio_plot'] = portfolio_plot
                    args['viewBuySellMA'] = buy_sell_moving_avg_plot
                    args['green_dot_values'] = zip(green_dot_dates, green_dot_values)
                print("Processing complete")
                return render(request, 'financeHome.html', args)
            except Exception as e:
                args['errors'] = "Please try another ticker. Redirect issue"
                return render(request, 'websiteBackbone/includes/404.html', args)
