"""Send stdin as Telegram message(s). Needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.

Does nothing if either is unset or if the text has no IPO card or scorecard, so it is safe to run on every snapshot.
Long texts are split at blank lines, so HTML tags are never cut in half (Telegram rejects broken tags).
Usage: python3 src/predict.py | python3 src/notify.py
"""
import json
import os
import sys
import urllib.request

LIMIT = 4000  # Telegram's hard limit is 4096 characters


def split(text, limit=LIMIT):
    parts, cur = [], ""
    for para in text.split("\n\n"):
        cand = f"{cur}\n\n{para}" if cur else para
        if len(cand) <= limit:
            cur = cand
            continue
        if cur:
            parts.append(cur)
        cur = para[:limit]  # ponytail: a single paragraph over 4000 chars is cut; no message produces one
    return parts + ([cur] if cur else [])


def send(token, chat, text):
    body = {"chat_id": chat, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)


if __name__ == "__main__":
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    text = sys.stdin.read().strip()
    if not (token and chat and ("Subscription:" in text or "Scorecard" in text)):
        print("notify: skipped (missing secrets or nothing to report)")
        sys.exit(0)
    parts = split(text)
    for part in parts:
        send(token, chat, part)
    print(f"notify: sent {len(parts)} message(s)")
