# Data sources (scouted 2026-10-02)

Findings from page reads and searches. Items marked "unverified" must be confirmed before building on them.

## Base rate (important for baselines)
2024 mainboard: 82.6% listed at open in profit (76 of 92 listings counted by Chittorgarh), average listing gain 28.2%, day-1 close profitable 79.3%. So "always apply" is already ~80% accurate in a hot year. The model has to beat that: its value is identifying the ~17-20% that list at a loss, not predicting winners. Check other years (2021-2023, 2025) before trusting this rate.

## Per-source notes

| Source | Gives | Gaps / caveats |
|---|---|---|
| Chittorgarh (chittorgarh.com) | Issue price, listing price, gains, subscription by category (QIB/NII/retail), lead manager performance. Year filter back to 2004 and an Export button on report pages. | GMP is live only, no history seen. robots.txt blocks AI crawlers (GPTBot, ChatGPT-User) and data-collection tools. Use the Export button manually rather than a scraper. Check ToS. |
| InvestorGain (investorgain.com) GMP performance tracker | Per-year table (239 rows for 2023, mainboard + SME, filterable): size, subscription multiple, final GMP, issue price, estimated price at GMP, listing price, day-1 close, LTP. | Final GMP only, not the day 1/2/3 trajectory. No export button seen. Pagination only. |
| Trendlyne IPO screener | Mainboard IPOs by year with performance. | Columns not checked yet. |
| NSE / BSE bid details | Category-wise subscription during the issue. Updated a few times per day (reported by search results, unverified). | No documented API. Endpoint must be found via browser network tab. Terms of use unchecked. |
| Apify "India IPO Tracker" | Prebuilt scraper for GMP, subscription, listing. | Third party, may be paid. Skipped. |

## Implications for the plan
- Phase 1 uses final GMP (last value before listing), not a daily trajectory. Trajectory features only come from the live logger (phase 3).
- Listing price, day-1 close and subscription history can be had from Chittorgarh/InvestorGain for 2021-2025. Enough for baselines.
- Day-1 close label exists (InvestorGain "Listing Day Close").
- Collection method: manual export or copy of year tables first, scripts only where terms allow. Keep raw files untouched in `data/raw/`.

## Open questions
- Is final GMP the day-3 value or the value on listing eve? Matters for leakage. Check how InvestorGain defines it.
- NSE bid-details endpoint and its terms.
- Market features (Nifty, VIX): free via NSE historical files or yfinance (unverified).
