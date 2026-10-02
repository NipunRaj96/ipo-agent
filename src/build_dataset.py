"""Parse saved InvestorGain mainboard tables (data/raw/ig_ipo_<year>.html) into data/ipos.csv."""
import io
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
NUM = re.compile(r"-?[\d,]+(?:\.\d+)?")


def first_num(s):
    m = NUM.search(str(s).replace("₹", ""))
    return float(m.group().replace(",", "")) if m else None


def pct_in_parens(s):
    m = re.search(r"\((-?[\d.]+)%\)", str(s))
    return float(m.group(1)) if m else None


def parse_year(path):
    t = pd.read_html(io.StringIO(path.read_text(encoding="utf-8")), attrs={"id": "reportTable"})[0]
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


def main():
    frames = [parse_year(p) for p in sorted((ROOT / "data/raw").glob("ig_ipo_*.html"))]
    df = pd.concat(frames, ignore_index=True)
    df["gmp_pct"] = df["gmp_rs"] / df["issue_price"] * 100
    df = df.sort_values("listing_date").reset_index(drop=True)
    df.to_csv(ROOT / "data/ipos.csv", index=False)
    print(df.shape)
    print(df.isna().sum())


if __name__ == "__main__":
    main()
