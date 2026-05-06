# Fantasy Arena

Production-grade scaffold for an Indian fantasy-sports + play-money social-casino platform.

> ⚠️ **Read [`LEGAL.md`](./LEGAL.md) before launching.** This codebase is a scaffold; real-money operations require KYC vendor contracts, payment-gateway merchant onboarding, GST/TDS registrations, and state-by-state legal review. The casino module is **play-money only** (virtual coins, no cash-out) — do **not** convert it to real-money gambling without dedicated state-wise gaming licences.

---

## What's inside

| Layer | Stack |
| --- | --- |
| **Web** | Next.js 14 (App Router) + TypeScript + Tailwind + React-Query |
| **Mobile** | Expo (React Native) + TypeScript + React-Query |
| **Backend** | FastAPI + SQLAlchemy 2 + Alembic + Pydantic v2 |
| **DB / cache** | PostgreSQL 16 + Redis 7 |
| **Workers** | Celery + Redis broker |
| **Real-time** | FastAPI WebSockets + Redis pub/sub |
| **Shared** | TypeScript package (`packages/shared`) for types, sport configs, scoring constants |
| **Infra** | Docker Compose for local; Dockerfiles for prod; GitHub Actions CI |

Sports supported in MVP: **Cricket, Football, Kabaddi, Basketball.**

Casino games (play-money, provably-fair): **Crash, Plinko, Mines, Dice, Roulette, Slots, Blackjack.**

160+ features listed in [`FEATURES.md`](./FEATURES.md).

---

## Quick start (local dev)

### Prerequisites
- Node.js 20+
- pnpm 9+
- Python 3.11+
- Docker + Docker Compose
- (Optional) Expo CLI for mobile

### Boot infra + backend
```bash
# Postgres + Redis + Mailhog
docker compose up -d

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env       # fill sandbox keys
alembic upgrade head
python seed.py             # demo matches, players, contests, promos
uvicorn app.main:app --reload --port 8000
```

In another shell, start the worker:
```bash
cd backend && source .venv/bin/activate
celery -A app.workers.celery_app worker -l info
```

### Web
```bash
cd web
cp .env.example .env.local
pnpm install
pnpm dev      # http://localhost:3000
```

### Mobile
```bash
cd mobile
pnpm install
pnpm start    # scan QR with Expo Go
```

---

## Repo layout

```
fantasy-arena/
├── backend/                 FastAPI + Celery + Alembic
│   ├── app/
│   │   ├── api/             HTTP + WS routes
│   │   ├── models/          SQLAlchemy models
│   │   ├── schemas/         Pydantic v2 schemas
│   │   ├── services/        business logic (auth, wallet, scoring, casino…)
│   │   │   ├── scoring/     per-sport point engines
│   │   │   └── casino/      provably-fair game engines
│   │   ├── workers/         Celery tasks
│   │   └── middleware/      rate-limit, audit, geo-block
│   ├── alembic/             migrations
│   ├── tests/
│   └── seed.py
├── web/                     Next.js 14 app
├── mobile/                  Expo app
├── packages/shared/         shared TS types + sport configs
├── docker-compose.yml
├── .github/workflows/       CI (lint, test, typecheck, build)
├── README.md
├── LEGAL.md                 ⚠️ MUST READ BEFORE LAUNCH
├── GO_LIVE.md               production-readiness checklist
├── ARCHITECTURE.md          system design
└── FEATURES.md              160+ feature matrix
```

---

## Key architectural decisions

- **Double-entry ledger** for all money: every wallet change is two opposite-signed `LedgerEntry` rows that must sum to zero. Source of truth is the ledger, not the wallet balance column.
- **Idempotency keys** on every mutating financial endpoint to prevent duplicate debits on client retries.
- **Three-wallet model** per user: `deposit`, `winnings`, `bonus`. Different withdrawal/usage rules per pocket.
- **Provably-fair casino**: HMAC-SHA256(server_seed, client_seed:nonce) — server seed hash is committed to the user before play, revealed after.
- **Geo-fencing**: blocks fantasy real-money play in states where it is restricted (AS, OD, NL, SK, TG, AP). Casino module is play-money so geo-block does not apply.
- **Responsible-gaming hooks**: deposit limits, time-spent limits, self-exclusion, 18+ gate.
- **TDS Section 194BA**: 30 % on net winnings withdrawn (post-deposit basis); GST 28 % on entry-fee deposits — both implemented in `services/tax_service.py`.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for diagrams and data flow.

---

## Testing

```bash
# Backend
cd backend && pytest -q

# Web
cd web && pnpm test
pnpm lint && pnpm typecheck

# Mobile
cd mobile && pnpm typecheck
```

CI runs all three on every PR.

---

## Deployment

- **Backend** → Fly.io / Render / Railway. Volume not required (no local files); Postgres + Redis as managed add-ons. See `backend/Dockerfile` + `backend/fly.toml.example`.
- **Web** → Vercel (zero-config Next.js).
- **Mobile** → Expo EAS Build → App Store / Play Store. Note Play Store has India-specific real-money fantasy review process.

Full runbook in [`GO_LIVE.md`](./GO_LIVE.md).

---

## Contributing

Read [`CONTRIBUTING.md`](./CONTRIBUTING.md). PRs must pass lint, typecheck, and tests.

## Licence

Proprietary © Fantasy Arena. All rights reserved.
