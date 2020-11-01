# Look into Airflow for scheduling adn Media Root https://www.saturncloud.io/s/job-scheduling-with-python/
import os
import smtplib
from email.message import EmailMessage
import datetime
from datetime import datetime as dt
from financeAnalysis.models import StockTicker, StockTickerHistory
import pickle

EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')


def emailAlert(tickers, msg):

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


def greendotAlert():
    three_days_alert = (dt.today() - datetime.timedelta(days=3))
    ticker_list = []
    for ticker in StockTicker.objects.all().values('id'):
        if StockTickerHistory.get_todays_history_from_symbol().green_dot_dates > three_days_alert:
            ticker_list.append(ticker)

    separator = ', '
    message = "The following " + separator.join(ticker_list) +" have crossed the Green Dot threshold"+\
		 "\n Determine Entry points that are in overall long term and short term uptrend. Optimal buying time is typically within 1-3 days of a "+\
		 "Green Dot appearing. This looks for the 10.4 stochastic crosses above 4 day SMA after being oversold."

    msg = EmailMessage()
    msg['Subject'] = 'Green Dot Alert!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ''
    msg.set_content(message)
    if ticker_list.any():
        emailAlert(ticker_list,msg)
    return ticker_list, msg

def simpleStats_Buy_AlertSP500():

    three_days_alert = (dt.today() - datetime.timedelta(days=3))
    ticker_list = []
    print(ticker_list)
    separator = ', '
    message = "The following " + separator.join(ticker_list) +" have a Buy Signal today"+\
		 "\n Current Price is greater than the 150 day simple moving average (SMA) which is greater than 200 day SMA "+\
		 "\n 150 day simple moving average (SMA) > 200 day moving average "+\
		 "\n 200 day SMA has been trending for 1 month "+ \
          "\n Current Price is greater than the 50 day SMA" + \
          "\n Current Price is 30% Greater than 52 week low " + \
          "\n Relative Strength Index (RSI)  is greater than 70 " + \
          "\n Current price is within 25% of 52 week high "
    msg = EmailMessage()
    msg['Subject'] = 'Buy Signal Alert!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ''
    msg.set_content(message)

    return ticker_list, msg


simpleStats_Buy_AlertSP500()