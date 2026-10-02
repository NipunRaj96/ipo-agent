# Overview

## Goal
For a given open mainboard IPO, output: apply / skip / abstain, P(listing gain > 0), P(gain >= 10%), a 10/50/90% gain range, and expected value including allotment odds.

## Principles
- Model produces the probability. The LLM only reads documents and explains. It never overrides the number.
- Calibration beats accuracy. Judge by Brier score and reliability curves.
- Abstaining is allowed and encouraged. Precision on "apply" calls is traded against coverage.
- No leakage: every feature is timestamped and must exist before bid close.
- Everything free: Python, pandas, scikit-learn, free LLM tiers, cron/GitHub Actions.

## Decisions
- Scope: mainboard IPOs only (2021-2025 for history). SME later, separate model.
- Language/stack: Python.
- Use: personal. Public advice would need SEBI RIA registration.
- Targets: listing open price gain (primary). Day-1 close gain (secondary). Day-1 close depends on crowd behaviour after listing, so expect weaker calibration there; report it separately and do not mix it into the apply decision until proven.
- 99% precision is not a goal. Realistic goal: well-calibrated probabilities and a high-precision "apply" subset with honest confidence intervals.

## Phases
1. [Dataset and baselines](01-dataset-and-baselines.md) - feasibility gate
2. [Model and calibration](02-model-and-calibration.md)
3. [Live logger](03-live-logger.md) - start as early as possible
4. [Agent layer](04-agent-layer.md) - parked, see [spec-2](implementation-plan/spec-2/README.md)
5. [Live mode](05-live-mode.md)

Data sources and access findings: [data-sources.md](data-sources.md)

## Risks
Sparse historical GMP, small sample (~100 IPOs/year), regime change (2021 boom vs later), scraping terms of service, GMP manipulation (only weakly detectable).
