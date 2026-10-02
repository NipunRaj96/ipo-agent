"""Append one snapshot of InvestorGain's live GMP table to data/gmp_log.csv (append-only)."""
import io
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
URL = "https://www.investorgain.com/report/ipo-gmp-live/331/"
UA = "Mozilla/5.0 (Macintosh) ipo-agent personal research"
NAME = re.compile(r"^(?P<name>.*?)\s+(?P<segment>IPO|BSE SME|NSE SME)(?P<status>[A-Z])$")
NUM = re.compile(r"-?[\d,]+(?:\.\d+)?")


def num(s, last=False):
    found = NUM.findall(str(s).replace("₹", ""))
    return float(found[-1 if last else 0].replace(",", "")) if found else None


def fetch_snapshot():
    html = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": UA}), timeout=30).read().decode()
    t = pd.read_html(io.StringIO(html), attrs={"id": "reportTable"})[0].dropna(how="all")
    t.columns = [c.replace("▲▼", "").strip() for c in t.columns]
    parts = t["Name"].str.extract(NAME)
    pct = t["GMP"].str.extract(r"\((-?[\d.]+)%\)")[0].astype(float)
    return pd.DataFrame({
        "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "name": parts["name"], "segment": parts["segment"], "status": parts["status"],
        "gmp_rs": t["GMP"].map(num), "gmp_pct": pct,
        "sub_x": t["Sub"].map(num), "price": t["Price (₹)"].map(lambda s: num(s, last=True)),
        "size_cr": t["IPO Size"].map(num), "lot": t["Lot"].map(num),
        "open": t["Open"].str.split(" GMP").str[0], "close": t["Close"], "listing": t["Listing"],
        "gmp_updated_on": t["Updated-On"],
    }).dropna(subset=["name"])


def main():
    df = fetch_snapshot()
    out = ROOT / "data/gmp_log.csv"
    df.to_csv(out, mode="a", header=not out.exists(), index=False)
    live = df[(df.segment == "IPO") & (df.status.isin(["O", "U"]))]
    print(f"logged {len(df)} rows, {len(live)} mainboard open/upcoming")
    print(live[["name", "status", "gmp_rs", "gmp_pct", "sub_x", "price", "open", "close", "listing"]].to_string(index=False))


if __name__ == "__main__":
    main()
