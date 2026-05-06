# Security model

## Threat model

| Threat | Mitigation |
|---|---|
| Account takeover (credential stuffing) | bcrypt cost-12, rate-limit /auth/login (per IP + per email), MFA opt-in (TOTP), email/SMS alert on new device login. |
| Stolen JWT | Short-lived access tokens (1h), refresh rotation with reuse detection, `device_id` binding. |
| Replay of payment webhook | Razorpay signature verification + idempotency table (`(provider, provider_event_id)` unique). |
| Double-spend on contest join | DB transaction + `idempotency_key` unique index + ledger double-entry post in same SQL transaction. |
| Multi-account abuse / bonus farming | PAN dedupe + Aadhaar-fragment dedupe + device fingerprint + bank account dedupe. |
| Withdrawal fraud | Manual approval queue for first withdrawal, velocity limits, KYC freshness, bank-account match to KYC PAN, AML checks for ≥ ₹1L. |
| Casino RNG manipulation | Provably-fair: server commits SHA-256 of seed before play; reveals seed on rotation; user can verify locally. |
| SQL injection | Only ORM/parameterized queries via SQLAlchemy 2.0; no f-string SQL. |
| XSS | React auto-escapes; CSP headers; `dangerouslySetInnerHTML` is forbidden in lint. |
| CSRF | API uses Bearer JWT only; no session cookies for state-changing requests. |
| PII leakage | KYC PII (PAN, full Aadhaar, address) AES-256-GCM encrypted with KMS key; only last-4 visible by default. Audit log for any PII view. |
| Brute-force / scraping | Token-bucket middleware (120 req/min default; `/auth/*` 10 req/min). |
| Insider threat | Admin actions written to append-only audit log; admin role uses 2FA mandatory; least-privilege scopes. |
| DoS | Cloudflare in front; Postgres connection pooling; queue-based offload (Celery). |
| Geo-bypass (real-money fantasy in restricted states) | KYC `state_code` enforced server-side at contest-join time; VPN detection on signup IP. |

## Cryptography

- Passwords: bcrypt (cost factor 12).
- JWTs: HS256 with rotated `SECRET_KEY` (90-day rotation).
- PII at rest: AES-256-GCM via dedicated KMS key (e.g. AWS KMS / HashiCorp Vault).
- TLS 1.3 only; HSTS 2-year; certificate pinning on mobile.
- Webhook signatures: HMAC-SHA256 (Razorpay-supplied).

## Data classification

| Class | Examples | Storage |
|---|---|---|
| Public | sport metadata, marketing copy | Postgres + CDN |
| Internal | match stats, contest configs | Postgres |
| Confidential | wallet balance, user email | Postgres, encrypted disk |
| Secret | password hash, JWT secret | Postgres, restricted access |
| Restricted | full PAN, full Aadhaar, bank acc no | Postgres, AES-GCM, KMS-wrapped |

## Logging & audit

- Every admin action and every privileged event written to `audit_events` (append-only).
- Application logs structured JSON; redact PII fields by default.
- 30-day hot retention, 7-year cold retention for compliance.

## Operational security

- Mandatory 2FA on all admin & engineer accounts.
- Production access via short-lived role assumption; no long-lived static keys.
- Quarterly external penetration tests; quarterly internal red-team.
- Annual SOC 2 Type II audit (post-launch).

## Incident response

- See [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md).
- 24/7 on-call rotation; PagerDuty integration.
- Public status page at status.fantasy-arena.in.
