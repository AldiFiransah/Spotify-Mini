#!/usr/bin/env bash
# Pemasang untuk Arch Linux: menaruh aplikasi di ~/.local dan membuat entri menu.
set -e
cd "$(dirname "$0")"
DIR="$HOME/.local/share/pemutar-musik"
APPS="$HOME/.local/share/applications"
mkdir -p "$DIR" "$APPS" "$HOME/.local/bin" "$HOME/Music"
cp desktop/musik_gui.py terminal/musik_tui.py "$DIR/"

cat > "$HOME/.local/bin/musik-gui" <<EOT
#!/usr/bin/env bash
exec python3 "$DIR/musik_gui.py" "\$@"
EOT
cat > "$HOME/.local/bin/musik" <<EOT
#!/usr/bin/env bash
exec python3 "$DIR/musik_tui.py" "\$@"
EOT
chmod +x "$HOME/.local/bin/musik" "$HOME/.local/bin/musik-gui"

cat > "$APPS/pemutar-musik.desktop" <<EOT
[Desktop Entry]
Type=Application
Name=Pemutar Musik
Comment=Putar musik lokal
Exec=python3 $DIR/musik_gui.py
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
echo "Selesai. Ketik 'musik' (terminal) atau 'musik-gui' (jendela), atau cari 'Pemutar Musik' di menu aplikasi."
echo "Jika perintah tidak ditemukan: echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
