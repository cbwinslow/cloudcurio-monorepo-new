#!/usr/bin/env bash
set -euo pipefail
_cbw_detect_mono() {
    if [ -n "${CBW_MONO:-}" ]; then
        echo "$CBW_MONO"
        return 0
    fi

    local script_dir
    if [ -n "${BASH_SOURCE:-}" ]; then
        script_dir="${BASH_SOURCE[0]%/*}"
        [ "$script_dir" = "$BASH_SOURCE[0]" ] && script_dir="."
    elif [ -n "${ZSH_VERSION:-}" ]; then
        script_dir="${(%):-%x}"
    else
        script_dir="$(dirname "$0")"
    fi

    [ -z "$script_dir" ] && script_dir="."

    local dir
    dir="$(cd "$script_dir/../.." && pwd 2>/dev/null)" || {
        echo "$HOME/Documents/cloudcurio_monorepo"
        return 0
    }

    if [ -f "$dir/Makefile" ] && [ -d "$dir/agents" ] && [ -d "$dir/workflows" ]; then
        echo "$dir"
        return 0
    fi

    echo "$HOME/Documents/cloudcurio_monorepo"
    return 0
}

: "${CBW_MONO:=$(_cbw_detect_mono)}"
export CBW_MONO
cbw_repo(){ cd "$CBW_MONO" || return 1; }
