# CloudCurio Monorepo — FINAL (v4)

This zip is a **single, ready-to-use** monorepo snapshot. You can use it **fresh** without merging anything.

## Fresh install (recommended)

```bash
cd ~/Documents
mkdir -p cloudcurio_monorepo
cd cloudcurio_monorepo

# Unzip this package so you end up with:
# ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo
unzip cloudcurio-monorepo-FINAL.zip -d .
cd cloudcurio-monorepo
```

## Bootstrap + verify

```bash
./scripts/bootstrap.sh
make doctor
make index
make validate
make compile
make eval
```

## Run the example agent

```bash
./bin/cbw-agent run agents/specs/examples/hello_world.agent.yaml --input "hello" --runtime local
```

## Observability (optional)

```bash
docker compose -f docker/compose/observability/docker-compose.yml up -d
```

---

## If you already have an older repo (v1–v3)

Use the upgrade script from this FINAL repo:

```bash
bash ./scripts/upgrade_existing_repo.sh --old ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo --backup-dir ~/Documents/cloudcurio_monorepo/backups --apply
```

That will:
- create a timestamped backup zip
- overlay the new framework safely
- keep your existing custom content intact
