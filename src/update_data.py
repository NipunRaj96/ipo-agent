"""Weekly data refresh.

1. Re-reads this year's InvestorGain tracker and replaces this year's rows in data/ipos.csv, so newly
   listed IPOs and their results flow into the training history.
2. Joins the live logs with those results into data/live_dataset.csv: one row per logged IPO that has
   listed, with the final investor-type subscription, P/E, and the GMP seen last while bids were open.
"""
import re
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd

from build_dataset import parse_html

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
URL = "https://www.investorgain.com/report/ipo-gmp-performance-tracker/377/ipo/?year={}"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) ipo-agent personal research"}


def key(name):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(limited|ltd|ipo)\b", "", str(name).lower()))


def refresh_outcomes():
    year = datetime.now().year
    html = urllib.request.urlopen(urllib.request.Request(URL.format(year), headers=UA), timeout=60).read().decode()
    new = parse_html(html).dropna(subset=["listing_date"])
    new["gmp_pct"] = new.gmp_rs / new.issue_price * 100
    old = pd.read_csv(DATA / "ipos.csv", parse_dates=["listing_date"]).dropna(subset=["listing_date"])
    out = pd.concat([old[old.listing_date.dt.year != year], new]).sort_values("listing_date")
    out.to_csv(DATA / "ipos.csv", index=False)
    print(f"ipos.csv: {len(old)} -> {len(out)} rows ({len(new)} for {year})")


def build_live_dataset():
    sub = pd.read_csv(DATA / "sub_log.csv").query("segment == 'IPO'").copy()
    gmp = pd.read_csv(DATA / "gmp_log.csv").query("segment == 'IPO'").copy()
    ipos = pd.read_csv(DATA / "ipos.csv").dropna(subset=["gain_open_pct", "gain_close_pct"]).copy()
    for df in (sub, gmp, ipos):
        df["k"] = df["name"].map(key)
    final = sub.sort_values("scraped_at").groupby("k").tail(1)
    last_open = gmp[gmp.status == "O"].sort_values("scraped_at").groupby("k").tail(1)
    last_open = last_open[["k", "gmp_pct"]].rename(columns={"gmp_pct": "gmp_pct_last_open"})
    out = (final[["k", "name", "total_x", "qib_x", "shni_x", "bhni_x", "nii_x", "rii_x", "anchor", "pe"]]
           .merge(last_open, on="k", how="left")
           .merge(ipos[["k", "listing_date", "issue_price", "gain_open_pct", "gain_close_pct"]], on="k"))
    out.drop(columns="k").to_csv(DATA / "live_dataset.csv", index=False)
    print(f"live_dataset.csv: {len(out)} listed IPOs with logged data (of {final.k.nunique()} logged mainboard IPOs)")
    waiting = sorted(set(final.name) - set(out.name))
    if waiting:
        print("logged but no result yet (not listed, or name differs between tables):", waiting)


if __name__ == "__main__":
    refresh_outcomes()
    build_live_dataset()
