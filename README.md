# ipo-agent

A small, free system that estimates how an Indian mainboard IPO is likely to list: the chance it lists at a loss, a small gain, a good gain or a big gain. On the last day of bidding it sends a short verdict to Telegram: **APPLY**, **SKIP** or **ABSTAIN**.

It is a personal research and engineering project. It is **not investment advice**, it is not a registered advisory service, and it should not be used as one.

## What a message looks like

This is the real alert it sent for HD Fire Protect at 16:00 IST on the last bidding day (15 Oct 2026):

```
HD Fire Protect
Bids close 15 Oct
Subscription: 129.08x (institutions 253.6x, retail 28.14x)
Grey market premium: Rs 90

Verdict: APPLY (97% chance of no loss at listing)

Listing price vs issue price
Loss or flat   ░░░░░░░░░░   3%
Gain 0-10%     █░░░░░░░░░   6%
Gain 10-30%    ██░░░░░░░░  25%
Gain over 30%  ███████░░░  66%
```

It listed on 21 Oct at **+23.6%**. The verdict held, though its most likely bucket (over 30%) did not: it landed in 10-30%.

## How it works

1. **Collect.** Three times on each weekday it reads public IPO tables: how many times each IPO is oversubscribed (in total and by investor type: institutions, wealthy individuals, retail), its valuation (P/E), and the grey market premium. Every snapshot is appended to a log and never overwritten.
2. **Compare.** A small model trained on about 450 past mainboard IPOs (2021-2026) turns the subscription level into probabilities for four outcomes.
3. **Decide.** On the last bidding day after 15:30 IST it gives a verdict: APPLY if the chance of no loss is at least 90%, SKIP if it is under 50%, ABSTAIN in between. Before that it only reports "too early", because early bidding numbers are not a fair guide.
4. **Keep score.** Every verdict is saved. Each Saturday the system checks it against how the IPO actually listed and sends a scorecard.

```
public IPO tables ──> logger (3x a day) ──> append-only logs ──> model ──> Telegram verdict
                                                     │
listing results ───> weekly refresh ──> training history + scorecard ──> Telegram scorecard
```

Everything runs on GitHub Actions, started by a free outside timer, with CSV files as the database. There is no server and it costs nothing to run.

## Results

**Backtest.** The model is trained only on earlier years and tested on the following year (2023 to 2026, 352 IPOs, data as of 22 Oct 2026).

| | |
|---|---|
| IPOs where it said APPLY | 145 |
| Of those, did not lose at listing | 95.2% (95% confidence range 90-98%) |
| Same check, 2026 only (a weaker year for IPOs) | 92% on 36 picks (range 78-97%) |
| Error score (Brier), model vs always guessing the average | 0.622 vs 0.758 (lower is better) |

It is cautious by design. In 2026 it held back on 34 of the 67 IPOs that went on to list at a gain.

**Live track record.** Only verdicts given before bidding closed count.

| IPO | Verdict | Listed | At open |
|---|---|---|---|
| HD Fire Protect | APPLY (97%) | 21 Oct 2026 | +23.6% |
| Fusion CX | SKIP (50%) | 22 Oct 2026 | +5.5% (a missed gain) |
| Tonbo Imaging India | APPLY (96%) | 23 Oct 2026 | pending |
| Zetwerk | SKIP (45%) | 23 Oct 2026 | pending |
| Sahajanand Medical Technologies | ABSTAIN (63%) | 23 Oct 2026 | pending |
| Bonfiglioli Transmissions | ABSTAIN (83%) | 23 Oct 2026 | pending |

This is a very small sample and proves little yet. The full, automatically updated list is in [`data/scorecard.csv`](data/scorecard.csv).

## What I learned building it

- **My first results were too good to be true.** A model using the grey market premium hit 100% precision on 65 picks. The premium in my historical data turned out to be recorded on listing morning, days after bidding closes, so it leaked the answer. I threw those results away and rebuilt on information that exists before the decision.
- **Free historical data for the most popular signal does not exist.** So the system logs it going forward, at the moments a real decision is made, and will test it once enough IPOs have listed.
- **Simple beat complex here.** Issue size, recent market mood and company financials read from the prospectus with an LLM did not improve the out-of-sample score. The parked LLM experiment is still in `src/prospectus.py` and `src/extract.py`.
- **Scheduled cloud jobs are not punctual.** GitHub dropped or delayed many scheduled runs by hours, so an outside timer now triggers them on time.

## Run it yourself

Requires Python 3.9 or newer.

```bash
pip install -r requirements.txt
python3 src/build_dataset.py --fetch   # download yearly IPO tables (2021 to now) and build data/ipos.csv
python3 src/model.py                   # quick self-check
python3 src/evaluate.py                # walk-forward backtest
python3 src/log_gmp.py                 # take one live snapshot
python3 src/predict.py | sed 's/<[^>]*>//g'   # message for IPOs closing today (from 15:30 IST)
```

`--fetch` downloads the past results from the public source, which allows automated access in its robots.txt. Please keep requests polite.

To automate your own copy: fork it, add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as repository secrets, and point an outside timer (for example cron-job.org) at the `gmp-snapshot` workflow's dispatch URL using a fine-grained token with only "Actions: read and write" on your repository. The workflows are in `.github/workflows/`.

## Project layout

| Path | What it does |
|---|---|
| `src/build_dataset.py` | Downloads and parses past IPO results |
| `src/model.py` | The model: subscription in, four outcome probabilities out |
| `src/evaluate.py` | Walk-forward backtest, calibration table, confidence ranges |
| `src/log_gmp.py` | Live snapshot of the public IPO tables |
| `src/predict.py` | Builds the Telegram message and records verdicts |
| `src/notify.py` | Sends messages to Telegram |
| `src/update_data.py` | Weekly refresh of listing results |
| `src/scorecard.py` | Scores verdicts against real listings |
| `src/prospectus.py`, `src/extract.py` | Parked LLM experiment (reads offer documents) |
| `.github/workflows/` | Snapshot job (3x on weekdays) and weekly refresh, with Telegram alerts on failure |
| `data/` | Live logs, verdicts and scorecard, committed by the bot after every run |

## Limits

- It looks only at demand (subscription). It does not judge the company itself.
- Late bids on the last day can still change the picture, so SKIP and ABSTAIN are less certain than APPLY.
- Even with an APPLY verdict, retail allotment is often a lottery, and about one in ten confident calls can still lose.
- Markets change. Results from past years may not hold.

## Disclaimer

This project is for learning and research. It does not recommend buying or selling any security and is not registered with SEBI as an investment adviser or research analyst. Data comes from public sources and may be wrong or late. Make your own decisions.

## License

MIT. See [LICENSE](LICENSE).
