#!/usr/bin/env bash
set -euo pipefail
cbw_ts(){ date +%Y-%m-%dT%H:%M:%S%z; }
cbw_log(){ printf "[%s] %s\n" "$(cbw_ts)" "$*"; }
cbw_warn(){ cbw_log "WARN: $*"; }
cbw_err(){ cbw_log "ERROR: $*"; }
