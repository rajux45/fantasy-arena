# Responsible gaming

We follow AIGF / FIFS responsible-gaming guidelines and add a few stricter defaults.

## Tools available to every user

- **Daily deposit limit** — default ₹10,000/day; user can lower it instantly. Raising takes effect 24 hours later.
- **Weekly deposit limit** — default ₹50,000/week.
- **Monthly deposit limit** — default ₹2,00,000/month.
- **Session-time reminder** — every 30 min, popup with elapsed time + cumulative deposit + cumulative win/loss.
- **Cool-off** — pause for 24h, 7d, or 30d. While active: no deposits, no contest joins, no casino plays. Withdrawals still allowed.
- **Self-exclude** — 1d / 7d / 30d / 6mo / permanent. Stricter than cool-off: also disables logins (or shows lock screen).
- **Reality check** — visible on every screen: today's net P&L; never hidden.

## Hard guardrails (cannot be disabled)

- **Age check (18+)** — at signup AND at KYC.
- **Geo block** — fantasy real-money disabled in AS, OD, NL, SK, TG, AP. Casino is play-money only — not geo-restricted, but minors blocked everywhere.
- **No real-money cash-out for casino coins** — by design and by law; the architecture has no such code path.
- **Underage detection** — periodic re-verification; flag inconsistencies between PAN-based age and behavioural signals.
- **Loss-chasing protection** — if a user loses > ₹5,000 in 60 minutes, app shows mandatory 5-minute cool-off + reality check.

## In-app messaging

- Bet input fields show "what you stand to win / lose" up-front, in plain Hindi/English.
- After a loss > ₹500 in casino, a tip appears: "Set a session limit. Take a break."
- After a winning streak that puts a user over their typical daily deposit, a calmer reminder appears.
- No "near-miss" animations, no "your luck is about to change" copy. Ever.

## What we do NOT do

- We do not extend credit. All play is from pre-funded wallet.
- We do not advertise to users who have self-excluded. (CRM filter by status.)
- We do not show win-frequency claims that aren't auditable from the ledger.
- We do not allow promo bonuses to convert to cash without play-through (transparent in promo T&Cs).

## Help & external resources

- In-app helpline: 1800-XXX-XXXX (24/7 in HI/EN).
- Email: care@fantasy-arena.in.
- External: Tata SAMVAD helpline, iCALL Tata, [Gambling Therapy](https://www.gamblingtherapy.org/) for severe cases.

## Operator dashboards

- Daily: counts of users hitting daily/weekly/monthly limits.
- Weekly: self-exclusions started / lifted / extended.
- Monthly: session-time distributions; deposit-loss correlations; flagged accounts requiring outreach.
