import requests
import json

class Error:
  def __init__(self):
    self.webhook = "https://discord.com/api/webhooks/1316932982417657989/O7QMv2k9dmf0PsfViAAw3jjJmX25_IYEHqrPCpcryniqigQC0bxsmBQA7h2Bc4qxobG4"
    self.header = { 'Content-Type': 'application/json' }
    self.template = {
      "content": None,
      "embeds": [
        {
          "title": "Monitor Error",
          "description": "",
          "color": 9114130,
          "thumbnail": {
            "url": "https://www.congress.gov/img/member/p000197_200.jpg"
          }
        }
      ],
      "attachments": []
    }

  def notify(self, e, id):
    data = self.template
    data["embeds"][0]["description"] = f"docID: `{id}`\n{e}"
    print(f"Caught new error {e}", flush=True)
    requests.request("POST", self.webhook, headers=self.header, data=json.dumps(data))