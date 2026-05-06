# Incident response

## Severity

| Level | Definition | Response time | Comms |
|---|---|---|---|
| SEV-0 | All users impacted; data loss / financial impact / regulatory breach. | 5 min ack, 15 min update cadence | Status page, X/Twitter, in-app banner. |
| SEV-1 | Major feature down; > 10% users impacted. | 15 min ack, 30 min update cadence | Status page, in-app banner. |
| SEV-2 | Single feature degraded; < 10% users impacted. | 1 hour ack, 2 hour update | Status page. |
| SEV-3 | Cosmetic / non-blocking. | next business day | None. |

## On-call

- PagerDuty rotation: Backend / SRE / Wallet (3 tracks, 1-week rotation).
- Primary + secondary; secondary auto-paged if primary doesn't ack in 15 min.
- Escalation policy: secondary -> on-call lead -> CTO.

## Playbooks

### `wallet-imbalance`
Symptom: `ledger_reconcile` task reports `Σ != 0`.
1. Freeze deposits + withdrawals + contest joins (feature flag `wallet.kill_switch`).
2. Snapshot `ledger_entries` to a backup table.
3. Run `wallet_service.find_unbalanced_txns` — get list of bad `txn_id`s.
4. Identify root cause (deploy diff, code change, race).
5. Roll back deploy if recent.
6. Manually correct via `admin/wallet/manual-adjust` with audit log entry citing this incident.
7. Resume traffic.

### `payment-webhook-flood`
1. Verify HMAC signatures — reject any without valid sig.
2. Confirm idempotency key dedup is working (no re-credits).
3. Check for replay of old events; rate-limit by `(provider, provider_event_id)`.

### `match-feed-stalled`
Symptom: cricket / football scores not updating > 60s.
1. Check Roanuz / data provider status page.
2. Restart `score_worker` Celery group.
3. If stalled > 5 min, post in-app banner "scoring delayed".

### `kyc-vendor-down`
1. Switch to fallback vendor (config flag).
2. Allow signups + non-real-money play to continue.
3. Block real-money fantasy contest joins until KYC completes.

### `auth-bruteforce`
1. Spike in `/auth/login` 401s — check rate-limit metrics.
2. Identify IPs / ASN; add to Cloudflare blocklist.
3. Force-rotate JWT secret if compromise suspected.

## Communication

- Status page: status.fantasy-arena.in (StatusPage / Atlassian).
- In-app banner via `system_announcements` table — read-time, no deploy.
- Customer support macros for common asks during outage.
- Postmortem within 5 business days, public summary for SEV-0/1.

## Postmortem template

See `docs/POSTMORTEM_TEMPLATE.md`. Covers: timeline, impact, root cause (5 whys), corrective actions, ownership, deadlines.
