# Contributing

Thanks for contributing to Fantasy Arena.

## Branching
- `main` is protected; ship via PRs.
- Feature branches: `feat/<short-desc>`, fixes: `fix/<short-desc>`, chores: `chore/<short-desc>`.

## Commit style
Conventional Commits. Examples:
```
feat(wallet): add penny-drop verification stub
fix(scoring/cricket): correct strike-rate bonus thresholds
chore(ci): bump pnpm to 9.12
```

## Local checks
Before opening a PR:
```bash
# Backend
cd backend && ruff check . && ruff format --check . && mypy app && pytest -q

# Web
cd web && pnpm lint && pnpm typecheck && pnpm test

# Mobile
cd mobile && pnpm typecheck
```

## Code style
- Python: ruff + black-compatible (handled by ruff format), full type hints, no `Any` except at API edges.
- TS: strict mode, zod for runtime validation at API boundaries, prefer pure components.
- SQL: write Alembic migrations, never edit applied migrations.
- Money: never use float; always `Decimal` (Python) / `bigint` paise (TS / DB).

## Tests
- New endpoints require an integration test under `backend/tests/`.
- New scoring rules require a unit test in `backend/tests/scoring/`.
- New web components require a render smoke test.
