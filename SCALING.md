# Scaling to 10 million users

## Targets

| Metric | Target |
|---|---|
| Registered users | 10,000,000 |
| Concurrent peak users (during major IPL match) | 1,500,000 |
| API requests / sec at peak | 60,000 |
| WebSocket messages / sec at peak | 250,000 (scoring fan-out) |
| p99 API latency | < 250 ms |
| p99 contest-join latency | < 400 ms |
| Database write throughput | 8,000 TPS sustained |
| Match-end settlement | All contests settled within 10 minutes of `match.complete` |

## Tiered architecture

```
                ┌───────────────────────────────┐
                │   Cloudflare (WAF + CDN +     │
                │   bot mgmt + DDoS shield)     │
                └─────────────┬─────────────────┘
                              │
                ┌─────────────┴─────────────────┐
                │  Edge: Next.js (Vercel /      │
                │  Cloudfront + S3 static)      │
                └─────────────┬─────────────────┘
                              │
                ┌─────────────┴─────────────────┐
                │  API gateway (NGINX / Envoy)  │
                │  + rate-limit token bucket    │
                └─────────────┬─────────────────┘
                              │
            ┌─────────────────┼──────────────────┐
            │                 │                  │
   ┌────────┴───────┐ ┌───────┴───────┐ ┌────────┴────────┐
   │ FastAPI (read) │ │FastAPI (write)│ │WebSocket cluster│
   │  60 pods       │ │ 30 pods       │ │ 40 pods         │
   └────────┬───────┘ └───────┬───────┘ └────────┬────────┘
            │                 │                  │
   ┌────────┴───────────┐ ┌───┴────────────┐  ┌──┴──────────┐
   │ Postgres replicas  │ │ Postgres prim  │  │ Redis (pub/ │
   │  (×8 read replicas)│ │  + Citus shard │  │ sub cluster)│
   └────────────────────┘ └────────────────┘  └─────────────┘
                              │
                              └─→ Celery workers (×80) ─→ Redis (queue)
```

## Database

- **Primary**: Postgres 16 with logical replication.
- **Sharding strategy**: Citus / Vitess by `user_id` for `ledger_entries`, `contest_entries`, `user_teams`.
- **Read replicas**: 8 replicas behind PgBouncer; lobby & leaderboard read-heavy queries fan out.
- **Connection pooling**: PgBouncer (transaction pooling) — backend pods see ~50 connections, real DB sees < 1000.
- **Hot indexes**: `(contest_id, points desc)` for leaderboards, `(user_id, created_at desc)` for ledger.
- **Archival**: Move closed contests > 90 days to cold storage (S3 + Athena).

## Caching

- **Redis (cluster mode)**: hot lookups — current match state, leaderboard top-100 (zset), seat counts, user wallet balance.
- **Local LRU**: per-pod sport configs, scoring tables, geo lookup table.
- **CDN**: Marketing pages, sport icons, player photos (immutable URLs).

## Real-time scoring fan-out

1. Roanuz feed → Celery `apply_score_event` task → DB update → Redis pub/sub → WebSocket pods → user clients.
2. WebSocket pods are stateless; users connected by `(contest_id, user_id)`.
3. Backpressure: per-user message queue capped at 1000; drop and snapshot on overflow.

## Wallet write path

- Single-leader for `ledger_entries` (Citus distributed table on `user_id`).
- Wallet operations are wrapped in a SERIALIZABLE transaction with idempotency key.
- Balance is **derived** by `SELECT SUM(amount_paise) WHERE account = 'wallet:winnings:{u}'` — but a materialized cache (Redis) is updated atomically inside the same transaction (commit hook).
- Reconciler job runs every 5 minutes; alarms if cache vs derived diverges > ₹0.

## Casino RNG

- Each round = one HMAC-SHA256 op on a single backend node (sub-millisecond). No DB write on play; aggregated round records flushed every 5s.
- Provably-fair: `server_seed` rotates per user every 1000 rounds or on user request.

## Observability

- **Metrics**: Prometheus → Grafana. SLOs alert via PagerDuty.
- **Traces**: OpenTelemetry → Tempo / Datadog APM.
- **Logs**: Loki / Datadog Logs (JSON structured).
- **Dashboards**:
  - Wallet (deposits, withdrawals, ledger imbalance count).
  - Contests (joins/sec, payouts/sec, settlement lag).
  - Casino (rounds/sec, RTP rolling 24h).
  - Auth (login success, OTP delivery rate).

## Deployment topology (production)

| Component | Replicas | Resources | Region |
|---|---|---|---|
| Next.js (web) | Vercel autoscale | — | India + global edge |
| FastAPI (api) | 60 pods (HPA 30–200) | 2 vCPU / 2 GB | ap-south-1 (Mumbai) |
| WebSocket | 40 pods (HPA 20–120) | 1 vCPU / 1 GB | ap-south-1 |
| Celery workers | 80 (HPA 40–300) | 2 vCPU / 4 GB | ap-south-1 |
| Postgres primary | 1 + 8 replicas | r6g.4xlarge | ap-south-1 |
| Redis cluster | 6 shards × 2 replicas | r6g.large | ap-south-1 |
| Object storage | S3 / GCS | infinite | ap-south-1 |

## Cost envelope (rough, peak month)

| Item | Approx cost / month |
|---|---|
| Compute (k8s, 200 nodes peak) | ₹15-20 L |
| Postgres (HA + replicas) | ₹6-8 L |
| Redis | ₹1.5 L |
| Cloudflare (Enterprise + 10 Tb egress) | ₹3 L |
| Razorpay TDR (~2%) | (revenue-linked) |
| KYC vendor (Digio / HV) | ₹2-4 L (volume-tiered) |
| Cricket data (Roanuz) | ₹15-50k |
| Total fixed | ~₹30 L / month at peak |

## Load testing

- Locust suite at `tests/load/` simulates lobby, team-build, contest-join, scoring, leaderboard, casino bet.
- CI runs smoke load at 1k concurrent; full 100k+ runs nightly in staging.
