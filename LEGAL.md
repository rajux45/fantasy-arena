# Legal & Compliance Notes

> **This is operator-level guidance, not legal advice.** Engage a qualified Indian gaming-law firm (e.g. Khaitan & Co, AZB & Partners, Ikigai Law) before going live.

---

## 1. Why this codebase ships two modules

| Module | Real money in / out? | Indian legal posture |
| --- | --- | --- |
| **Fantasy sports** (cricket, football, kabaddi, basketball) | Yes — paid contests with cash prizes | **Skill-based** under Indian Public Gambling Act 1867 + state Acts. Supreme Court (Varun Gumber 2017, RMD 2021) and Karnataka HC (2022) treat Dream11-style fantasy as game of skill, hence legal in most states. |
| **Play-money social casino** (crash, plinko, mines, dice, roulette, slots, blackjack) | Coins purchasable with real money, **NO cash-out** | Legal as entertainment — not gambling under any Indian state law because there is no real-money prize. |

**The casino module must never expose a real-money cash-out path.** The architecture enforces this:
- Casino coins live in a separate `casino_coin_balance` field, **not** in the `winnings` wallet pocket.
- The withdrawal endpoint (`POST /wallet/withdraw`) only debits `winnings` and `deposit` pockets.
- There is no admin path to convert casino coins → fantasy winnings → bank.

---

## 2. State restrictions for fantasy (real-money)

The following Indian states/UTs prohibit or restrict pay-to-play fantasy sports as of 2025:

- **Assam (AS)** — Assam Game and Betting Act, 1970
- **Odisha (OD)** — Odisha Prevention of Gambling Act, 1955
- **Nagaland (NL)** — restricted by Nagaland Prohibition of Gambling Act
- **Sikkim (SK)** — restricted (own licensing regime)
- **Telangana (TG)** — Telangana Gaming Act amendment 2017
- **Andhra Pradesh (AP)** — AP Gaming Act amendment 2020
- **Tamil Nadu (TN)** — partial restriction post-2022 amendments (currently litigated)

These are blocked at runtime in `backend/app/services/geo_service.py`. **You must update this list per the latest legal opinion before launch.**

---

## 3. Mandatory pre-launch artefacts

| Item | Owner | Rough cost / time |
| --- | --- | --- |
| Pvt Ltd company incorporation (MCA) | CA | ₹15-25 k / 2 wk |
| GST registration | CA | ₹0 / 1 wk |
| Razorpay/Cashfree merchant onboarding (Gaming MCC 7995) | Founder | ₹0 / 2-4 wk; needs MoA + GST + bank |
| KYC vendor contract (Digio / HyperVerge / Onfido) | Founder | ₹3-10 / KYC; ₹50 k MSA |
| Sports data API (Roanuz / Sportradar / Cricbuzz) | Founder | ₹15 k - 5 L /month |
| FIFS or AIGF self-regulation membership | Founder | ₹2-5 L /year |
| Privacy Policy, T&C, Refund Policy, Game-specific Rules, Responsible Gaming Policy | Lawyer | ₹50 k - 1 L |
| Cyber-insurance + D&O insurance | Broker | ₹50 k - 2 L /year |
| Information Security audit (CERT-In) before public launch | Auditor | ₹2-5 L |

---

## 4. Tax handling (already implemented in code)

### GST on entry fee — `tax_service.compute_gst_on_entry()`
- 28 % GST on the **full face value** of contest entry deposits (per 1 Oct 2023 amendment to CGST Act, Schedule III).
- We collect GST inclusive: when user deposits ₹100, ₹78.13 is credited to `deposit` pocket and ₹21.87 is recorded as GST liability (28/128 of 100).

### TDS Section 194BA — `tax_service.compute_tds_on_withdrawal()`
- 30 % TDS on **net winnings at the time of withdrawal** (inflows ledger – outflows ledger of `winnings` pocket since FY start).
- Deducted automatically; user receives Form 16A annually (generation script in `backend/app/workers/tax_filings.py`).
- TDS deposited to govt monthly via challan (manual).

### Audit
- All ledger entries are immutable and timestamped.
- `audit_logs` table records every admin action, every withdrawal approval, every wallet manual-adjust.
- Standard practice: monthly statutory audit by CA, quarterly internal audit, annual external audit.

---

## 5. KYC requirements

- **PAN + Aadhaar + selfie liveness** before first withdrawal of any amount (industry standard; FIFS code).
- **Video KYC** for withdrawals > ₹50 k cumulative (RBI guidance).
- **Bank-account penny-drop verification** before payout to that account.
- KYC re-verification every 24 months.
- Records retained 7 years (Income Tax Act).

---

## 6. Responsible gaming (already implemented)

- **18+ age gate** on signup.
- **Self-exclusion**: user can lock account for 1 / 7 / 30 / 90 days or permanently.
- **Deposit limits**: daily / weekly / monthly user-set limits, can only be reduced (cooling-off 24 h to increase).
- **Time-spent limits**: configurable hourly nudge.
- **Reality-check pop-ups** every 30 min of active play (configurable).
- All visible in `Settings → Responsible Gaming`.

---

## 7. Disallowed practices (don't add these)

- ❌ No real-money cash-out from casino games.
- ❌ No betting on real-world events (cricket match outcome, election results, etc.) — that is **wagering**, criminally illegal.
- ❌ No prize draws / lotteries / sweepstakes without separate state licence.
- ❌ No credit / loan / pay-later for deposits.
- ❌ No promotional ads / SMS to users in restricted states.
- ❌ No play by anyone < 18.

---

## 8. Disclaimers (must appear in app + marketing)

- "This game involves an element of financial risk and may be addictive. Please play responsibly and at your own risk."
- "Not available in Andhra Pradesh, Assam, Nagaland, Odisha, Sikkim, Telangana." (update as needed)
- "Skill-based contests only. No betting or gambling."

---

If anything in this file conflicts with current law, **current law wins**. Re-read this whole file with your lawyer before each major release.
