import re
import requests
import json

class Webhook:
  def __init__(self):
    self.titles = ["Mr", "Mrs", "Ms", "Miss", "Dr", "Prof"]
    self.middle_initial_pattern = r'\b[A-Z]\.\s*'
    self.session = requests.session()
    self.maxLineChar = 50 # max number in a line for a embedded table
    self.tickerStart = 0
    self.typeStart = 9
    self.boughtStart = 17
    self.filedStart = 31
    self.sizeStart = 44
    self.webhook = "https://discord.com/api/webhooks/1314047025003892798/jkZJTnpTc09rAxZtjZHvqKXOttrMp6OCii_aZxuWQbsGtsaGv4MeibHIwF9VKmoRX33a"
    self.header = { 'Content-Type': 'application/json' }
    self.template = {
        "content": None,
        "embeds": [
          {
            "title": "{name} Transaction!",
            "description": "🚨 `NOT FINANCIAL ADVICE DYOR` 🚨\n\n```\n{transaction}\n```\n📏 `Size Guide`\n```\nLabel    Size\n1S       $1,001       -  $15,000\n2S       $15,001      -  $50,000\n3S       $50,001      -  $100,000\n1L       $100,001     -  $250,000\n2L       $250,001     -  $500,000\n3L       $500,001     -  $1,000,000\n1XL      $1,000,001   -  $5,000,000\n2XL      $5,000,001   -  $25,000,000\n3XL      $25,000,001  -  $50,000,000\nXXL      $50,000,000+\n```",
            "color": None,
            "thumbnail": {
              "url": "https://www.congress.gov/img/member/{bioguide}_200.jpg"
            }
          }
        ],
        "attachments": []
      }

  def send(self, txs, row, bioguide):
    if len(txs) == 0:
      return
    name = row["First"] + " " + row["Last"]
    name = self.cleanName(name)
    data = self.template
    data["embeds"][0]["title"] = data["embeds"][0]["title"].replace("{name}", name)
    txTable = self.formatFilings(txs)
    data["embeds"][0]["description"] = data["embeds"][0]["description"].replace("{transaction}", f"{txTable}")
    data["embeds"][0]["thumbnail"]["url"] = data["embeds"][0]["thumbnail"]["url"].replace("{bioguide}", bioguide.lower())
    requests.request("POST", self.webhook, headers=self.header, data=json.dumps(data))

  def formatFilings(self, txs):
    text = "Ticker    Type    Bought        Filed        Size"
    for item in txs:
      charPos = 0
      text += "\n"
      text += item["Ticker"]
      charPos += len(item["Ticker"])
      while charPos <= self.typeStart: 
        text += " "
        charPos += 1
      text += item["Type"]
      charPos += len(item["Type"])
      while charPos <= self.boughtStart:
        text += " "
        charPos += 1
      text += item["Bought"]
      charPos += len(item["Bought"])
      while charPos <= self.filedStart:
        text += " "
        charPos += 1
      text += item["Filed"]
      charPos += len(item["Filed"])
      while charPos <= self.sizeStart:
        text += " "
        charPos += 1
      text += self.orderSize(item["Amount"])
    return text
      
  def orderSize(self, amount):
    if "$1,001" in amount:
      return "1S"
    if "$15,001" in amount:
      return "2S"
    if "$50,001" in amount:
      return "3S"
    if "$100,001" in amount:
      return "1L"
    if "$250,001" in amount:
      return "2L"
    if "$500,001" in amount:
      return "3L"
    if "$1,000,001" in amount:
      return "1XL"
    if "$5,000,001" in amount:
      return "2XL"
    if "$25,000,001" in amount:
      return "3XL"
    if "$50,000,000" in amount:
      return "XXL"

  def cleanName(self, name):
    name = re.sub(r'\b(' + '|'.join(self.titles) + r')\.?\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+s\b', '', name, flags=re.IGNORECASE)
    name = re.sub(self.middle_initial_pattern, '',name)
    return name

    # response = requests.request("POST", self.webhook, headers=self.header, data=self.template)