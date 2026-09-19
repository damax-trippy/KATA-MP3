#!/usr/bin/env bash
# KATA-MP3 installer — sets up venv + desktop entry.
# Safe to re-run.

set -euo pipefail

# --- Where is this script? ------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

APP_NAME="KATA-MP3"
VENV_DIR="$SCRIPT_DIR/.venv"
PY="$VENV_DIR/bin/python"

# --- Colors ---------------------------------------------------------------
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[x]${NC} $*" >&2; }

# --- Sanity checks --------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
    error "python3 not found. Install it with: sudo apt install python3 python3-venv"
    exit 1
fi

if ! python3 -c "import venv" 2>/dev/null; then
    error "python3-venv module missing. Install with: sudo apt install python3-venv"
    exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
    warn "ffmpeg not found. MP3 conversion will FAIL."
    warn "Install it with: sudo apt install ffmpeg"
    read -rp "Continue anyway? [y/N] " ans
    [[ "${ans,,}" == "y" ]] || exit 1
fi

# --- Create venv ----------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
else
    info "Virtual environment already exists"
fi

# --- Install Python deps --------------------------------------------------
info "Installing Python dependencies"
"$PY" -m pip install --upgrade pip wheel >/dev/null
"$PY" -m pip install -r requirements.txt

# --- Install .desktop entry ----------------------------------------------
DESKTOP_SRC="$SCRIPT_DIR/packaging/kata-mp3.desktop"
DESKTOP_DST="$HOME/.local/share/applications/kata-mp3.desktop"

if [ -f "$DESKTOP_SRC" ]; then
    info "Installing desktop entry to $DESKTOP_DST"
    mkdir -p "$(dirname "$DESKTOP_DST")"

    # Rewrite Exec / Path / Icon placeholders with real paths
    sed \
        -e "s|__VENV_PYTHON__|$PY|g" \
        -e "s|__SCRIPT_DIR__|$SCRIPT_DIR|g" \
        -e "s|__ICON__|$SCRIPT_DIR/assets/icon.png|g" \
        "$DESKTOP_SRC" > "$DESKTOP_DST"

    chmod +x "$DESKTOP_DST"

    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$HOME/.local/share/applications" || true
    fi
else
    warn "No desktop file found at $DESKTOP_SRC — skipping menu entry"
fi

info "Done."
echo
echo "  Launch from your app menu (search for '$APP_NAME')"
echo "  Or run directly:  $PY $SCRIPT_DIR/main.py"
echo
