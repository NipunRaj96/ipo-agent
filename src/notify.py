"""Send stdin as a Telegram message. Needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.

Does nothing if either is unset or if the text has no IPO verdict, so it is safe to run on every snapshot.
Usage: python3 src/predict.py | python3 src/notify.py
"""
import json
import os
import sys
import urllib.request

token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
text = sys.stdin.read().strip()
if not (token and chat and ("Subscription:" in text or "Scorecard" in text)):
    print("notify: skipped (missing secrets or no open mainboard IPO)")
    sys.exit(0)
req = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    json.dumps({"chat_id": chat, "text": text[:4000], "parse_mode": "HTML", "disable_web_page_preview": True}).encode(),
    {"Content-Type": "application/json"},
)
urllib.request.urlopen(req, timeout=30)
print("notify: sent")
