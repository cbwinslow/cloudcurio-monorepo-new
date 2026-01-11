#!/usr/bin/env bash
# upgrade_existing_repo.sh
# Date: 2026-01-11
# Author: cbwinslow (generated with ChatGPT)
# Summary:
#   Safely upgrades an existing CloudCurio monorepo (v1–v3) to the FINAL (v4) framework
#   by taking a timestamped backup and overlaying the new framework directories.
#
# Safety:
#   - Does NOT delete user files.
#   - Requires --apply to actually modify anything.
#   - Uses rsync with sane defaults.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash ./scripts/upgrade_existing_repo.sh --old <OLD_REPO_PATH> --backup-dir <BACKUP_DIR> [--dry-run] [--apply] [--no-verify]

Required:
  --old         Path to your existing repo root (folder that contains bin/, scripts/, etc.)
  --backup-dir  Directory where backups should be written

Options:
  --dry-run     Print actions only
  --apply       Perform changes (required to actually upgrade)
  --no-verify   Skip ./scripts/bootstrap.sh and make checks

Example:
  bash ./scripts/upgrade_existing_repo.sh --old ~/Documents/cloudcurio_monorepo/cloudcurio-monorepo --backup-dir ~/Documents/cloudcurio_monorepo/backups --apply
EOF
}

OLD=""
BACKUP_DIR=""
DRY_RUN="0"
APPLY="0"
NO_VERIFY="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --old) OLD="${2:-}"; shift 2 ;;
    --backup-dir) BACKUP_DIR="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN="1"; shift ;;
    --apply) APPLY="1"; shift ;;
    --no-verify) NO_VERIFY="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$OLD" || -z "$BACKUP_DIR" ]]; then
  echo "ERROR: --old and --backup-dir are required."
  usage
  exit 2
fi

OLD="$(python3 -c 'import os,sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' "$OLD")"
BACKUP_DIR="$(python3 -c 'import os,sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' "$BACKUP_DIR")"

if [[ ! -d "$OLD" ]]; then
  echo "ERROR: old repo path not found: $OLD"
  exit 2
fi

mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_ZIP="$BACKUP_DIR/cloudcurio-monorepo-backup-$STAMP.zip"

echo "Old repo:   $OLD"
echo "Backup zip: $BACKUP_ZIP"
echo "Dry-run:    $DRY_RUN"
echo "Apply:      $APPLY"
echo "No-verify:  $NO_VERIFY"
echo

# Always create backup zip (unless dry-run)
if [[ "$DRY_RUN" == "1" ]]; then
  echo "DRY-RUN: would create backup zip of $OLD"
else
  (cd "$(dirname "$OLD")" && zip -r "$BACKUP_ZIP" "$(basename "$OLD")" >/dev/null)
  echo "Backup created."
fi

FINAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

overlay() {
  local rel="$1"
  local src="$FINAL_ROOT/$rel"
  local dst="$OLD/$rel"

  if [[ ! -e "$src" ]]; then
    echo "SKIP missing in FINAL: $rel"
    return 0
  fi

  if [[ "$DRY_RUN" == "1" || "$APPLY" != "1" ]]; then
    echo "PLAN: overlay $rel"
    return 0
  fi

  if [[ -d "$src" ]]; then
    mkdir -p "$dst"
    rsync -av "$src/" "$dst/"
  else
    cp -f "$src" "$dst"
  fi
}

# Framework overlay (authoritative)
overlay "bin"
overlay "src"
overlay "agents"
overlay "workflows"
overlay "kb"
overlay "docker"
overlay "shell"
overlay "scripts"
overlay "prompts"
overlay "tests"
overlay "docs"
overlay "pyproject.toml"
overlay "Makefile"
overlay ".pre-commit-config.yaml"
overlay ".editorconfig"
overlay ".github"
overlay "SECURITY.md"
overlay "CODEOWNERS"
overlay "CHANGELOG.md"
overlay "FINAL_VERSION.md"

if [[ "$DRY_RUN" == "1" || "$APPLY" != "1" ]]; then
  echo
  echo "Done (no changes applied). Re-run with --apply to perform upgrade."
  exit 0
fi

echo
echo "Overlay complete. Fixing executable bits..."
find "$OLD/bin" "$OLD/scripts" "$OLD/shell" -type f -exec chmod +x {} \; || true

if [[ "$NO_VERIFY" == "1" ]]; then
  echo "Skipping verification as requested."
  exit 0
fi

echo
echo "Running verification..."
cd "$OLD"
./scripts/bootstrap.sh
make doctor
make index
make validate
make compile
make eval
echo
echo "SUCCESS: upgrade verified."
