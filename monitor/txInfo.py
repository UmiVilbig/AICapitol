import yfinance as yf
import pandas as pd
import math
import json

from datetime import datetime, date, timedelta
from utility import closestWeekday

class TxInfo:
  def __init__(self):
    pass

  # filing date is in MM-DD-YYYY format but need to switch to yfinance YYYY-MM-DD format
  def getPriceOnDate(self, ticker, date) -> float:
    start = self.convertDateFormat(date)
    # include the filing date so grab the next day
    end = self.convertDateFormat(date, delta=1)
    data = yf.download(ticker, start=start, end=end, auto_adjust=True)
    if data.empty:
      return float('nan')
    avg = float((data["Close"].iloc[0] + data["Open"].iloc[0]).iloc[0]) / 2
    return round(avg, 2)
  
  def getStockInfo(self, ticker, start, end):
    start = self.convertDateFormat(start)
    end = self.convertDateFormat(end, delta=1)
    data = yf.download(ticker, start=start, end=end, auto_adjust=True)
    if data.empty:
      return float('nan')
    return data
  
  def getDetails(self, ticker):
    try:
      info = yf.Ticker(ticker).get_info()
      today = closestWeekday(date.today()).strftime('%m/%d/%Y')
      lastMonth = (date.today() - timedelta(days=30)).strftime('%m/%d/%Y')
      today = self.getPriceOnDate(ticker, today)
      lastMonth = self.getPriceOnDate(ticker, lastMonth)
      if not math.isclose(lastMonth, 0.0):
        roi30 = 100 * ((today - lastMonth) / lastMonth)
      else: 
        roi30 = float('nan')
      if '52WeekChange' in info.keys():
        ytd = info["52WeekChange"] * 100
      else:
        ytd = float('nan')
      if 'sector' in info.keys():
        sector = info["sector"]
      else:
        sector = None
      return round(roi30, 2), round(ytd, 2), sector
    except json.JSONDecodeError as e:
      print(f"[ERROR] JSON parse error retrying the function")
      return self.getDetails(ticker)
    
  def convertDateFormat(self, date, delta = 0):
    if type(date) is not str:
      date = date.strftime('%m/%d/%Y')
    dateObj = datetime.strptime(date, '%m/%d/%Y') + timedelta(days=delta)
    return dateObj.strftime("%Y-%m-%d")