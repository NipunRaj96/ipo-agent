# Phase 2: Model and calibration

- Models: logistic regression first, small gradient boosting second. Small data, so simple wins unless proven otherwise.
- Split: walk-forward by time (train on earlier IPOs, test on later). Never random split.
- Calibration: isotonic or Platt via cross-validation. Evaluate with Brier score and reliability curve.
- Magnitude: quantile outputs (10/50/90%), not a single point estimate.
- Abstain rule: publish a "precision vs share of IPOs covered" curve. Pick the threshold from it. Report Wilson confidence intervals because n is small.
- Expected value: `P(allotment) * expected gain * lot value`. Allotment odds come from the retail subscription multiple (retail oversubscribed means a lottery).
- Day-1 close gets its own model and its own metrics.
