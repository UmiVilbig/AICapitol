import time

from filings import Filings
from pymongo import MongoClient

if __name__ == "__main__":
  client = MongoClient("localhost", 27017)
  db = client["insider"]
  file_instance = Filings(db, 2024)
  while True:
    file_instance.start()
    time.sleep(300)