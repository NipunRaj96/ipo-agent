"""Extract structured facts from a saved prospectus text with Gemini (free tier). Facts only, no predictions.

Usage: python3 src/extract.py moneyview a-one ...
Needs GEMINI_API_KEY in the environment or in a .env file at the project root.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def num(desc):
    return {"type": "NUMBER", "nullable": True, "description": desc}


FIELDS = {
    "ofs_pct": num("Offer for sale as % of total issue size"),
    "revenue_growth_pct": num("Revenue growth, latest fiscal year vs previous, %"),
    "pat_margin_pct": num("PAT divided by revenue, latest fiscal year, %"),
    "pat_growth_pct": num("PAT growth, latest fiscal year vs previous, %. Null if either year is a loss"),
    "ronw_pct": num("Return on net worth, latest fiscal year, %"),
    "debt_to_equity": num("Debt to equity ratio, latest fiscal year"),
    "promoter_holding_pre_pct": num("Promoter and promoter group holding before the issue, %"),
    "debt_repayment_pct_of_proceeds": num("Share of fresh issue proceeds used to repay borrowings, %"),
    "outstanding_litigation_count": num("Total count of outstanding legal proceedings involving company, promoters, directors, subsidiaries"),
}
SCHEMA = {
    "type": "OBJECT",
    "properties": {**FIELDS, "red_flags": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Up to 5 short, factual risks stated in the document"}},
    "required": list(FIELDS) + ["red_flags"],
}
PROMPT = (
    "Extract the requested fields from the IPO abridged prospectus below. Use only the document text. "
    "Do not use outside knowledge. Do not predict listing performance or give advice. "
    "If a value is not stated or cannot be computed from stated numbers, return null. "
    "Only ratios and percentages are requested, so units (lakhs, million, crore) do not matter."
)


def api_key():
    k = os.environ.get("GEMINI_API_KEY", "")
    env = ROOT / ".env"
    if not k and env.exists():
        k = next((l.split("=", 1)[1].strip() for l in env.read_text().splitlines() if l.startswith("GEMINI_API_KEY=")), "")
    if not k:
        sys.exit("Set GEMINI_API_KEY in the environment or in .env")
    return k


def extract(text):
    body = {
        "contents": [{"parts": [{"text": f"{PROMPT}\n\nDOCUMENT:\n{text}"}]}],
        "generationConfig": {"temperature": 0, "responseMimeType": "application/json", "responseSchema": SCHEMA},
    }
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": api_key()})
    for attempt in range(4):
        try:
            reply = json.load(urllib.request.urlopen(req, timeout=180))
            return json.loads(reply["candidates"][0]["content"]["parts"][0]["text"])
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 503) or attempt == 3:
                raise
            time.sleep(15 * (attempt + 1))


if __name__ == "__main__":
    out = ROOT / "data/llm"
    out.mkdir(parents=True, exist_ok=True)
    for key in sys.argv[1:]:
        features = extract((ROOT / f"data/prospectus/{key}.txt").read_text())
        (out / f"{key}.json").write_text(json.dumps({"model": MODEL, "features": features}, indent=2))
        print(key, json.dumps(features, ensure_ascii=False))
