from django.db import models
from datetime import datetime
from websiteBackbone.models import Profile
from django.contrib.postgres.fields import ArrayField

class StockTicker(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    updated_time = models.DateTimeField(auto_now_add=True, null=True)
    adr_tso = models.FloatField(default=0.0)
    market_cap = models.FloatField(default=0.0)
    active = models.BooleanField()
    is_currency = models.BooleanField()
    country = models.CharField(max_length=100)
    exchange_market = models.CharField(max_length=100)
    ipo_year = models.DateTimeField(null=True)
    industry = models.CharField(max_length=100)
    last_sale = models.FloatField(default=0.0)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)

    def get_stock_ticker_from_symbol(symbol):
        try:
            return StockTicker.objects.filter(id=symbol).last()
        except Exception as e:
            return print(e)


class StockTickerHistory(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.ForeignKey("StockTicker", on_delete=models.CASCADE)
    updated_on = models.DateTimeField(null=True)
    open = models.FloatField(default=0.0)
    close = models.FloatField(default=0.0)
    adjusted_close = models.FloatField(default=0.0)
    high = models.FloatField(default=0.0)
    low = models.FloatField(default=0.0)
    volume = models.FloatField(default=0.0)
    dividend = models.FloatField(default=0.0)
    plot = models.TextField(blank=True, default="")
    sma_thirty_day = models.FloatField(default=0.0)
    sma_fifty_day = models.FloatField(default=0.0)
    sma_hundred_fifty_day = models.FloatField(default=0.0)
    sma_two_hundred_day = models.FloatField(default=0.0)
    rsi = models.FloatField(default=0.0)
    ml_confidence = models.TextField(blank=True, default="")
    ml_predictions = models.TextField(blank=True, default="")
    simple_stat_buy_signal = models.BooleanField(default=False)
    green_dot_values = ArrayField(models.FloatField(default=0), null=True, blank=True)
    green_dot_dates = ArrayField(models.DateField(), null=True, blank=True)
    decision_tree_plot = models.TextField(blank=True, default="")
    rsi_plot = models.TextField(blank=True, default="")
    sma_plot = models.TextField(blank=True, default="")
    svr_plot = models.TextField(blank=True, default="")

    def get_history_from_symbol(symbol):
        try:
            return StockTickerHistory.objects.filter(symbol_id=symbol).last()
        except Exception as e:
            return print(e)

    def get_todays_history_from_symbol(symbol):
        try:
            return StockTickerHistory.objects.filter(symbol_id=symbol).filter(updated_on__range=[datetime(2020,10,22),datetime.utcnow()]).last()
        except Exception as e:
            return print(e)


class Earnings(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.FloatField(default=0.0)
    earnings_date = models.DateTimeField()
    symbol = models.ForeignKey("StockTicker", on_delete=models.CASCADE)
    portfolio = models.ForeignKey("Portfolio", on_delete=models.CASCADE)


class Account(models.Model):
    """A brokerage account"""

    ACCOUNT_TYPES = (
        ('TRADITIONAL', 'Traditional IRA or 401(k)'),
        ('ROTH', 'Roth IRA or 401(k)'),
        ('STANDARD', 'Standard Brokerage'),
    )

    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=100, choices=ACCOUNT_TYPES)
    cash_balance = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

#Additional Position Ideas: https://forum.djangoproject.com/t/django-model-to-save-a-stock-portfolio-to-db/3290
class Portfolio(models.Model):
    """A position, such as an equity holding"""
    models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    symbol = models.ForeignKey("StockTicker", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    purchased_on = models.DateTimeField()
    quantity = models.FloatField()
    cost_basis = models.FloatField(default=0.0)
    account_id = models.ForeignKey("Account", on_delete=models.CASCADE)
    userprofile_id = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.symbol
