#!/usr/bin/env bash
# ==============================================================================
# NeoArcade Installer
# Installs the NeoArcade .deb package from GitHub Releases.
# Works on any apt-based system (Armbian/Debian/Ubuntu), arm64 and x86:
# the package is Architecture: all — apt pulls python3-pygame for each
# architecture.
#
# Usage:
#   Local:  bash scripts/install_on_neo.sh
#   Remote: curl -sSL https://raw.githubusercontent.com/ThingEdu/NeoArcade/main/scripts/install_on_neo.sh | bash
#
# Options:
#   --uninstall        Remove NeoArcade installation
#   --version=X.Y.Z    Install a specific release (default: latest)
# ==============================================================================
set -euo pipefail

# -- Configuration ------------------------------------------------------------
REPO="ThingEdu/NeoArcade"
PKG="neoarcade"
BIN="neoarcade"
RAW_INSTALL_URL="https://raw.githubusercontent.com/${REPO}/main/scripts/install_on_neo.sh"

# -- Parse arguments -----------------------------------------------------------
UNINSTALL=false
INSTALL_VERSION=""

for arg in "$@"; do
    case "$arg" in
        --uninstall)  UNINSTALL=true ;;
        --version=*)  INSTALL_VERSION="${arg#*=}"; INSTALL_VERSION="${INSTALL_VERSION#v}" ;;
        *)            echo "Unknown option: $arg"; exit 1 ;;
    esac
done

# -- Helpers -------------------------------------------------------------------
info()  { echo -e "\033[1;32m[INFO]\033[0m  $*"; }
warn()  { echo -e "\033[1;33m[WARN]\033[0m  $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*" >&2; }

require_cmd() {
    if ! command -v "$1" &>/dev/null; then
        error "'$1' is required but not found. Please install it first."
        exit 1
    fi
}

SUDO="sudo"
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
fi

# -- Uninstall -----------------------------------------------------------------
if [ "$UNINSTALL" = true ]; then
    info "Uninstalling $PKG..."
    if command -v apt-get &>/dev/null && dpkg -s "$PKG" &>/dev/null; then
        $SUDO apt-get remove -y "$PKG"
    fi
    info "$PKG has been uninstalled."
    exit 0
fi

# -- Pre-flight checks ---------------------------------------------------------
info "Detected architecture: $(uname -m)"

if ! command -v apt-get &>/dev/null; then
    error "This installer requires an apt-based system (Armbian/Debian/Ubuntu)."
    exit 1
fi
require_cmd curl

# -- Step 1: Resolve version ----------------------------------------------------
if [ -z "$INSTALL_VERSION" ]; then
    info "Resolving latest release..."
    INSTALL_VERSION="$(curl -sSL "https://api.github.com/repos/${REPO}/releases/latest" \
        | grep -m1 '"tag_name"' | sed -E 's/.*"v?([^"]+)".*/\1/')"
    if [ -z "$INSTALL_VERSION" ]; then
        error "Could not determine the latest release. Check your network,"
        error "or pin a version: bash install_on_neo.sh --version=X.Y.Z"
        exit 1
    fi
fi
info "Installing $PKG $INSTALL_VERSION"

DEB_NAME="${PKG}_${INSTALL_VERSION}_all.deb"
DEB_URL="https://github.com/${REPO}/releases/download/v${INSTALL_VERSION}/${DEB_NAME}"

# -- Step 2: Download and install ------------------------------------------------
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

info "Downloading $DEB_URL"
if ! curl -fSL --progress-bar -o "$TMP_DIR/$DEB_NAME" "$DEB_URL"; then
    error "Download failed. Does release v${INSTALL_VERSION} exist and include ${DEB_NAME}?"
    error "See: https://github.com/${REPO}/releases"
    exit 1
fi

info "Installing via apt (pulls python3-pygame)..."
$SUDO apt-get update -qq || true
$SUDO apt-get install -y "$TMP_DIR/$DEB_NAME"

# -- Step 3: Verify ------------------------------------------------------------
if ! command -v "$BIN" &>/dev/null; then
    error "Installation failed - '$BIN' not found on PATH."
    exit 1
fi
info "Verified: $(command -v "$BIN")"

# -- Done ----------------------------------------------------------------------
echo ""
info "=========================================="
info "  $PKG $INSTALL_VERSION installed successfully!"
info "=========================================="
echo ""
echo "  Run:  $BIN"
echo ""
echo "  Uninstall:  curl -sSL $RAW_INSTALL_URL | bash -s -- --uninstall"
echo ""
