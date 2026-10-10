"""Build the IPO check message from the latest logged snapshot. Output is Telegram HTML (bold, monospace).

Terminal view without tags: python3 src/predict.py | sed 's/<[^>]*>//g'

Subscription comes from sub_log.csv, which keeps an IPO listed after bids close, unlike the GMP table.
Verdicts only appear on the bid-close day from 15:30 IST (including after close, when numbers are final).
Earlier the subscription multiple is not final and the model was trained on final multiples.
"""
import html
from datetime import datetime, timedelta

import pandas as pd

from model import ROOT, bucket_probs, fit, load

APPLY_AT, SKIP_BELOW = 0.90, 0.50
VERDICT_FROM_MINUTES = 15 * 60 + 30  # IST minutes after midnight
CLOSE_MINUTES = 17 * 60  # bidding closes 17:00 IST
EARLY_STATUS_HOUR = 11  # early "too early" notes only in this IST hour, to keep alerts quiet
ROWS = ["Loss or flat", "Gain 0-10%", "Gain 10-30%", "Gain over 30%"]
RULE = "\n\n" + "─" * 16 + "\n\n"

hist = load()
models = {"open": fit(hist, "gain_open_pct"), "close": fit(hist, "gain_close_pct")}

sub_log = pd.read_csv(ROOT / "data/sub_log.csv")
snap = sub_log.scraped_at.max()
live = sub_log[(sub_log.scraped_at == snap) & (sub_log.segment == "IPO")]
gmp_log = pd.read_csv(ROOT / "data/gmp_log.csv")
gmp = gmp_log.sort_values("scraped_at").dropna(subset=["gmp_rs"]).groupby("name").gmp_rs.last().to_dict()  # last seen: closed IPOs leave the GMP table

ist = datetime.fromisoformat(snap) + timedelta(hours=5, minutes=30)
minutes = ist.hour * 60 + ist.minute


def card(row, close, status_lines):
    g = gmp.get(row.name)
    return "\n".join([
        f"<b>{html.escape(row.name)}</b>",
        f"Bids close {close:%d %b}",
        f"Subscription: {row.total_x}x (institutions {row.qib_x}x, retail {row.rii_x}x)",
        f"Grey market premium: {'Rs ' + format(g, 'g') if g is not None else 'not available'}",
        "",
        *status_lines,
    ])


def bars(p):
    cells = (f"{label:<15}{'█' * round(x * 10)}{'░' * (10 - round(x * 10))} {x:>4.0%}" for label, x in zip(ROWS, p))
    return "<pre>" + "\n".join(cells) + "</pre>"


blocks, verdict_shown = [], False
for row in live.itertuples():
    close = datetime.strptime(row.close_date, "%d-%m-%Y").date()
    if close < ist.date():
        continue
    if close > ist.date():
        if ist.hour == EARLY_STATUS_HOUR:
            blocks.append(card(row, close, ["<b>Status: too early.</b> Bidding is still open and the numbers are not final."]))
        continue
    if minutes < VERDICT_FROM_MINUTES:
        blocks.append(card(row, close, ["<b>Status: wait.</b> Last bidding day. Most bids arrive in the final hours. Verdict after 3:30 PM IST."]))
        continue
    sub = 0 if pd.isna(row.total_x) else row.total_x
    p_open, p_close = bucket_probs(models["open"], [sub])[0], bucket_probs(models["close"], [sub])[0]
    p_ok = 1 - p_open[0]
    verdict = "APPLY" if p_ok >= APPLY_AT else "SKIP" if p_ok < SKIP_BELOW else "ABSTAIN"
    note = ("Bids have closed. These are the final numbers." if minutes >= CLOSE_MINUTES
            else "Late bids can still raise the subscription, so SKIP and ABSTAIN are less certain than APPLY.")
    day1 = ", ".join(f"{label.lower().replace('gain ', '')} {x:.0%}" for label, x in zip(ROWS, p_close))
    blocks.append(card(row, close, [
        f"<b>Verdict: {verdict}</b> ({p_ok:.0%} chance of no loss at listing)",
        "",
        "<b>Listing price vs issue price</b>",
        bars(p_open),
        f"<b>End of day 1:</b> {day1}",
        "",
        f"<i>{note}</i>",
    ]))
    verdict_shown = True

if blocks:
    head = f"<b>IPO check</b> · {ist:%d %b, %H:%M} IST"
    foot = f"<i>Based on {len(hist)} past IPOs (2021-2026). Personal research, not financial advice.</i>"
    legend = "<i>APPLY: very likely not to lose. SKIP: a loss is more likely than not. ABSTAIN: unclear.</i>\n" if verdict_shown else ""
    print(head + RULE + RULE.join(blocks) + RULE + legend + foot)
