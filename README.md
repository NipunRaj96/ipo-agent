# ipo-agent

A small tool that helps you decide whether to apply for an Indian IPO.

An IPO is when a company sells its shares to the public for the first time. Many people apply hoping the share will list above its issue price. This tool looks at how popular the IPO is and tells you how likely that is.

## What you get

A short Telegram message for each IPO that is open for bidding. On the last day of bidding, after 3:30 PM, it gives one of three answers:

- **APPLY**: the IPO is very likely to list at or above its issue price.
- **SKIP**: a loss is more likely than not.
- **ABSTAIN**: not clear enough to call.

It also shows the chances of a loss, a small gain (up to 10%), a good gain (10-30%) and a big gain (over 30%), for the listing price and for the end of the first day.

Before the last day it only shows the current numbers and says "too early", because early bidding numbers are not a fair guide.

## How it works

1. A few times a day it reads the public IPO table on InvestorGain and saves how many times the IPO has been oversubscribed (the more investors want it, the better it tends to do) along with the grey market price, the unofficial price people trade at before listing.
2. It compares that with 450 past IPOs from 2021 to 2026 and their actual results.
3. It sends you the result on Telegram.

It runs on its own on GitHub at about 11:00, 14:00 and 16:00 IST. It is free to run.

## How reliable is it?

When tested on past IPOs (2023 to 2026), the picks it was most sure about (APPLY) did not lose at listing about 95% of the time. In 2026 alone, a tougher year for IPOs, it was about 91% on fewer picks. A cautious reading is around 90%. It will be wrong sometimes, and it plays safe: in 2026 it skipped or held back on most of the IPOs that did well.

Two honest limits:

- The tests used the final bidding numbers. On the last day, late bids can still change the picture, so SKIP and ABSTAIN are less certain than APPLY.
- It only looks at how popular the IPO is. It does not read the company's accounts or news. We tried that and parked it for now.

## Setting it up

You need a free Telegram bot (made through @BotFather) and these values saved in the GitHub repository settings under Secrets: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. After that the schedule does the rest. You can also start it by hand from the Actions tab.

## Good to know

- This is a personal research project, not financial advice. Please decide for yourself.
- It is still being checked against real IPOs as they list.
- Plans and test results are in the `build-plan` folder.
