# Upgrading from older versions (v1–v3) to FINAL (v4)

Manual merges are painful. Use the provided script.

## What it does

1. Verifies the old repo path exists.
2. Creates a timestamped backup zip.
3. Overlays FINAL framework directories:
   - `bin/`, `src/`, `agents/`, `workflows/`, `kb/`, `docker/`, `shell/`, `scripts/`, `prompts/`, `tests/`
   - key root files like `Makefile`, `pyproject.toml`, and `.github/`
4. Does **not** delete your custom files.
5. Optionally runs verification (`bootstrap.sh` + `make ...`)

## Usage

```bash
bash ./scripts/upgrade_existing_repo.sh \
  --old ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo \
  --backup-dir ~/Documents/cloudcurio_monorepo/backups \
  --apply
```

Options:
- `--dry-run` prints actions only
- `--no-verify` skips verification

After upgrade, run:

```bash
cd ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
./scripts/bootstrap.sh
make doctor index validate compile eval
```
