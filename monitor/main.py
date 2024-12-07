import time
import logging

from filings import Filings
from pymongo import MongoClient

if __name__ == "__main__":
  # setup logging
  logger = logging.basicConfig(level=logging.INFO)

  # set up mongo client
  # client = MongoClient("mongodb://mongo:27017")
  client = MongoClient("mongodb://localhost:27017")
  db = client["insider"]
  file_instance = Filings(db, 2024, logger)
  while True:
    logging.info("Starting periodic check")
    file_instance.start()
    logging.getLogger().handlers[0].flush()
    time.sleep(300)