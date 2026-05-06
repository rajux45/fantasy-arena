## Summary

<!-- What does this PR change and why? -->

## Test plan

- [ ] `pnpm install` and `pnpm --filter @fantasy-arena/web build` succeed
- [ ] Backend `pytest` is green
- [ ] Backend `ruff check .` is clean

## Legal & compliance

- [ ] No real-money cash-out path was introduced for casino coins.
- [ ] No new sport/contest types bypass geo-fencing for restricted states (AS/OD/NL/SK/TG/AP).
- [ ] Money values are stored/transferred as integer paise — never as floats.

## Notes

<!-- Migrations, config changes, follow-ups, screenshots… -->
