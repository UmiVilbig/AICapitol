from datetime import datetime, timedelta

def closestWeekday(date):
  if type(date) is str:
    date = datetime.strptime(date, '%m/%d/%Y')
  weekday = date.weekday()
  if weekday >= 5:
    date -= timedelta(days=weekday -4)

  return date