import io
import pandas
import re
import os

from datetime import date
from urllib.request import urlopen
from pypdf import PdfReader
from webhook import Webhook
from txInfo import TxInfo
from fuzzywuzzy import fuzz
from utility import closestWeekday
from playsound import playsound
from error import Error

class Filings:
  def __init__(self, db, year, logger):
    self.logger = logger
    self.trades_db = db.trades
    self.congressmen_db = db.congressmens
    self.today = date.today().strftime("%m/%d/^y")
    self.url = f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.txt"
    self.fileDocURL = "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2024/{docID}.pdf"
    self.stockCode = "ST"
    self.titles = ["Mr", "Mrs", "Ms", "Miss", "Dr", "Prof"]
    self.middle_initial_pattern = r'\b[A-Z]\.\s*'
    self.ticker_pattern = r'\([A-Z]{1,5}\)'
    self.endTHead_pattern = r'\$\d+(?:\.\d+)*'
    self.endTx_pattern = r'^F S: (.*)$'
    self.description_pattern = r'D:\s*'
    self.tx_pattern = r"^(P|S|E)"
    self.date_pattern = r'(\d{2}/\d{2}/\d{4})'
    self.owner_pattern = r'^(DC|JT|SP)\s'
    self.asset_class_pattern = r'\[(.*?)\]'
    self.amount_pattern = r'\$(\d{1,3}(,\d{3})*(\.\d{2})?)\s*-\s*\$(\d{1,3}(,\d{3})*(\.\d{2})?)|over\s*\$50,000,000'
    self.knownMissingMembers = ["'Michael  Collins'"]

    # EDGE CASES
    self.filingInTx = "Filing ID #"
    self.orderTypeFcked = r"[A-Za-z]+[PSE](?=\s\d)|\)?[PSE](?=\s\d)"
    self.orderTypeFckedParse = r"([A-Za-z]*|[^\w\s]*)([PSE])"
    self.tHeaders = ["Type", "Date Notification", "Date", "Amount Cap.", "Gains >", "$200?"]
    self.subHolding = "S O: "
    self.exact_amount = r'\$(\d{1,3}(,\d{3})*(\.\d{2})?)'

  def start(self):
    with urlopen(self.url) as response:
      data_in_memory = io.StringIO(response.read().decode())
      self.df = pandas.read_csv(data_in_memory, sep="\t")

    self.filterLatest()

    if self.df.empty:
      print("no filings today")
      return
    
    # check and drops already in the db doc ids
    self.checkTxInDB()

    if self.df.empty:
      self.logger.info("No new filings today")
      return
    
    for i, row in self.df.iterrows():
      try:
        docID = row["DocID"]
        lines = self.pullFiling(docID)
        txs = self.isolateTxs(lines)
        txs = self.parseTxs(txs)
        txs = self.addDetailsToTx(txs)
        bioguide = self.createTxEntry(txs, row)
        current_dir = os.getcwd()
        playsound(f"{current_dir}\\done.mp3")
      except Exception as e:
        Error().notify(e, docID)

      # committees = self.congressmen_db.find_one({ "bioguide": bioguide })["committees"]
      # Webhook().send(txs, row, bioguide, committees)
      
  
  def cleanName(self, name):
    name = re.sub(r'\b(' + '|'.join(self.titles) + r')\.?\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+s\b', '', name, flags=re.IGNORECASE)
    name = re.sub(self.middle_initial_pattern, '',name)
    return name

  def findMember(self, first, last):
    fullName = first + " " + last
    member = self.congressmen_db.find_one({ "fullName": fullName })
    if member:
      return member
    fullName = self.cleanName(first) + " " + self.cleanName(last)
    member = self.congressmen_db.find_one({ "fullName": fullName })
    if member:
      return member
    member = self.congressmen_db.find_one({ "first": first, "last": last })
    if member:
      return member
    first = first.split(" ")[0]
    last = last.split(" ")[0]
    member = self.congressmen_db.find_one({ "first": first, "last": last })
    if member:
      return member
    member = self.congressmen_db.find({ "last": last })
    found = False
    print(f"could not use find_one query and switching to Jaro-Winkler Distnace for {first + last}")
    # self.logger.info(f"could not use find_one query and switching to Jaro-Winkler Distnace for {fullName}")
    for item in member:
      if fuzz.partial_ratio(first, item["first"]) > 65:
        # self.logger.info(f"Used the first name from distance and writing to {member["fullName"]} doc")
        print(f"Used the first name from distance and writing to {item["fullName"]} doc")
        member = item
        found = True
        break
      else:
        print(f"Distance too far {fuzz.partial_ratio(first, item["first"])}")
    if member and found:
      return member
    # last resort
    member = self.congressmen_db.find({ "first": first })
    for item in member:
      if fuzz.partial_ratio(last, item["last"]) > 65:
        # self.logger.info(f"Used the first name from distance and writing to {member["fullName"]} doc")
        print(f"Used the first name from distance and writing to {item["fullName"]} doc")
        member = item
        found = True
        break
      else:
        print(f"Distance too far {fuzz.partial_ratio(last, item["last"])}")
    if member and found:
      return member
    else:
      return None
      # raise "Could not find member with a close enough distance"

  def filterLatest(self):
    self.df.sort_values(by="FilingDate", ascending=False)
    # self.df = self.df[self.df["FilingDate"] == self.today]
    # self.df = self.df[self.df["FilingDate"] == "11/21/2024"]
    self.df = self.df[self.df["DocID"].astype(str).str.startswith('200')]

  def checkTxInDB(self):
    for i, row in self.df.iterrows():
      docID = row["DocID"]
      inDB = self.trades_db.find_one({ "id": docID })
      if inDB:
        self.df.drop(i, inplace=True)

  def pullFiling(self, docID):
    url = self.fileDocURL.replace("{docID}", str(docID))
    with urlopen(url) as response:
      pdf_bytes = io.BytesIO(response.read())
      reader = PdfReader(pdf_bytes)

    # pull all the text
    text = ""
    for x in range(len(reader.pages)):
      page = reader.pages[x]
      text += page.extract_text()
    lines = text.splitlines()
    lines = [x.replace('\x00', '') for x in lines]
    return lines
  
  def isolateTxs(self, lines):
    for i, line in enumerate(lines):
      if re.search(self.endTHead_pattern, line):
        lines = lines[i + 1:]
        break

    # in case of multiple pages
    for header in self.tHeaders:
      while header in lines:
        lines.remove(header)

    tx, txs = "", []
    for i, line in enumerate(lines):
      if re.search(self.endTx_pattern, line):
        tx = tx.replace("ID Owner Asset Transaction", "")
        txs.append(tx)
        tx = ""
        continue
      if not re.search(self.description_pattern, line):
        if not self.filingInTx in line:
          match = re.search(self.orderTypeFcked, tx)
          if match:
            prefix, suffix = tx[:match.start()], tx[match.end():]
            match_str = match.group()
            match = re.match(self.orderTypeFckedParse, match_str)
            word, orderType = match.group(1), match.group(2)
            if word == "":
              tx += line
            else:
              tx = prefix + word + " " + line + orderType + suffix
          else:
            if not self.subHolding in line:
              tx += line
    return txs

  def parseTxs(self, txs):
    transactions = []
    for tx in txs:
      asset = re.search(self.asset_class_pattern, tx)
      if not asset:
        continue

      owner = re.search(self.owner_pattern, tx)
      if owner and owner.group(0):
        tx = tx.replace(owner.group(0), "")

      asset_class = asset.group(1)
      if asset_class != self.stockCode:
        break

      stock = tx.split(f"[{asset_class}]")[0]
      ticker = re.search(self.ticker_pattern, stock)
      if ticker:
        ticker = ticker.group()[1:-1]
      tx = tx.replace(f"{stock}", "")
      tx = tx.replace(f"[{asset_class}]", "")

      # sometimes the first char is a space and causes error so remove it
      if tx[0] == " ":
        tx = tx[1:]

      orderType = re.search(self.tx_pattern, tx)
      if orderType:
        orderType = orderType.group(0)
      dates = re.findall(self.date_pattern, tx)
      amount = re.search(self.amount_pattern, tx)
      if not amount:
        amount = re.search(self.exact_amount, tx)
      if amount:
        amount = amount.group(0)

      # validate the fields
      tx = {
        "Stock": stock,
        "Ticker": ticker,
        "Class": asset_class,
        "Type": orderType,
        "Bought": dates[0],
        "Filed": dates[1],
        "Amount": amount
      }
      transactions.append(tx)

    return transactions
  
  def addDetailsToTx(self, txs):
    info = TxInfo()
    today = closestWeekday(date.today()).strftime('%m/%d/%Y')
    for tx in txs:
      if not tx["Ticker"]:
        print(f"Problem parsing tx for ticker ignoring the issue for now")
        tx = self.tempValues(tx)
        continue
      tx["BuyPrice"] = info.getPriceOnDate(tx["Ticker"], tx["Bought"])
      tx["FilePrice"] = info.getPriceOnDate(tx["Ticker"], closestWeekday(tx["Filed"]))
      tx["MonitorPrice"] = info.getPriceOnDate(tx["Ticker"], today)
      if tx["BuyPrice"] and tx["FilePrice"]:
        tx["Change"] = 100 * ((tx["FilePrice"] - tx["BuyPrice"]) / tx["BuyPrice"])
      else:
        tx["Change"] = float('nan')
      roi30, ytd, sector = info.getDetails(tx["Ticker"])
      tx["30DC"], tx["YTD"], tx["Sector"] = roi30, ytd, sector
    return txs
      
  # returns the thomas_id of the congressmen
  def createTxEntry(self, txs, row):
    member = self.findMember(row["First"], row["Last"])
    fullName, bioguide = "", ""
    if member:
      fullName = member["fullName"]
      bioguide = member["bioguide"]
    entry = {
      "id": row["DocID"],
      "txs": txs,
      "member": fullName,
      "date": row["FilingDate"]
    }
    _id = self.trades_db.insert_one(entry)
    _id = _id.inserted_id
    if(member):
      self.congressmen_db.update_one(
        {"_id": member["_id"]},
        {"$push": {"txs": _id}}
      )
    return bioguide
  
  def tempValues(self, tx):
    tx["BuyPrice"] = float('nan')
    tx["FilePrice"] = float('nan')
    tx["MonitorPrice"] = float('nan')
    tx["Change"] = float('nan')
    tx["30DC"] = float('nan')
    tx["YTD"] = float('nan')
    tx["Sector"] = None
    return tx
