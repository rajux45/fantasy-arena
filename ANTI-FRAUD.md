# Anti-fraud playbook

## Signal sources

| Signal | Source |
|---|---|
| Device fingerprint | client-side (FingerprintJS-style) + server-side hash of UA/IP/screen |
| IP geolocation | MaxMind / IPInfo |
| KYC dedupe | PAN exact, Aadhaar fragment match, full-name+DOB fuzzy |
| Bank account dedupe | hash of (IFSC + last-4) on withdrawal |
| Velocity | sliding windows: deposits, contest joins, OTP requests, login attempts |
| Behavioural | session duration, click cadence, team-build patterns |

## Risk score

```
risk = w1 * device_collisions
     + w2 * pan_collisions
     + w3 * bank_collisions
     + w4 * velocity_z_score
     + w5 * geo_anomaly
     + w6 * payment_failure_rate
     + w7 * referral_chain_depth
     + w8 * promo_abuse_score
```

Bands:

| Score | Band | Action |
|---|---|---|
| 0-20 | green | normal |
| 20-50 | yellow | additional KYC step (selfie + liveness) on next deposit |
| 50-80 | orange | hold withdrawal for manual review; cap deposits at ₹1k/day |
| 80-100 | red | freeze account; investigate; SAR if AML thresholds breached |

## Specific anti-patterns

### Multi-account / bonus farming
- Same PAN → reject signup (after KYC).
- Same device fingerprint > 3 accounts → flag yellow.
- Same bank account on withdrawal > 2 accounts → freeze, AML flag.

### Collusion in private contests
- Detect rosters with > 70% player overlap among contest entries from same IP-block.
- Detect head-to-head pairs with reciprocal wins beyond statistical chance.

### Payment retry / chargeback
- 5+ failed deposits in 60 min → cooling period (10 min).
- Webhook idempotency on `(provider, provider_event_id)` (unique index).

### Withdrawal laundering
- First withdrawal > ₹50k → manual review.
- Bank account different from registered → 24h hold + email confirm.
- Velocity: > ₹2L in 24h triggers AML SAR pre-check.

### OTP / account-takeover
- 5+ wrong OTP in 10 min → lock OTP for 30 min.
- New device login → email + SMS notification + step-up KYC if recent withdrawal added.

## Manual review queue

Admin → Anti-fraud queue. Each card shows:

- User profile + KYC + recent ledger.
- Risk score breakdown (top 3 contributing signals).
- Linked accounts (device / PAN / bank match).
- Actions: approve, reject, freeze, request more KYC, escalate to AML.

Every action is written to `audit_events`.

## Reporting

- Daily: counts by band, false-positive rate from manual review.
- Weekly: SAR / STR submissions, recovered fraud value.
- Monthly: model retraining (gradient-boosted features) on labeled outcomes.
