"""Score recorded verdicts (data/verdicts.csv) against listing results (data/ipos.csv).

Writes data/scorecard.csv and prints a Telegram-HTML summary. For each IPO the verdict it could actually
have acted on (issued before bids closed) is used, else the latest one. Gain above 0% at open counts as a win.
"""
import html
from datetime import date
from pathlib import Path

import pandas as pd

from update_data import key

ROOT = Path(__file__).resolve().parent.parent
src = ROOT / "data/verdicts.csv"
if not src.exists():
    raise SystemExit(0)

v = pd.read_csv(src)
v["k"] = v["name"].map(key)
pick = v.sort_values(["actionable", "snapshot_utc"]).groupby("k").tail(1)  # actionable rows sort last

ipos = pd.read_csv(ROOT / "data/ipos.csv").dropna(subset=["gain_open_pct"])
ipos["k"] = ipos["name"].map(key)
cols = ["k", "listing_date", "gain_open_pct", "gain_close_pct"]
board = pick.merge(ipos[cols].drop_duplicates("k", keep="last"), on="k", how="left")
board["gain_open_pct"] = board["gain_open_pct"].astype(float)
board.drop(columns="k").sort_values("snapshot_utc").to_csv(ROOT / "data/scorecard.csv", index=False)

listed, waiting = board[board.gain_open_pct.notna()], board[board.gain_open_pct.isna()]
lines = [f"<b>Scorecard</b> · {date.today():%d %b %Y}", ""]
for verdict in ("APPLY", "ABSTAIN", "SKIP"):
    g = listed[listed.verdict == verdict]
    if g.empty:
        continue
    wins = int((g.gain_open_pct > 0).sum())
    lines.append(f"<b>{verdict}</b>: {len(g)} listed, {wins} gained, {len(g) - wins} lost or flat, "
                 f"median {g.gain_open_pct.median():+.1f}% at open")
if listed.empty:
    lines.append("No verdicts have listed yet.")
if len(waiting):
    lines += ["", "Waiting for listing: " + ", ".join(html.escape(n) for n in waiting.name)]
late = int((board.actionable == 0).sum())
if late:
    lines += ["", f"<i>{late} of {len(board)} verdicts were issued after bids closed, so they could not have been acted on.</i>"]
print("\n".join(lines))
