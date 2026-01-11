#!/usr/bin/env bash
set +e
export CBW_MONO="${CBW_MONO:-$HOME/Documents/cloudcurio_monorepo}"

_cbw_validate_repo() {
    local required_paths=("agents" "workflows" "kb" "bin" "shell" "docker/compose/observability" "src")
    local missing=()

    for path in "${required_paths[@]}"; do
        [ -d "$CBW_MONO/$path" ] || missing+=("$path")
    done

    if [ ${#missing[@]} -gt 0 ]; then
        echo "ERROR: CBW_MONO is not set to a valid CloudCurio repo root" >&2
        echo "Missing paths: ${missing[*]}" >&2
        echo "Please set CBW_MONO to: $HOME/Documents/cloudcurio_monorepo" >&2
        return 1
    fi
    return 0
}

[ -f "$CBW_MONO/shell/lib/logging.sh" ] && source "$CBW_MONO/shell/lib/logging.sh"
[ -f "$CBW_MONO/shell/lib/core.sh" ] && source "$CBW_MONO/shell/lib/core.sh"
cbw() { _cbw_validate_repo && "$CBW_MONO/bin/cbw" "$@"; }
cbw-agent() { _cbw_validate_repo && "$CBW_MONO/bin/cbw-agent" "$@"; }
cbw-index() { _cbw_validate_repo && "$CBW_MONO/bin/cbw-index" "$@"; }
cbw-doctor() { _cbw_validate_repo && "$CBW_MONO/bin/cbw-doctor" "$@"; }
cbw-workflow() { _cbw_validate_repo && "$CBW_MONO/bin/cbw-workflow" "$@"; }
cbw-capture() { _cbw_validate_repo && "$CBW_MONO/bin/cbw-capture" "$@"; }
