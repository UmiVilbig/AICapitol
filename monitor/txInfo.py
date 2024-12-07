import yfinance as yf
import pandas as pd

from datetime import datetime, timedelta, date

class TxInfo:
  def __init__(self):
    pass

  # filing date is in MM-DD-YYYY format but need to switch to yfinance YYYY-MM-DD format
  def getPriceOnDate(self, ticker, date) -> float:
    start = self.convertDateFormat(date)
    # include the filing date so grab the next day
    end = self.convertDateFormat(date, delta=1)
    data = yf.download(ticker, start=start, end=end, auto_adjust=True)
    avg = float((data["Close"].iloc[0] + data["Open"].iloc[0]).iloc[0]) / 2
    return round(avg, 2)
  
  def getDetails(self, ticker):
    info = yf.Ticker(ticker).get_info()
    today = datetime.today().strftime('%m/%d/%Y')
    lastMonth = (datetime.today() - timedelta(days=30)).strftime('%m/%d/%Y')
    today = self.getPriceOnDate(ticker, today)
    lastMonth = self.getPriceOnDate(ticker, lastMonth)
    roi30 = 100 * ((today - lastMonth) / lastMonth)
    ytd = info["52WeekChange"] * 100
    sector = info["sector"]
    return round(roi30, 2), round(ytd, 2), sector
    
  def convertDateFormat(self, date, delta = 0):
    dateObj = datetime.strptime(date, '%m/%d/%Y') + timedelta(days=delta)
    return dateObj.strftime("%Y-%m-%d")