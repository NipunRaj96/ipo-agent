# Phase 3: Live logger

Historical GMP is patchy, so clean forward data is the long-term asset. Start this as soon as sources are confirmed, in parallel with phase 1.

- Scheduled job (local cron or GitHub Actions) snapshots every open IPO: GMP, subscription by category, timestamp.
- Append-only storage (CSV or SQLite). Never overwrite.
- After listing, fill in the labels automatically.
- Frequency: a few times per day while an IPO is open, more often on day 3.

## Manual mode (current)
No cron or GitHub Actions until the live Groww validation passes. Snapshots are taken by hand:

    python3 src/log_gmp.py

Run once each morning (about 10 AM IST) while any mainboard IPO is open, and several times on the last bid day, especially after 3 PM IST. Each run appends every open/upcoming IPO to `data/gmp_log.csv` with a timestamp, so the GMP trend across bidding days builds up on its own. Rows are never overwritten.

Goal: about 40+ mainboard IPOs with GMP at bid close plus final outcome, then test whether GMP trend improves on the subscription-only model (walk-forward Brier score).
