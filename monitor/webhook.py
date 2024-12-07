import re
import requests
import json

class Webhook:
  def __init__(self):
    self.titles = ["Mr", "Mrs", "Ms", "Miss", "Dr", "Prof"]
    self.middle_initial_pattern = r'\b[A-Z]\.\s*'
    self.session = requests.session()
    self.maxLineChar = 50 # max number in a line for a embedded table
    self.webhook = "https://discord.com/api/webhooks/1314047025003892798/jkZJTnpTc09rAxZtjZHvqKXOttrMp6OCii_aZxuWQbsGtsaGv4MeibHIwF9VKmoRX33a"
    self.header = { 'Content-Type': 'application/json' }
    self.template = {
        "content": None,
        "embeds": [
          {
            "title": "{name} Transaction!",
            "description": "**__🚨 NOT FINANCIAL ADVICE DYOR 🚨__**\n```\n{transaction}\n```\n**__🤑 Price Details__**\n```\n{price}\n```\n**__🔍Company Details__**\n```\n{details}\n```\n**__🐱‍👤Governance__**\n{governance}\n\n📏 Size Guide\n```Size     From            To\n1S       $1,001       -  $15,000\n2S       $15,001      -  $50,000\n3S       $50,001      -  $100,000\n1L       $100,001     -  $250,000\n2L       $250,001     -  $500,000\n3L       $500,001     -  $1,000,000\n1XL      $1,000,001   -  $5,000,000\n2XL      $5,000,001   -  $25,000,000\n3XL      $25,000,001  -  $50,000,000\nXXL      $50,000,000+\n```",
            "color": None,
            "thumbnail": {
              "url": "https://www.congress.gov/img/member/{bioguide}_200.jpg"
            }
          }
        ],
        "attachments": []
      }

  def send(self, txs, row, bioguide, committees):
    if len(txs) == 0:
      return
    name = row["First"] + " " + row["Last"]
    name = self.cleanName(name)
    data = self.template
    data["embeds"][0]["title"] = data["embeds"][0]["title"].replace("{name}", name)
    txTable = self.formatFilings(txs)
    pricingTable = self.formatPricings(txs)
    detailsTable = self.formatDetails(txs)
    governanceTable = self.formatGovernance(committees)
    data["embeds"][0]["description"] = data["embeds"][0]["description"].replace("{transaction}", f"{txTable}")
    data["embeds"][0]["description"] = data["embeds"][0]["description"].replace("{price}", f"{pricingTable}")
    data["embeds"][0]["description"] = data["embeds"][0]["description"].replace("{details}", f"{detailsTable}")
    data["embeds"][0]["description"] = data["embeds"][0]["description"].replace("{governance}", f"{governanceTable}")
    data["embeds"][0]["thumbnail"]["url"] = data["embeds"][0]["thumbnail"]["url"].replace("{bioguide}", bioguide.lower())
    requests.request("POST", self.webhook, headers=self.header, data=json.dumps(data))

  def formatFilings(self, txs):
    type, bought, filed, size = 9, 16, 29, 41
    text = "Ticker    Type    Bought        Filed        Size"
    for item in txs:
      charPos = 0
      text += "\n"
      text += item["Ticker"]
      charPos += len(item["Ticker"])
      text += self.moveToPos(charPos, type)
      charPos = type

      text += item["Type"]
      charPos += len(item["Type"])
      text += self.moveToPos(charPos, bought)
      charPos = bought

      text += item["Bought"]
      charPos += len(item["Bought"])
      text += self.moveToPos(charPos, filed)
      charPos = filed

      text += item["Filed"]
      charPos += len(item["Filed"])
      text += self.moveToPos(charPos, size)
      text += self.orderSize(item["Amount"])
    return text
      
  def formatPricings(self, txs):
    bought, filed, now = 9, 18, 29
    text = "Ticker    Bought    Filed       Now"
    for tx in txs:
      charPos = 0
      text += "\n"
      text += tx["Ticker"]
      charPos += len(tx["Ticker"])
      text += self.moveToPos(charPos, bought)
      charPos = bought

      text += str(tx["BuyPrice"])
      charPos += len(str(tx["BuyPrice"]))
      text += self.moveToPos(charPos, filed)
      charPos = filed

      text += str(tx["FilePrice"])
      charPos += len(str(tx["FilePrice"]))
      text += self.moveToPos(charPos, now)
      charPos = now

      text += str(tx["MonitorPrice"])
    return text

  def formatDetails(self, txs):
    roi30, ytd, industry = 9, 18, 28
    text = "Ticker    30DC      YTD        Industry"
    for tx in txs:
      charPos = 0
      text += "\n"
      text += tx["Ticker"]
      charPos += len(tx["Ticker"])
      text += self.moveToPos(charPos, roi30)
      charPos = roi30

      text += str(tx["30DC"])
      charPos += len(str(tx["30DC"]))
      text += self.moveToPos(charPos, ytd)
      charPos = ytd

      text += str(tx["YTD"])
      charPos += len(str(tx["YTD"]))
      text += self.moveToPos(charPos, industry)
      charPos = industry

      text += tx["Sector"]
    return text
  
  def formatGovernance(self, committees):
    text = ""
    for committee in committees:
      text += f"\n- `{committee}`"
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

  def moveToPos(self, pos, to):
    text = ""
    while pos <= to:
      text += " "
      pos += 1
    return text