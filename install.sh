#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
DIR="$HOME/.local/share/pemutar-musik"
APPS="$HOME/.local/share/applications"
mkdir -p "$DIR" "$APPS" "$HOME/.local/bin" "$HOME/Music"
cp index.html musik_tui.py "$DIR/"

cat > "$HOME/.local/bin/musik" <<EOT
#!/usr/bin/env bash
exec python3 "$DIR/musik_tui.py" "\$@"
EOT
chmod +x "$HOME/.local/bin/musik"

if command -v chromium >/dev/null; then GUI="chromium --app=file://$DIR/index.html"
elif command -v google-chrome-stable >/dev/null; then GUI="google-chrome-stable --app=file://$DIR/index.html"
else GUI="xdg-open $DIR/index.html"; fi

cat > "$APPS/pemutar-musik.desktop" <<EOT
[Desktop Entry]
Type=Application
Name=Pemutar Musik
Comment=Putar musik lokal
Exec=$GUI
Icon=multimedia-audio-player
Categories=AudioVideo;Audio;Player;
EOT

cat > "$APPS/pemutar-musik-terminal.desktop" <<EOT
[Desktop Entry]
Type=Application
Name=Pemutar Musik (Terminal)
Exec=$HOME/.local/bin/musik
Icon=multimedia-audio-player
Terminal=true
Categories=AudioVideo;Audio;Player;
EOT

command -v update-desktop-database >/dev/null && update-desktop-database "$APPS" || true
echo "Selesai. Cari 'Pemutar Musik' di menu aplikasi, atau ketik: musik"
