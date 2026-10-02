# Phase 1 first results (2026-10-02)

Data: InvestorGain mainboard tables 2021-2025, saved raw in `data/raw/`, parsed by `src/build_dataset.py` into `data/ipos.csv` (357 usable rows of 378; 21 rows missing values were dropped). Baselines: `src/baselines.py`. Train 2021-2023 (164), test 2024-2025 (193).

Access notes: InvestorGain robots.txt allows general crawling (blocks only CCBot, Bytespider). Chittorgarh robots.txt blocks AI crawlers and data tools, so it is not scraped. Trendlyne allows /ipo/ with a 1s delay (10s for GPTBot/ClaudeBot), unused so far.

## Test results (target: gain at listing open > 0)
- Base rate: 72% of 2024-2025 IPOs won at open (75% in train). "Always apply" precision 0.72.
- GMP% > 0: precision 0.82 on 159 applies. GMP% > 10: 0.94 on 102. GMP% > 20: 1.00 on 65 (95% CI 0.94-1.00).
- Subscription >= 50x: 0.95 on 83.
- Logistic (GMP% + log subscription): AUC 0.874, Brier 0.133 vs 0.202 for always-base-rate. P(win) >= 0.9: 1.00 on 69 (CI 0.95-1.00).
- GMP alone gives AUC 0.876, so subscription adds nothing on top in this sample.

## Caveats (do not skip)
1. The GMP column is probably the last GMP before listing, not the GMP at bid close. If so, these numbers are optimistic because the decision must be made earlier. Phase 3 live logger exists to fix this.
2. Missing GMP may be recorded as 0, which can look like "GMP says no gain".
3. Small samples: 65-100 applies, so the lower CI bound (0.94-0.95) is the honest figure, not 1.00.
4. Win is defined as any gain > 0 at open, including +0.5%. A "meaningful win" (>= 5%) target is stricter.
5. Single split, no tuning, no calibration yet.

## Next
- Pin down what InvestorGain's GMP timestamp is (compare against GMP on bid-close day for a few recent IPOs).
- Add market features, Nifty trend and recent-listing average.
- Start the live logger.

## Update: GMP timestamp check (same day)
Caveat 1 is confirmed. For Urban Co. (bids closed 12-Sep-2025, listed 17-Sep) and Shringar House of Mangalsutra (same dates), the tracker GMP equals the last GMP-history entry, stamped listing morning 9:37 AM, five days after bids closed. So every GMP result above leaks information the decision cannot have. GMP history per IPO is capped at 3 rows on InvestorGain (full history is paid), and Wayback Machine snapshots are too sparse to backfill.

## Leak-free results (no GMP; test 2024-2025)
Features: final subscription multiple (known at close, slightly optimistic if the decision is made earlier), issue size, average gain of the previous 10 listings.
- Subscription only: AUC 0.817, Brier 0.159. P(win) >= 0.90 gives precision 0.952 on 84 applies (95% CI 0.88-0.98).
- Adding issue size or recent-listing average does not help (AUC 0.815 and 0.810).
- Market-index features (Nifty) deprioritised: the recent-listing feature already failed to add signal.

## Live logger
`src/log_gmp.py` appends a snapshot of InvestorGain's live GMP table (all open/upcoming IPOs, mainboard and SME) to `data/gmp_log.csv`. Tested once on 2026-10-02: 23 rows, two mainboard IPOs open (Nityas Gems and Jewellery, Vishal Nirmiti, both close 5-Oct, list 8-Oct). Scheduling not set up yet.
