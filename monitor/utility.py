from datetime import datetime, timedelta

def closestWeekday(date):
  if type(date) is str:
    date = datetime.strptime(date, '%Y-%m-%d')
  weekday = date.weekday()
  if weekday >= 5:
    date -= timedelta(days=weekday -4)
  return date

def spotDate(date, delta):
  if type(date) is str:
    date = datetime.strptime(date, '%m/%d/%Y')
  date += timedelta(days=delta)
  return closestWeekday(date.strftime('%Y-%m-%d'))

def getSpot(date1, date2):
  if type(date1) is str:
    date1 = datetime.strptime(date1, '%m/%d/%Y')
  if type(date2) is str:
    date2 = datetime.strptime(date2, '%m/%d/%Y')
  return abs((date1 - date2).days)

def convertDateFormat(date, delta = 0):
  if type(date) is not str:
    date = date.strftime('%m/%d/%Y')
  dateObj = datetime.strptime(date, '%m/%d/%Y') + timedelta(days=delta)
  return dateObj.strftime("%Y-%m-%d")