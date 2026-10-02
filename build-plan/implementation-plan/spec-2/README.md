# Spec 2: LLM layer (prospectus fact extraction)

Status: PARKED on 2026-10-02. Pilot extraction ran on 4 IPOs and works for ratios. Backfill of ~250 IPOs is not being done.

Why parked: GMP (the market's own forecast) already prices in what the prospectus says, and in the pilot subscription explained outcomes better than any extracted ratio. The simpler plan is subscription (done) plus bid-close GMP and its trend from the live logger. Revive only if the GMP-based model plateaus, and then likely as an explanation writer rather than a feature source.

## Idea you proposed, and how it is applied
Show the LLM only information that existed before bids opened, then compare with what actually happened. For each IPO the only input is its abridged prospectus (published before bids open). No news, GMP, subscription numbers or listing results are shown. The LLM is asked for facts only, never for a prediction, which keeps outcome knowledge from leaking in.

## Why the abridged prospectus, not the full RHP
The full RHP is ~437 pages (~375K tokens), too big for a free-tier call. The abridged prospectus is 9-14 pages (~10K tokens), is the document brokers like Groww show retail investors, and still contains financials, promoters, objects of the issue, risk summary and litigation counts.

## LLM choice
Gemini free tier (Flash). Groq's free tier allows only ~8K tokens/minute and ~200K tokens/day on its larger models, which cannot handle documents of this size across many IPOs. Gemini limits come from third-party sources and should be checked in Google AI Studio. Model name is configurable via `GEMINI_MODEL`.

## Files
| File | Role |
|---|---|
| `src/prospectus.py` | Finds the filing on SEBI's public-issues listing, downloads the PDF, saves text to `data/prospectus/<key>.txt`. Reads only the latest listing page for now. |
| `src/extract.py` | Sends the text to Gemini with a fixed JSON schema (14 numeric fields + up to 5 red flags), temperature 0, saves `data/llm/<key>.json`. |

API key goes in `.env` (`GEMINI_API_KEY=...`), which is git-ignored.

## Pilot set (already listed, so outcomes are known)
| IPO | Final subscription | Gain at open | Gain at day-1 close | Prospectus saved |
|---|---|---|---|---|
| Moneyview | 101.87x | +61.76% | +58.91% | yes |
| A-One Steels | 12.23x | +12.35% | +2.96% | yes |
| Swastika Infra | 7.91x | +8.11% | +13.51% | yes |
| ArMee Infotech | 2.62x | 0.00% | -20.00% | yes |
| Elevate Campuses | 1.89x | -1.91% | -10.79% | no, not on SEBI latest listing page |

## What the pilot can and cannot prove
- Can prove: the pipeline runs, and extracted numbers match the document (checked by hand against the PDF).
- Cannot prove: that the features improve predictions. Five IPOs are far too few.

## Pilot results (gemini-2.5-flash, temperature 0)
- Ratios were correct on every field checked by hand against the PDFs (A-One: PAT margin 3.06, debt/equity 1.17, OFS 12.35% = 5,000 of 40,500 lakhs; ArMee: promoter 92.72, revenue growth 6.34%; Moneyview: revenue growth 43.26%).
- Absolute amounts were wrong: documents use different units (A-One and ArMee in INR lakhs, Moneyview in INR million), so crore conversions came out 10x off. Removed all absolute amounts from the schema; only ratios and percentages are extracted.
- Removed `promoter_holding_post_pct` and `pe_at_upper_band`: null for every IPO, since the abridged prospectus leaves post-issue numbers as [●] and has no peer P/E.
- Instability between two runs at temperature 0: `outstanding_litigation_count` (ArMee 13 then 14), `debt_repayment_pct_of_proceeds` (0 vs null), `ofs_pct` null for Moneyview and Swastika. Treat these three as unreliable until checked or computed in code.
- Gemini returned HTTP 503 (overloaded) for a few minutes on one occasion; `extract.py` retries 4 times with backoff.
- Elevate Campuses not tested (not on SEBI's latest listing page).
- Four IPOs say nothing about predictive value. Subscription still explains the outcomes far better than any extracted ratio here.

## Gate to the real test
1. Pilot extraction is accurate (spot-check every field on at least 3 IPOs).
2. Add paging to `prospectus.py` to backfill 2024-2026 IPOs (about 250), run extraction on all (free-tier request limits make this a multi-day job).
3. Add features to the model one group at a time and keep a group only if walk-forward Brier score improves. If none do, the LLM layer stays as explanation-only.

## Known limits
- Valuation vs peers (P/E) usually sits in the full RHP, not the abridged prospectus, so `pe_at_upper_band` is often null.
- LLM unit conversion (million to crore) and ratio arithmetic can be wrong, hence the hand check.
- Live mode could add news and web search, but that is not used in backtests because it cannot be time-fenced.
