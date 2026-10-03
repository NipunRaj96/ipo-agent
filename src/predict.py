"""Score open mainboard IPOs from the latest logged snapshot with bucket probabilities.

Verdicts only appear on the bid-close day from 15:30 IST. Earlier the subscription multiple is not final,
and the model was trained on final multiples, so it would understate the outcome.
"""
from datetime import datetime, timedelta

import pandas as pd

from model import LABELS, ROOT, bucket_probs, fit, load

APPLY_AT, SKIP_BELOW = 0.90, 0.50
VERDICT_FROM_MINUTES = 15 * 60 + 30  # IST minutes after midnight

hist = load()
models = {"open": fit(hist, "gain_open_pct"), "close": fit(hist, "gain_close_pct")}

log = pd.read_csv(ROOT / "data/gmp_log.csv")
latest = log[log.scraped_at == log.scraped_at.max()]
live = latest[(latest.segment == "IPO") & (latest.status == "O")]
ist = datetime.fromisoformat(latest.scraped_at.max()) + timedelta(hours=5, minutes=30)
close_today = f"{ist.day}-{ist:%b}"
late = ist.hour * 60 + ist.minute >= VERDICT_FROM_MINUTES

print(f"snapshot {ist:%d-%b %H:%M} IST | trained on {len(hist)} IPOs | apply if P(not loss)>={APPLY_AT}, skip if <{SKIP_BELOW}")
fmt = lambda p: "  ".join(f"{l} {x:.0%}" for l, x in zip(LABELS, p))
for row in live.itertuples():
    print(f"\n{row.name} | sub {row.sub_x}x | GMP Rs{row.gmp_rs} | closes {row.close}, lists {row.listing}")
    if row.close != close_today:
        print("  TOO EARLY: bids still open, subscription not final")
        continue
    if not late:
        print("  WAIT: last bidding day, most bids arrive in the final hours. Verdict after 15:30 IST")
        continue
    sub = 0 if pd.isna(row.sub_x) else row.sub_x
    p_open, p_close = bucket_probs(models["open"], [sub])[0], bucket_probs(models["close"], [sub])[0]
    p_ok = 1 - p_open[0]
    verdict = "APPLY" if p_ok >= APPLY_AT else "SKIP" if p_ok < SKIP_BELOW else "ABSTAIN"
    print(f"  open gain : {fmt(p_open)}")
    print(f"  day-1 close: {fmt(p_close)}")
    print(f"  P(not loss at open) {p_ok:.0%} -> {verdict}")
    print("  Late bids can still raise the multiple, so treat SKIP/ABSTAIN as less certain than APPLY.")
