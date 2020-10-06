from django import forms

class FinanceForm(forms.Form):
    stock_ticker_symbol = forms.CharField(label='Stock Ticker Symbol', max_length=7)
