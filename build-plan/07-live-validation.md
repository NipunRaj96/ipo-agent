# Live validation (gate before GitHub Actions or any automation)

Nothing is automated or pushed until one live IPO passes this check, with a human comparing against Groww.

## Test IPOs
Nityas Gems & Jewellery and Vishal Nirmiti: bids close Mon 5-Oct-2026, list Thu 8-Oct-2026.

## Steps
1. Fri 2-Oct to Mon 5-Oct: run `python3 src/log_gmp.py` by hand a few times per day (more on 5-Oct, especially after 3 PM).
2. Mon 5-Oct, last hour before close: run `python3 src/log_gmp.py && python3 src/predict.py`.
3. Compare with Groww at the same time:
   - Subscription multiple (total, plus QIB / NII / retail) matches what we logged?
   - GMP on Groww-linked sources roughly matches the logged GMP?
   - Prices, lot size, close and listing dates match?
4. Thu 8-Oct, after listing: record actual open price and day-1 close. Compare to the verdict.

## Pass criteria
- Logged numbers match Groww within rounding / update delay.
- predict.py outputs a verdict only when subscription is final (close day), otherwise TOO EARLY.
- Actual outcome is consistent with the verdict (a single IPO cannot prove accuracy; this only proves the pipeline is wired correctly).

## After passing
Decide scheduling (GitHub Actions, only then), then add category-wise subscription (QIB / NII / retail) and the agent layer.
