#!/usr/bin/env bash
# ==============================================================================
# NeoArcade installer — NEO App Script Convention v0 (for NEOPlay).
# Bộ game arcade vận động ThingBot trên NEO (Dế Foundation / ThingEdu).
#
# NEOPlay chạy: bash install_on_neo.sh --version=X.Y.Z   (không TTY, user thường)
# Thủ công:     bash install_on_neo.sh --version 0.1.0
# Gỡ:           bash install_on_neo.sh --uninstall
# ==============================================================================
set -euo pipefail

APP_ID="neoarcade"
DISPLAY_NAME="NeoArcade"
MODULE="neoarcade"
GIT_REPO="https://github.com/ThingEdu/NeoArcade.git"
BUNDLED_SRC="$HOME/Ai-Code/NeoArcade"          # source cài sẵn trên image NEO (nếu có)

APP_HOME="$HOME/Applications/$APP_ID"
VENV="$APP_HOME/venv"
BIN="$HOME/.local/bin/$APP_ID"
DESKTOP="$HOME/.local/share/applications/$APP_ID.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor/128x128/apps"
ICON_FILE="$ICON_DIR/$APP_ID.png"

VERSION=""
UNINSTALL=false
while [ $# -gt 0 ]; do
    case "$1" in
        --version=*)  VERSION="${1#*=}"; shift ;;
        --version)    VERSION="${2:-}"; shift 2 ;;
        --uninstall)  UNINSTALL=true; shift ;;
        --no-desktop) shift ;;
        *)            shift ;;                  # không hard-fail arg lạ (convention)
    esac
done

uninstall() {
    rm -rf "$APP_HOME" "$BIN" "$DESKTOP" "$ICON_FILE"
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    echo "$DISPLAY_NAME đã gỡ."
    exit 0
}
[ "$UNINSTALL" = true ] && uninstall

if [ -z "$VERSION" ]; then
    echo "NEOPLAY_ERROR=missing_version" >&2
    exit 1
fi

# Python 3.11+ (đã có sẵn trên image NEO)
if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,11) else 1)'; then
    echo "NEOPLAY_ERROR=missing_system_deps" >&2
    exit 1
fi

# Nguồn cài: ưu tiên bundled trên máy; nếu không có thì clone từ GitHub (repo public).
WORK=""
if [ -d "$BUNDLED_SRC/src/$MODULE" ]; then
    SRC="$BUNDLED_SRC"
    echo "Cài từ source bundled: $SRC"
else
    require_git() { command -v git >/dev/null || { echo "NEOPLAY_ERROR=missing_system_deps" >&2; exit 1; }; }
    require_git
    WORK="$(mktemp -d)"
    git clone --depth 1 "$GIT_REPO" "$WORK/NeoArcade" >/dev/null 2>&1 \
        || { echo "NEOPLAY_ERROR=clone_failed" >&2; exit 1; }
    SRC="$WORK/NeoArcade"
    echo "Cài từ GitHub: $GIT_REPO"
fi

# venv riêng cho app (convention #4). NeoArcade chỉ cần pygame-ce (có wheel aarch64).
rm -rf "$APP_HOME"
mkdir -p "$APP_HOME"
python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet "$SRC"          # kéo theo pygame-ce, tạo console-script 'neoarcade'

if [ ! -x "$VENV/bin/$APP_ID" ]; then
    echo "NEOPLAY_ERROR=install_failed" >&2
    exit 1
fi

# launcher trong ~/.local/bin (convention exec = ["neoarcade"])
mkdir -p "$(dirname "$BIN")"
ln -sf "$VENV/bin/$APP_ID" "$BIN"

# icon
if [ -f "$SRC/src/$MODULE/assets/logo_de.png" ]; then
    mkdir -p "$ICON_DIR"
    cp "$SRC/src/$MODULE/assets/logo_de.png" "$ICON_FILE"
    ICON_REF="$ICON_FILE"
else
    ICON_REF="applications-games"
fi

# .desktop (convention #6) — hiện trong menu desktop mục Education
mkdir -p "$(dirname "$DESKTOP")"
cat > "$DESKTOP" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$DISPLAY_NAME
GenericName=Arcade Games
Comment=Bộ game arcade vận động ThingBot trên NEO (Dế Foundation)
Exec=$BIN
Icon=$ICON_REF
Terminal=false
Categories=Education;
Keywords=neo;game;arcade;maker;education;de;
StartupNotify=true
EOF
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

# PATH có ~/.local/bin?
case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) grep -q 'local/bin' "$HOME/.bashrc" 2>/dev/null || \
       echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc" ;;
esac

[ -n "$WORK" ] && rm -rf "$WORK"

# marker thành công (convention #5 — dòng cuối)
echo "NEOPLAY_INSTALLED version=$VERSION"
