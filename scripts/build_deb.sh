#!/usr/bin/env bash
# ==============================================================================
# Build the neo-arcade .deb inside a Debian bookworm container.
#
# The package is Architecture: all (pure Python + pygame), so one build works
# on both arm64 and amd64 — apt resolves python3-pygame per-architecture at
# install time. Requires docker (or podman via alias).
#
# Usage:  bash scripts/build_deb.sh
# Output: dist/neo-arcade_<version>_all.deb
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="debian:bookworm"

DOCKER="docker"
if ! command -v docker &>/dev/null; then
    if command -v podman &>/dev/null; then
        DOCKER="podman"
    else
        echo "ERROR: docker or podman is required." >&2
        exit 1
    fi
fi

mkdir -p "$REPO_ROOT/dist"

"$DOCKER" run --rm \
    -v "$REPO_ROOT:/src:ro" \
    -v "$REPO_ROOT/dist:/out" \
    "$IMAGE" bash -euo pipefail -c '
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        apt-get install -y -qq --no-install-recommends \
            build-essential debhelper dh-python devscripts \
            python3-all python3-setuptools pybuild-plugin-pyproject \
            >/dev/null

        # Work on a copy so the host repo stays clean.
        cp -a /src /build
        cd /build
        rm -rf dist .git

        dpkg-buildpackage -us -uc -b

        cp /neo-arcade_*_all.deb /out/
        chown "$(stat -c "%u:%g" /out)" /out/neo-arcade_*_all.deb || true
        echo ""
        echo "Built:"
        ls -lh /out/neo-arcade_*_all.deb
    '
