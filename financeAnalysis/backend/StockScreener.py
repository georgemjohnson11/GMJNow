
import pandas as pd
from lxml import html
import requests
import json
import argparse
from collections import OrderedDict
from .portfolioManagement import getPortfolio


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

def movingAverageAnalysis(ticker):

	exportList= pd.DataFrame(columns=["50 Day SMA", "150 Day SMA", "200 Day SMA", "52 Week Low", "52 week High", "RSI", "Buy Signal"])
	otherDataList = pd.DataFrame(columns=["Earning Per Share", "Price to Earnings Ratio","Forward Dividend & Yield", "Earnings Date", "Last Dividend Date", "1y Target Est", "Day's Range","url"])
	try:
		df = getPortfolio(ticker)[-400:]
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
		smaUsed=[50,150,200]
		for x in smaUsed:
			sma=x
			df["SMA_"+str(sma)]=round(df['Adj Close'].rolling(window=sma).mean(),2)

		#Get the difference in daily price
		delta = df['Adj Close'].diff(1)
		delta = delta.dropna()
		up= delta.copy()
		down = delta.copy()
		up[up<0] = 0
		down[down>0] = 0

		period =14
		AVG_GAIN = up.rolling(window=period).mean()
		AVG_LOSS = abs(down.rolling(window=period).mean())

		#Calculate Relative Strength (RS)
		df["RS"] = AVG_GAIN /AVG_LOSS
		#Calculate RSI
		df["RSI"] = 100.0 - (100.0 / (1.0 + df["RS"]))

		currentClose=df["Adj Close"][-1]
		moving_average_50=df["SMA_50"][-1]
		moving_average_150=df["SMA_150"][-1]
		moving_average_200=df["SMA_200"][-1]
		current_RSI = df["RSI"][-1]
		low_of_52week=round(min(df["Adj Close"][-260:]), 4)
		high_of_52week=round(max(df["Adj Close"][-260:]), 4)
		print(df)
		try:
			moving_average_200_20 = df["SMA_200"][-20]

		except Exception:
			moving_average_200_20=0

		#Condition 1: Current Price > 150 SMA and > 200 SMA
		if(currentClose>moving_average_150>moving_average_200):
			cond_1=True
		else:
			cond_1=False
		#Condition 2: 150 SMA and > 200 SMA
		if(moving_average_150>moving_average_200):
			cond_2=True
		else:
			cond_2=False
		#Condition 3: 200 SMA trending up for at least 1 month (ideally 4-5 months)
		if(moving_average_200>moving_average_200_20):
			cond_3=True
		else:
			cond_3=False
		#Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
		if(moving_average_50>moving_average_150>moving_average_200):
			#print("Condition 4 met")
			cond_4=True
		else:
			#print("Condition 4 not met")
			cond_4=False
		#Condition 5: Current Price > 50 SMA
		if(currentClose>moving_average_50):
			cond_5=True
		else:
			cond_5=False
		#Condition 6: Current Price is at least 30% above 52 week low (Many of the best are up 100-300% before coming out of consolidation)
		if(currentClose>=(1.3*low_of_52week)):
			cond_6=True
		else:
			cond_6=False
		#Condition 7: Current Price is within 25% of 52 week high
		if(currentClose>=(.75*high_of_52week)):
			cond_7=True
		else:
			cond_7=False
		#Condition 8: IBD RS rating >70 and the higher the better
		if(current_RSI>70):
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


		if(cond_1 and cond_2 and cond_3 and cond_4 and cond_5 and cond_6 and cond_7 and cond_8):
			exportList = exportList.append({"50 Day SMA": moving_average_50, "150 Day SMA": moving_average_150, "200 Day SMA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week, "RSI": current_RSI, "Buy Signal": 'Yes'}, ignore_index=True)
			return exportList
	except Exception:
		print("No data on "+ticker)
	exportList = exportList.append({"50 Day SMA": moving_average_50, "150 Day SMA": moving_average_150, "200 Day SMA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week, "RSI": current_RSI, "Buy Signal": 'No'}, ignore_index=True)
	return exportList

