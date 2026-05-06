# Go-Live Checklist

A linear list — do not skip steps.

## Phase 0 — Legal & corporate
- [ ] Incorporate Pvt Ltd company (India), get CIN.
- [ ] GSTIN obtained.
- [ ] PAN/TAN obtained.
- [ ] Engage gaming-law firm for opinion letter (state-wise legality, fantasy + casino models).
- [ ] Draft & sign: Privacy Policy, T&C, Refund Policy, Responsible Gaming Policy, Game Rules per sport. Publish on web + mobile + admin.
- [ ] FIFS / AIGF self-regulation membership filed.

## Phase 1 — Vendors & accounts
- [ ] Razorpay / Cashfree merchant account (MCC 7995 — gaming). Get live key + webhook secret.
- [ ] KYC vendor (Digio / HyperVerge / Onfido) MSA + sandbox + live keys.
- [ ] Sports data API (Roanuz for cricket+kabaddi, Sportradar for football+basketball) live keys + webhook URLs.
- [ ] SMS / OTP vendor (MSG91, Kaleyra, Twilio) DLT registered, sender IDs approved.
- [ ] Email vendor (Postmark / SES) verified domain.
- [ ] Push: FCM project + APNs key.
- [ ] Cloud: AWS / GCP / Azure account, billing alerts.
- [ ] Domain + SSL.

## Phase 2 — Infra
- [ ] Production Postgres (managed, multi-AZ, daily backups, PITR).
- [ ] Production Redis (managed).
- [ ] Object storage (S3 / GCS) for media, KYC docs (encrypted, KMS-managed key).
- [ ] CDN (CloudFront / Cloudflare) for static + media.
- [ ] Secrets manager (AWS SM / Vault) — never .env on servers in prod.
- [ ] WAF rules (Cloudflare / AWS WAF).
- [ ] Sentry / Datadog / NewRelic.
- [ ] Backup + restore drill executed.

## Phase 3 — Code hardening
- [ ] All env vars in production: see `backend/.env.example`, `web/.env.example`.
- [ ] Bcrypt rounds set to 12+ in prod.
- [ ] CORS allow-list locked to your domains.
- [ ] CSRF protection on cookie-based admin.
- [ ] Helmet / strict CSP on web.
- [ ] `DEBUG=False`, no stack traces to clients.
- [ ] Encrypted-at-rest fields verified (Aadhaar, PAN, bank account).
- [ ] Run `bandit`, `safety`, `npm audit`, `pnpm audit`.
- [ ] Load test (locust / k6) at expected peak (e.g. IPL final tier-1 spike).

## Phase 4 — Compliance scripts
- [ ] Geo-block list updated to current legal opinion.
- [ ] State-wise IP geolocation source tested (MaxMind GeoIP2 City).
- [ ] Daily TDS file generation tested and matches CA expectation.
- [ ] Daily GST report tested (GSTR-1 prep).
- [ ] Withdrawal manual-review threshold set (default ₹10k).
- [ ] Self-exclusion + responsible-gaming UI verified end-to-end.

## Phase 5 — Audits
- [ ] Penetration test by third-party (CERT-In empanelled).
- [ ] Internal security review.
- [ ] Privacy review (DPDP Act 2023 readiness).
- [ ] Legal sign-off on go-live.

## Phase 6 — Launch
- [ ] Soft-launch to 100 invitees for 7 days.
- [ ] Monitor: error rate, p95 latency, withdrawal SLA, KYC success rate.
- [ ] Public launch. Marketing only in non-restricted states.
- [ ] On-call rotation.
- [ ] Statutory monthly: TDS deposit (7th), GST filing (20th), payroll. Quarterly: TDS return.

## Phase 7 — Continuous
- [ ] Quarterly internal audit.
- [ ] Annual external audit + ISO 27001 path.
- [ ] Annual legal review of state-wise restrictions.
- [ ] Quarterly DR drill.
