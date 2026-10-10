"""Append one snapshot of InvestorGain's live tables (append-only):
- GMP table -> data/gmp_log.csv
- subscription by investor type, anchor flag, P/E -> data/sub_log.csv
"""
import io
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
GMP_URL = "https://www.investorgain.com/report/ipo-gmp-live/331/"
SUB_URL = "https://www.investorgain.com/report/ipo-subscription-live/333/"
UA = "Mozilla/5.0 (Macintosh) ipo-agent personal research"
GMP_NAME = re.compile(r"^(?P<name>.*?)\s+(?P<segment>IPO|BSE SME|NSE SME)(?P<status>[A-Z])$")
SUB_NAME = re.compile(r"^(?P<name>.*?)\s*(?P<segment>IPO|BSE SME|NSE SME)GMP:")
NUM = re.compile(r"-?[\d,]+(?:\.\d+)?")


def num(s, last=False):
    found = NUM.findall(str(s).replace("₹", ""))
    return float(found[-1 if last else 0].replace(",", "")) if found else None


def read_table(url):
    html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read().decode()
    t = pd.read_html(io.StringIO(html), attrs={"id": "reportTable"})[0].dropna(how="all")
    t.columns = [c.replace("▲▼", "").strip() for c in t.columns]
    return t


def fetch_gmp(ts):
    t = read_table(GMP_URL)
    parts = t["Name"].str.extract(GMP_NAME)
    pct = t["GMP"].str.extract(r"\((-?[\d.]+)%\)")[0].astype(float)
    return pd.DataFrame({
        "scraped_at": ts,
        "name": parts["name"], "segment": parts["segment"], "status": parts["status"],
        "gmp_rs": t["GMP"].map(num), "gmp_pct": pct,
        "sub_x": t["Sub"].map(num), "price": t["Price (₹)"].map(lambda s: num(s, last=True)),
        "size_cr": t["IPO Size"].map(num), "lot": t["Lot"].map(num),
        "open": t["Open"].str.split(" GMP").str[0], "close": t["Close"].str.split(" GMP").str[0], "listing": t["Listing"],
        "gmp_updated_on": t["Updated-On"],
    }).dropna(subset=["name"])


def fetch_subscription(ts):
    t = read_table(SUB_URL)
    parts = t["Name"].str.extract(SUB_NAME)
    total = t["Total"].astype(str).str.extract(r"^\s*(?P<total_x>[\d.]+)\s*(?P<sub_updated>.*)$")
    return pd.DataFrame({
        "scraped_at": ts,
        "name": parts["name"], "segment": parts["segment"],
        "total_x": total["total_x"].astype(float), "sub_updated": total["sub_updated"],
        "qib_x": t["QIB"].map(num), "shni_x": t["SHNI"].map(num), "bhni_x": t["BHNI"].map(num),
        "nii_x": t["NII"].map(num), "rii_x": t["RII"].map(num),
        "anchor": t["Anchor"].map({"✅": 1, "❌": 0}),
        "size_cr": t["IPO Size"].map(num), "price": t["IPO Price"].map(num), "pe": t["P/E"].map(num),
        "close_date": t["Closing Date"],
    }).dropna(subset=["name"])


def append(df, name):
    out = ROOT / "data" / name
    df.to_csv(out, mode="a", header=not out.exists(), index=False)


def main():
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    gmp, sub = fetch_gmp(ts), fetch_subscription(ts)
    if gmp.empty or sub.empty:
        raise SystemExit("snapshot is empty: the site layout may have changed")
    append(gmp, "gmp_log.csv")
    append(sub, "sub_log.csv")
    live = gmp[(gmp.segment == "IPO") & (gmp.status.isin(["O", "U"]))]
    print(f"logged {len(gmp)} GMP rows, {len(sub)} subscription rows, {len(live)} mainboard open/upcoming")
    print(live[["name", "status", "gmp_rs", "gmp_pct", "sub_x", "price", "open", "close", "listing"]].to_string(index=False))
    main_sub = sub[sub.segment == "IPO"]
    print(main_sub[["name", "total_x", "qib_x", "nii_x", "rii_x", "anchor", "pe", "close_date"]].to_string(index=False))


if __name__ == "__main__":
    main()
