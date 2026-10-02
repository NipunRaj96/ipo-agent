# Phase 1: Dataset and baselines (feasibility gate)

## Rows
Mainboard IPOs 2021-2025 (~400). One row per IPO.

## Labels
- `gain_open_pct` = (listing open price / issue price - 1) * 100. Primary.
- `gain_close_pct` = same at day-1 close. Secondary.
- Derived: `win_open` (>0), `big_win_open` (>=10).

## Features (all stamped with capture time, all before bid close)
- Static: issue size, fresh vs OFS share, price band, sector, P/E vs listed peers, lead managers, revenue/profit growth.
- Dynamic: subscription by category (QIB, NII, retail) per day, GMP on day 1/2/3 and its trend.
- Market: Nifty 5/20-day return, India VIX, average listing gain of last 10 IPOs.

## Baselines
1. Always apply.
2. GMP-only threshold.
3. GMP + QIB multiple logistic regression.

## Gate
If the GMP-only baseline is about as good as the richer model, skip the heavy agent work and ship the simple version. If every baseline is near coin-flip, stop.

## Output
One CSV in `data/` plus a data dictionary. Raw scrapes kept untouched in `data/raw/`.
