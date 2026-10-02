# Spec 1: Profit buckets, calibration check, day-1 close

Approved 2026-10-02. Spec and plan combined in this one file.

## Goal
Replace the win/lose-only model with bucket probabilities for two targets: gain at listing open and gain at day-1 close.

## Design
- Buckets (right-closed): `<=0%` (loss or flat), `0-10%`, `10-30%`, `30%+`. "Win" stays defined as gain > 0, so earlier numbers remain comparable.
- Model: multinomial logistic regression on log(1 + final subscription). One model per target. Alternatives rejected: gradient boosting plus separate calibrator (overkill for one feature, 357 rows), lookup table by subscription band (too coarse, kept only as an idea for sanity checks).
- Verdict unchanged: APPLY if P(not loss) >= 0.90, SKIP if < 0.50, otherwise ABSTAIN; TOO EARLY unless the bid close date is today.
- Calibration: no separate calibrator. The reliability table in the evaluation decides whether one is needed.

## Files
| File | Role |
|---|---|
| `src/model.py` | `load()`, `bucket()`, `fit()`, `bucket_probs()`. Shared by everything. Has a tiny self-check under `__main__`. |
| `src/evaluate.py` | Walk-forward test (train on years before Y, test on Y, for 2023-2025): multi-class Brier vs base-rate Brier, reliability table, apply-rule precision with Wilson interval. Replaces `src/baselines.py` (deleted). |
| `src/predict.py` | Prints bucket probabilities for open and day-1 close plus the verdict, for live open mainboard IPOs. |

## Tasks
1. Write `model.py`, run its self-check.
2. Write `evaluate.py`, run it, read the reliability table.
3. Update `predict.py`, run on the latest snapshot.
4. Delete `baselines.py`. Record results below.

## Known limits
- 30%+ bucket is thin in 2021-2022, so its probabilities are noisy.
- Day-1 close depends on crowd behaviour after listing and will calibrate worse than listing open.
- Final subscription is used as the feature, which is slightly optimistic if the decision is made before the last-hour bids.
- Bucket edges are a choice and easy to change in `model.py`.

## Results
Walk-forward, test years 2023-2025, n=253 (final subscription as the only feature).

- Multi-class Brier, listing open: model 0.633 vs base-rate 0.761. Day-1 close: 0.661 vs 0.769. Model beats the base rate on both.
- Apply rule P(not loss) >= 0.90: listing open 109 of 253 picks, precision 0.963 (95% CI 0.91-0.99). Day-1 close 115 picks, 0.957 (CI 0.90-0.98). The lower CI bound (~0.90-0.91) is the honest number.
- Reliability: confident calls hold up (P(loss) under 10% happens 4% of the time). Middle ranges are rough: P(loss) predicted 16% happened 36% of the time; 30%+ predicted at 69% happened 55%, so the top bucket is overconfident.
- Calibration decision: no separate calibrator yet. Samples per cell are 26-110, too small to fit one reliably. Revisit once the live logger and new IPOs add data.
- Day-1 close calibrates slightly worse in the middle buckets, as expected.
- `src/baselines.py` deleted, replaced by `src/evaluate.py`.
