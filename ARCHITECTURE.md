# Architecture

## High-level

```
┌────────────┐   ┌────────────┐
│  Web (TS)  │   │ Mobile (TS)│
│  Next.js   │   │   Expo     │
└─────┬──────┘   └─────┬──────┘
      │ HTTPS / WSS    │
      └────────┬───────┘
               │
       ┌───────▼────────┐
       │   FastAPI API  │      ◀──── Razorpay / Cashfree webhooks
       │   + WS hub     │      ◀──── Sports data API webhooks
       └──┬─────┬───┬───┘
          │     │   │
   ┌──────▼─┐ ┌─▼─┐ ▼ pub/sub
   │Postgres│ │Redis│ ──▶ Celery workers
   └────────┘ └────┘       (scoring, payouts, notifications)
```

## Core domains

### Identity
- `users` — login id, hashed password, phone, email, kyc_status, geo_state, age_verified, role.
- `kyc_records` — Aadhaar/PAN/selfie payloads (encrypted), vendor refs, verdicts.
- `sessions` — refresh-token jti, device fingerprint, ip, ua.

### Wallet & ledger
- `wallets(user_id)` with three pockets: `deposit`, `winnings`, `bonus`. Casino has separate `casino_coins`.
- `ledger_entries` — every money movement is at least two entries that must net to zero. Columns: `txn_id`, `account` (`user:42:deposit`, `system:gst_payable`, `gateway:razorpay_clearing`…), `amount` (signed), `currency`, `meta`.
- Invariant: `Σ ledger_entries.amount == 0` per `txn_id`. Enforced in DB by trigger and in code by `wallet_service.post_txn()`.
- `payments` — gateway-side payment intents, idempotency keys, webhook records.
- `withdrawals` — request → manager_review → approved/rejected → payout_initiated → payout_settled/failed. Each transition writes an `audit_log`.

### Fantasy
- `sports` — cricket / football / kabaddi / basketball.
- `tournaments`, `matches` — schedule + live state.
- `players` — per-sport, with credits, stats, role.
- `match_player_stats` — produced by scoring worker from raw events.
- `contests` — scope (match-specific), entry fee, prize pool, max teams, prize slabs (JSON).
- `user_teams` — 11 selected players per team + captain/vc.
- `contest_entries(contest_id, user_id, team_id)` — many users join one contest.
- `leaderboard_snapshots` — periodic snapshot for performance.

### Casino
- `casino_games` — definitions (slug, type, config).
- `casino_seeds` — server seed (revealed only after rotate), client seed, nonce per user.
- `casino_rounds` — bet, outcome, multiplier, payout, server_seed_hash, server_seed (after reveal), client_seed, nonce.
- Coins live in `wallets.casino_coins` only. Hard invariant: no service writes `casino_coins → winnings/deposit`.

### Promotions
- `promo_codes`, `cashback_rules`, `referrals`.

### Comms
- `notifications` (in-app), `notification_deliveries` (push/email/sms log).

### Compliance
- `audit_logs` — admin actions + critical user actions.
- `responsible_gaming_settings(user_id)` — limits.
- `self_exclusions` — start, end, scope.

## Request lifecycle (typical)

1. Client (web/mobile) calls `POST /v1/contests/{id}/join` with `Idempotency-Key` header and JWT.
2. Middleware: rate-limit → auth (JWT) → audit start → geo-block check (state vs sport).
3. `contest_service.join()`:
   - Validates user, contest open, team valid, lineup unlocked.
   - Calls `wallet_service.post_txn()` to debit deposit pocket + credit `system:contest_pool`. Idempotent on `Idempotency-Key`.
   - Inserts `contest_entry`.
   - Publishes `contest.entry.created` to Redis pub/sub (for WS leaderboard).
4. Returns receipt with `txn_id`.

## Real-time

Single Redis pub/sub bus. Channel topology:
- `match.{match_id}.events` — produced by ingestion worker.
- `contest.{contest_id}.leaderboard` — produced by scoring worker on each event.
- `user.{user_id}.notifications` — produced by notification service.
- `casino.{user_id}.{game}.state` — produced by casino service.

WebSocket gateway (`app/api/ws.py`) authenticates the socket, subscribes to relevant channels per route, fans out JSON frames.

## Scoring pipeline (cricket example)

```
sports-API webhook  ──▶  /webhooks/sports  ──▶  ingest_event Celery task
                                                    │
                                                    ▼
                                  match_player_stats upsert (idempotent)
                                                    │
                                                    ▼
                                  scoring/cricket.compute_points()
                                                    │
                                                    ▼
                                  user_team_points recompute  (only affected teams)
                                                    │
                                                    ▼
                                  Redis pub/sub → WS leaderboard
```

When match is `completed`, `payout_contest` task:
1. Locks all `contest_entries` for the match.
2. Sorts by points DESC + tie-breakers.
3. Applies prize slabs.
4. For each winner, posts `wallet_service.post_txn(system:contest_pool → user:winnings)`.
5. Marks contest completed, writes `audit_log`.

## Casino round lifecycle (provably-fair)

1. User starts session → server generates `server_seed` (random 32 B), stores it, returns `sha256(server_seed)` as `server_seed_hash`.
2. Each round, user supplies `client_seed`, server keeps `nonce`.
3. Outcome RNG: `HMAC_SHA256(server_seed, f"{client_seed}:{nonce}")` → bytes → game-specific decoder.
4. Round persisted with `server_seed_hash`, `client_seed`, `nonce`, **never** server_seed in plaintext until rotation.
5. User can rotate seed → server reveals old `server_seed`; user can verify any past round by recomputing HMAC themselves.

## Anti-fraud

- Login: rate-limit by IP+account, password breach check, suspicious device challenge.
- Signup: device fingerprint + IP + email + phone — multi-account detector.
- Withdrawals: velocity rules, KYC gate, manual review > threshold, penny-drop, mismatch flags.
- Contests: server-side validation of team composition, captain/vc assignment, lineup lock window.
- Casino: nonce monotonicity, server_seed rotate, server-only RNG.

## Observability

- Structured JSON logs with `request_id`, `user_id`, `route`, `latency_ms`, `outcome`.
- Sentry (DSN env var) for exceptions.
- Healthz `/healthz`, readyz `/readyz`, metrics `/metrics` (prometheus) endpoints.

## Failure modes & mitigations

| Failure | Mitigation |
| --- | --- |
| Gateway webhook arrives twice | Idempotency on `gateway_payment_id`. |
| Scoring API down | Worker retries with exp-backoff; manual override endpoint for admin. |
| Lineup-lock race | DB-level `FOR UPDATE` lock on contest row + `lock_at` check. |
| User starts withdrawal during ongoing scoring | Withdrawals dequeue only every 5 min; running tally is idempotent. |
| WS overload | Per-channel back-pressure; client falls back to SSE then polling. |
