
import pandas as pd
from lxml import html
import requests
import json
import argparse
from datetime import datetime, timedelta
from collections import OrderedDict
from .portfolioManagement import getPortfolio
from financeAnalysis.models import StockTickerHistory


def get_headers():
    return {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
            "cache-control": "max-age=0",
            "dnt": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}



def parse(ticker):
	try:
		url = "http://finance.yahoo.com/quote/%s?p=%s" % (ticker, ticker)
		response = requests.get(
			url, verify=False, headers=get_headers(), timeout=30)
		print("Parsing %s" % (url))
		parser = html.fromstring(response.text)
		summary_table = parser.xpath(
			'//div[contains(@data-test,"summary-table")]//tr')
		summary_data = OrderedDict()
		other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(
			ticker)
		summary_json_response = requests.get(other_details_json_link)
		json_loaded_summary = json.loads(summary_json_response.text)
		try:
			summary = json_loaded_summary["quoteSummary"]["result"][0]
			y_Target_Est = summary["financialData"]["targetMeanPrice"]['raw']
			earnings_list = summary["calendarEvents"]['earnings']
			eps = summary["defaultKeyStatistics"]["trailingEps"]['raw']
			datelist = []

			for i in earnings_list['earningsDate']:
				datelist.append(i['fmt'])
			earnings_date = ' to '.join(datelist)

			for table_data in summary_table:
				raw_table_key = table_data.xpath(
					'.//td[1]//text()')
				raw_table_value = table_data.xpath(
					'.//td[2]//text()')
				table_key = ''.join(raw_table_key).strip()
				table_value = ''.join(raw_table_value).strip()
				summary_data.update({table_key: table_value})
			summary_data.update({'1y Target Est': y_Target_Est, 'EPS (TTM)': eps,
								 'Earnings Date': earnings_date, 'ticker': ticker,
								 'url': url})
			return summary_data
		except ValueError:
			print("Failed to parse json response")
			return {"error": "Failed to parse json response"}
		except:
			return {"error": "Unhandled Error"}
	except requests.exceptions.RequestException as e:  # This is the correct syntax
		raise SystemExit(e)

def buy_signal_indicator(ticker, date=datetime.today()):
	exportList= pd.DataFrame(columns=["50 Day SMA", "150 Day SMA", "200 Day SMA", "52 Week Low", "52 week High", "RSI", "Buy Signal"])
	otherDataList = pd.DataFrame(columns=["Earning Per Share", "Price to Earnings Ratio","Forward Dividend & Yield", "Earnings Date", "Last Dividend Date", "1y Target Est", "Day's Range","url"])
	try:
		df = getPortfolio(ticker)[-260:]
		stock_info = StockTickerHistory.objects.get(symbol_id=ticker, updated_on=date)
		days_ago_20 = date - timedelta(days=20)
		stock_info_20_days_ago = stock_info = StockTickerHistory.objects.get(symbol_id=ticker, updated_on=days_ago_20)
		# summary = parse(ticker)
		# print(summary)
		# pe = summary["PE Ratio (TTM)"]
		# eps = summary["EPS (TTM)"]
		# pctyield = summary["Forward Dividend & Yield"]
		# earningsdate= summary["Earnings Date"]
		# lastdividenddate = summary["Ex-Dividend Date"]
		# one_year_est = summary["1y Target Est"]
		# daysRange = summary["Day's Range"]
		# reference = summary["url"]
		# if(pe):
		# 	otherDataList = otherDataList.append({"Earning Per Share": eps, "Price to Earnings Ratio":pe,"Forward Dividend & Yield": pctyield, "Earnings Date": earningsdate, "Last Dividend Date": lastdividenddate, "1y Target Est": one_year_est, "Day's Range": daysRange, "url": reference}, ignore_index=True)
		# 	print(otherDataList)

		low_of_52week=round(min(df["adjusted_close"][-260:]), 4)
		high_of_52week=round(max(df["adjusted_close"][-260:]), 4)
		currentClose = stock_info.adjusted_close
		moving_average_150 = stock_info.sma_hundred_fifty_day
		moving_average_200 = stock_info.sma_two_hundred_day
		moving_average_50 = stock_info.sma_fifty_day
		current_RSI = stock_info.rsi
		#Condition 1: Current Price > 150 SMA and > 200 SMA
		if currentClose>moving_average_150>moving_average_200:
			cond_1=True
		else:
			cond_1=False
		#Condition 2: 150 SMA and > 200 SMA
		if moving_average_150>moving_average_200:
			cond_2=True
		else:
			cond_2=False
		#Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
		if moving_average_200>stock_info_20_days_ago.sma_two_hundred_day:
			cond_3=True
		else:
			cond_3=False
		#Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
		if moving_average_50>moving_average_150>moving_average_200:
			#print("Condition 4 met")
			cond_4=True
		else:
			#print("Condition 4 not met")
			cond_4=False
		#Condition 5: Current Price > 50 SMA
		if currentClose>moving_average_50:
			cond_5=True
		else:
			cond_5=False
		#Condition 6: Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)
		if currentClose>=(1.3 * low_of_52week):
			cond_6=True
		else:
			cond_6=False
		#Condition 7: Current Price is within 25% of 52 week high
		if currentClose>=(.75 * high_of_52week):
			cond_7=True
		else:
			cond_7=False
		#Condition 8: IBD RS rating >70 and the higher the better
		if current_RSI>70:
			cond_8=True
		else:
			cond_8=False
		# P/ E < 25
		# if (pe < 25):
		# 	cond_9 = True
		# else:
		# 	cond_9 = False
		# # EPS (earning per share) > 0
		# if (eps > 0):
		# 	cond_10 = True
		# else:
		# 	cond_10 = False
		# if (eps > 0):
		# 	cond_10 = True
		# else:
		# 	cond_10 = False
		# #Other Conditions: Yield > 4%
		# if (pctyield.split(' (')[1][2] > 0):
		# 	cond_11 = True
		# else:
		# 	cond_11 = False
		# #Payout Ratio <90
		# if (eps):
		# 	cond_9 = True
		# 	cond_10 = True
		# 	cond_11 = True


		if cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7 and cond_8:
			stock_info.simple_stat_buy_signal = True
			stock_info.save()
	except Exception:
		print("No data on "+ticker)
	return exportList

