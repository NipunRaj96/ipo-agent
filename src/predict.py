"""Score open mainboard IPOs from the latest logged snapshot with bucket probabilities."""
from datetime import date

import numpy as np
import pandas as pd

from model import LABELS, ROOT, bucket_probs, fit, load

APPLY_AT, SKIP_BELOW = 0.90, 0.50

hist = load()
models = {"open": fit(hist, "gain_open_pct"), "close": fit(hist, "gain_close_pct")}

log = pd.read_csv(ROOT / "data/gmp_log.csv")
latest = log[log.scraped_at == log.scraped_at.max()]
live = latest[(latest.segment == "IPO") & (latest.status == "O")].copy()
today = date.today()
final_sub = (live.close == f"{today.day}-{today:%b}").to_numpy()

print(f"snapshot {latest.scraped_at.max()} | {len(hist)} training IPOs | apply if P(not loss)>={APPLY_AT}, skip if <{SKIP_BELOW}")
for i, row in enumerate(live.itertuples()):
    sub = 0 if pd.isna(row.sub_x) else row.sub_x
    p_open = bucket_probs(models["open"], [sub])[0]
    p_close = bucket_probs(models["close"], [sub])[0]
    p_ok = 1 - p_open[0]
    verdict = ("TOO EARLY" if not final_sub[i] else "APPLY" if p_ok >= APPLY_AT else "SKIP" if p_ok < SKIP_BELOW else "ABSTAIN")
    fmt = lambda p: "  ".join(f"{l} {x:.0%}" for l, x in zip(LABELS, p))
    print(f"\n{row.name} | sub {row.sub_x}x | GMP Rs{row.gmp_rs} | closes {row.close}, lists {row.listing}")
    print(f"  open gain : {fmt(p_open)}")
    print(f"  day-1 close: {fmt(p_close)}")
    print(f"  P(not loss at open) {p_ok:.0%} -> {verdict}")
print("\nTOO EARLY = subscription not final (model trained on final subscription), numbers above are not valid.")
