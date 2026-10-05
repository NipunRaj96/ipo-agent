"""Score mainboard IPOs from the latest logged snapshot with bucket probabilities.

Subscription comes from sub_log.csv, which keeps an IPO listed after bids close, unlike the GMP table.
Verdicts only appear on the bid-close day from 15:30 IST (including after close, when numbers are final).
Earlier the subscription multiple is not final and the model was trained on final multiples.
"""
from datetime import datetime, timedelta

import pandas as pd

from model import LABELS, ROOT, bucket_probs, fit, load

APPLY_AT, SKIP_BELOW = 0.90, 0.50
VERDICT_FROM_MINUTES = 15 * 60 + 30  # IST minutes after midnight
CLOSE_MINUTES = 17 * 60  # bidding closes 17:00 IST
EARLY_STATUS_HOUR = 11  # early "too early" notes only in this IST hour, to keep alerts quiet

hist = load()
models = {"open": fit(hist, "gain_open_pct"), "close": fit(hist, "gain_close_pct")}

sub_log = pd.read_csv(ROOT / "data/sub_log.csv")
snap = sub_log.scraped_at.max()
live = sub_log[(sub_log.scraped_at == snap) & (sub_log.segment == "IPO")]
gmp_log = pd.read_csv(ROOT / "data/gmp_log.csv")
gmp = gmp_log.sort_values("scraped_at").dropna(subset=["gmp_rs"]).groupby("name").gmp_rs.last().to_dict()  # last seen: closed IPOs leave the GMP table

ist = datetime.fromisoformat(snap) + timedelta(hours=5, minutes=30)
minutes = ist.hour * 60 + ist.minute
fmt = lambda p: "  ".join(f"{l} {x:.0%}" for l, x in zip(LABELS, p))

print(f"snapshot {ist:%d-%b %H:%M} IST | trained on {len(hist)} IPOs | apply if P(not loss)>={APPLY_AT}, skip if <{SKIP_BELOW}")
for row in live.itertuples():
    close = datetime.strptime(row.close_date, "%d-%m-%Y").date()
    head = (f"\n{row.name} | sub {row.total_x}x (QIB {row.qib_x}x, retail {row.rii_x}x) | "
            f"GMP Rs{gmp.get(row.name, 'n/a')} | bids close {close:%d-%b}")
    if close > ist.date():
        if ist.hour == EARLY_STATUS_HOUR:
            print(head + "\n  TOO EARLY: bids still open, subscription not final")
        continue
    if close < ist.date():
        continue
    if minutes < VERDICT_FROM_MINUTES:
        print(head + "\n  WAIT: last bidding day, most bids arrive in the final hours. Verdict after 15:30 IST")
        continue
    sub = 0 if pd.isna(row.total_x) else row.total_x
    p_open, p_close = bucket_probs(models["open"], [sub])[0], bucket_probs(models["close"], [sub])[0]
    p_ok = 1 - p_open[0]
    verdict = "APPLY" if p_ok >= APPLY_AT else "SKIP" if p_ok < SKIP_BELOW else "ABSTAIN"
    print(head)
    print(f"  open gain : {fmt(p_open)}")
    print(f"  day-1 close: {fmt(p_close)}")
    print(f"  P(not loss at open) {p_ok:.0%} -> {verdict}")
    if minutes >= CLOSE_MINUTES:
        print("  Bids have closed: final numbers. Compare with the listing result.")
    else:
        print("  Late bids can still raise the multiple, so treat SKIP/ABSTAIN as less certain than APPLY.")
