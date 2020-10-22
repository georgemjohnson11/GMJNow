from .backend.MLBuySell import do_ml
from .automation.get_stocks import backpopulate_stock_history_2015
from .backend.StockScreener import movingAverageAnalysis
from .backend.GL_loop import GL_calculator
from .backend.plots import *
from financeAnalysis.finance_form import FinanceForm
from financeAnalysis.automation.get_stocks import backpopulate_stock_history_2015
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
            backpopulate_stock_history_2015()
        context['stocktickers'] = stocktickers
        backpopulate_stock_history_2015()
        return context

class financeAnalysisDetail():
    model = StockTickerHistory
    template_name = 'financeHome.html'

    def get_context_data(self, **kwargs):
        context = super(financeAnalysisDetail,self).get_context_data(**kwargs)

    def analysis_page(request):
        errors = ""
        args = {}
        if request.method == "POST":
            try:
                form = FinanceForm(request.POST)
                if form.is_valid():
                    stock_ticker_symbol = form.cleaned_data['stock_ticker_symbol']
                    stock_history = StockTickerHistory.get_history_from_symbol(symbol=stock_ticker_symbol)
                    stock_ticker = StockTicker.get_stock_ticker_from_symbol(stock_ticker_symbol)
                    stock_pickle = os.path.join(settings.BASE_DIR, 'stock_dfs', stock_ticker_symbol + '.pickle')
                    portfolio_plot = stock_history.plot
                    print("portfolio complete")
                    svr_prediction_plot = stock_history.svr_plot
                    rsi_plot = stock_history.rsi_plot
                    decision_tree_plot = stock_history.decision_tree_plot
                    buy_sell_moving_avg_plot = stock_history.sma_plot
                    simpleStatsTable = movingAverageAnalysis(stock_ticker_symbol)
                    args['result'] = stock_history.ml_predictions
                    args['confidence'] = stock_history.ml_confidence
                    print("simplestats complete")
                    if os.path.exists(stock_pickle):
                        list_green_line_values = GL_calculator(stock_ticker_symbol)
                        print("GL complete")
                        args['simpleStats'] = simpleStatsTable.to_html(classes='table-dark')
                        # args['otherData'] = otherDataTable.to_html(classes='table-dark')
                        args['stock_ticker'] = stock_ticker
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
            return render(request, 'websiteBackbone/includes/404.html', args)
