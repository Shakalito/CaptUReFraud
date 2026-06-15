# Development workflow

This project is developed using GitHub issues, epics, feature branches, and Docker-based execution.

---

## Commit convention

Commits use short conventional-style messages that describe the changed area.

Examples:

- `feat(simulation): add prediction interface`
- `feat(model): add reproducible training script`
- `docs: reorganize project documentation`
- `ops: improve startup and dataset setup scripts`
- `frontend: add risk levels and suspicious alerts`
- `simulation: expose transaction business fields`

## Running tests

Backend tests should be run from the project root through Docker Compose:

```bash
docker compose exec app python3 -m pytest tests
```

Frontend validation should be run from the project root through Docker Compose:

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
```

## Local artifacts

The following directories are generated locally and are not tracked by Git:

- `data/raw/`
- `data/processed/`
- `models/`

These artifacts must be recreated locally after cloning the repository.
