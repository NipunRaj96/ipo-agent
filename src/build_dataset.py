"""Parse saved InvestorGain mainboard tables (data/raw/ig_ipo_<year>.html) into data/ipos.csv.

python3 src/build_dataset.py --fetch   downloads the yearly tables first (2021 to this year, a few seconds apart).
"""
import io
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
NUM = re.compile(r"-?[\d,]+(?:\.\d+)?")
URL = "https://www.investorgain.com/report/ipo-gmp-performance-tracker/377/ipo/?year={}"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) ipo-agent personal research"}


def first_num(s):
    m = NUM.search(str(s).replace("₹", ""))
    return float(m.group().replace(",", "")) if m else None


def pct_in_parens(s):
    m = re.search(r"\((-?[\d.]+)%\)", str(s))
    return float(m.group(1)) if m else None


def parse_year(path):
    return parse_html(path.read_text(encoding="utf-8"))


def parse_html(html):
    t = pd.read_html(io.StringIO(html), attrs={"id": "reportTable"})[0]
    t.columns = [c.replace("▲▼", "").strip() for c in t.columns]
    t = t.dropna(subset=["IPO"]).reset_index(drop=True)
    return pd.DataFrame({
        "name": t["IPO"],
        "listing_date": pd.to_datetime(t["Listing Dt"], format="%d-%b-%y", errors="coerce"),
        "size_cr": t["Size"].map(first_num),
        "sub_x": t["Sub"].map(first_num),
        "gmp_rs": t["GMP"].map(first_num),
        "issue_price": t["Price"].map(first_num),
        "gain_open_pct": t["Listing Price"].map(pct_in_parens),
        "gain_close_pct": t["Listing Day Close"].map(pct_in_parens),
    })


def fetch(years):
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    for year in years:
        req = urllib.request.Request(URL.format(year), headers=UA)
        (raw / f"ig_ipo_{year}.html").write_bytes(urllib.request.urlopen(req, timeout=60).read())
        print("fetched", year)
        time.sleep(3)


def main():
    if "--fetch" in sys.argv:
        fetch(range(2021, date.today().year + 1))
    frames = [parse_year(p) for p in sorted((ROOT / "data/raw").glob("ig_ipo_*.html"))]
    df = pd.concat(frames, ignore_index=True)
    df["gmp_pct"] = df["gmp_rs"] / df["issue_price"] * 100
    df = df.sort_values("listing_date").reset_index(drop=True)
    df.to_csv(ROOT / "data/ipos.csv", index=False)
    print(df.shape)
    print(df.isna().sum())


if __name__ == "__main__":
    main()
