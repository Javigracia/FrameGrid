#!/usr/bin/env bash
# FrameGrid — Copyright (C) 2026 Javier
# SPDX-License-Identifier: GPL-3.0-or-later
# Instala FrameGrid en ~/.local/share/framegrid y crea el lanzador del escritorio.
#   ./install.sh            -> instala + acceso en el menú de KDE
#   ./install.sh --steam    -> además lo añade a la biblioteca de Steam (en vivo, sin cerrar Steam)
#   ./install.sh --uninstall
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.local/share/framegrid"
APPS="$HOME/.local/share/applications"
DESKTOP_FILE="$APPS/framegrid.desktop"

if [[ "${1:-}" == "--uninstall" ]]; then
  rm -rf "$DEST" "$DESKTOP_FILE" "$HOME/Desktop/framegrid.desktop"
  echo "FrameGrid desinstalado (tu API key sigue en ~/.config/framegrid; bórrala si quieres)."
  exit 0
fi

command -v python3 >/dev/null || { echo "Falta python3"; exit 1; }
python3 - <<'EOF' || { echo "Se necesita Python 3.9 o superior"; exit 1; }
import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)
EOF

mkdir -p "$DEST" "$APPS"
cp -r "$SRC/framegrid.py" "$SRC/fg" "$SRC/web" "$SRC/framegrid.svg" "$SRC/LICENSE" "$DEST/"
chmod +x "$DEST/framegrid.py"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=FrameGrid
Comment=Carátulas de SteamGridDB y colecciones para Steam
Exec=python3 $DEST/framegrid.py
Icon=$DEST/framegrid.svg
Terminal=false
Categories=Game;Utility;
EOF
chmod +x "$DESKTOP_FILE"
if [[ -d "$HOME/Desktop" ]]; then
  cp "$DESKTOP_FILE" "$HOME/Desktop/framegrid.desktop"
  chmod +x "$HOME/Desktop/framegrid.desktop"
fi
command -v update-desktop-database >/dev/null && update-desktop-database "$APPS" >/dev/null 2>&1 || true
echo "Instalado en $DEST — búscalo como «FrameGrid» en el menú de aplicaciones."

if [[ "${1:-}" == "--steam" ]]; then
  # Con Steam abierto usa el modo en vivo (depurador CEF); no hace falta cerrar Steam
  python3 "$DEST/framegrid.py" --add-to-steam
fi
echo
python3 "$DEST/framegrid.py" --status || true
