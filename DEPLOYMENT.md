# Deployment

This document covers deploying Fantasy Arena to a production environment.

> **⚠ Important.** This repository ships sandbox / placeholder integrations only.
> Before going live with real-money fantasy contests, see [GO_LIVE.md](GO_LIVE.md) for the
> full legal-and-business checklist (Pvt Ltd entity, GST, Razorpay live merchant, KYC vendor,
> AIGF/FIFS membership, etc.). The casino module is play-money only and **must not** be modified
> to support cash-out — see [LEGAL.md](LEGAL.md).

## Environments

| Env | Web | API | Database | Notes |
|---|---|---|---|---|
| local | `pnpm --filter web dev` | `uvicorn app.main:app --reload` | SQLite | dev / fastest iteration |
| ci | `next build` | `pytest` | SQLite (in-memory) | GitHub Actions |
| preview | Vercel preview | Fly.io app | Fly Postgres (small) | per-PR ephemeral |
| staging | Vercel | Fly.io / k8s | RDS Postgres | mirrors prod minus traffic |
| production | Vercel + CDN | Kubernetes | Postgres (HA) + Redis cluster | India region (ap-south-1) |

## Web (Next.js → Vercel)

```bash
# from repo root
pnpm install --frozen-lockfile
pnpm --filter @fantasy-arena/web build
```

Vercel project settings:

- Root directory: `web`
- Build command: `pnpm --filter @fantasy-arena/web build`
- Install command: `pnpm install --frozen-lockfile`
- Output directory: `.next`
- Env vars:
  - `NEXT_PUBLIC_API_URL` → `https://api.fantasy-arena.in`
  - `NEXT_PUBLIC_WS_URL` → `wss://api.fantasy-arena.in`

## API (FastAPI → Fly.io / Kubernetes)

Use the existing `backend/Dockerfile`:

```bash
cd backend
docker build -t fantasy-arena-api:latest .
```

### Fly.io (single-region quickstart)

```bash
flyctl launch --name fantasy-arena-api --region bom \
  --dockerfile Dockerfile --no-deploy
flyctl postgres create --name fantasy-arena-pg --region bom
flyctl secrets set \
  SECRET_KEY=... \
  DATABASE_URL=postgres://... \
  REDIS_URL=redis://... \
  RAZORPAY_KEY_ID=... \
  RAZORPAY_KEY_SECRET=...
flyctl deploy
```

### Kubernetes (production)

`infra/k8s/` contains:

- `api-deployment.yaml` (60 pods, HPA 30–200, readiness + liveness probes)
- `ws-deployment.yaml` (40 pods, separate scaling axis)
- `worker-deployment.yaml` (Celery, 80 pods, HPA 40–300)
- `beat-deployment.yaml` (single replica with leader election)
- `service.yaml`, `ingress.yaml` (NGINX), `hpa.yaml`, `pdb.yaml`
- `secrets.yaml.example`

## Database migrations

Always run migrations before rolling out new pods:

```bash
cd backend
alembic upgrade head
```

In Kubernetes use a Job:

```yaml
# infra/k8s/migrate-job.yaml
apiVersion: batch/v1
kind: Job
metadata: { name: migrate-{{ build_id }} }
spec:
  template:
    spec:
      containers:
        - name: alembic
          image: fantasy-arena-api:{{ build_id }}
          command: ["alembic", "upgrade", "head"]
      restartPolicy: Never
```

## Mobile (Expo → EAS)

```bash
cd mobile
eas build --platform android --profile production
eas build --platform ios --profile production
eas submit --platform android
eas submit --platform ios
```

## Smoke checks (post-deploy)

```bash
curl https://api.fantasy-arena.in/healthz   # {ok:true}
curl https://api.fantasy-arena.in/readyz    # {ok:true}
curl https://api.fantasy-arena.in/v1/sports # 4 entries
```

## Rollback

- API: `flyctl releases` → `flyctl deploy --image <prev>` (or `kubectl rollout undo deploy/api`).
- DB: forward-only migrations. Reverts go via a new migration; never `alembic downgrade` in prod.
- Web: Vercel "Promote previous deployment".
