import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import pickle

def GL_calculator(ticker):
  with open("stock_dfs/{}.pickle".format(ticker), "rb") as f:
    tickers = pickle.load(f)

  tickers.drop(tickers[tickers["Volume"]<1000].index, inplace=True)

  now = dt.datetime.now()
  dfmonth=tickers.groupby(pd.Grouper(freq="M"))["High"].max()

  allGLVs = []
  allGLVdates = []
  glDate=0
  lastGLV=0
  currentDate=""
  curentGLV=0
  for index, value in dfmonth.items():
    if value > curentGLV:
      curentGLV=value
      currentDate=index
      counter=0
    if value < curentGLV:
      counter=counter+1

      if counter==3 and ((index.month != now.month) or (index.year != now.year)):
          if curentGLV != lastGLV:
            allGLVs.append(curentGLV)
            allGLVdates.append(glDate)
          glDate=currentDate
          lastGLV=curentGLV
          counter=0

  if lastGLV==0:
    message=ticker+" has not formed a green line yet"
  else:
    message=("Last Green Line: "+str(lastGLV)+" on "+str(glDate))
  GL = pd.DataFrame()
  GL['Dates'] = allGLVdates
  GL['GreenLightValue'] = allGLVs
  return GL


