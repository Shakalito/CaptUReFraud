# Development workflow

This project is developed using GitHub issues, epics, feature branches, and Docker-based execution.

---

## Commit convention

Commits follow the format:

`feat(scope): short description`

Examples:

- `feat(simulation): add prediction interface`
- `feat(model): add reproducible training script`
- `docs: reorganize project documentation`

## Running tests

Inside the Docker container:

```bash
python3 -m pytest tests
```

## Local artifacts

The following directories are generated locally and are not tracked by Git:

- `data/raw/`
- `data/processed/`
- `models/`
