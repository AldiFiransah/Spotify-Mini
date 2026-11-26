# Pemutar Musik Lokal

Pemutar musik gratis bergaya Spotify untuk file lagu milikmu sendiri (MP3, FLAC, WAV, OGG, M4A, OPUS).
Tersedia dalam tiga versi, semuanya membaca lagu dari komputermu, tanpa akun dan tanpa internet.

> Proyek ini **tidak** mengambil lagu dari Spotify atau layanan streaming apa pun. Kamu perlu punya file lagunya sendiri.

## Versi yang tersedia

| Versi | Folder | Jalan di | Cocok untuk |
|---|---|---|---|
| Web | `web/` | Browser (Chromium/Firefox) | Dicoba cepat di OS apa saja |
| Terminal | `terminal/` | Terminal Linux | Dipakai di dashboard terminal (kitty, dll.) |
| Desktop | `desktop/` | Jendela aplikasi Linux (Qt) | Aplikasi biasa tanpa browser |

## Fitur

- **Web**: cover dan judul dari tag lagu, visualizer, acak, ulang, pencarian, tombol keyboard, tombol media keyboard.
- **Terminal**: tampilan biru, playlist, favorit, acak, ulang, pencarian, kontrol volume dan geser lagu.
- **Desktop**: cover album, pencarian, acak, ulang, mengingat folder musik terakhir.

## Menjalankan di browser

1. Buka `web/index.html` dengan Chromium atau Firefox (klik dua kali, atau `chromium web/index.html`).
2. Klik **Pilih folder musik** lalu pilih folder berisi lagumu. File tidak diunggah ke internet, tetap di komputermu.
3. Klik lagu untuk memutar.

Catatan:
- Cover dan judul dibaca memakai library `jsmediatags` yang dimuat dari internet (CDN). Tanpa internet, lagu tetap terputar, tetapi cover dan metadata tidak terbaca.
- Setiap halaman dimuat ulang, folder harus dipilih lagi.
- Tombol keyboard: `Spasi` putar/jeda, `N` berikutnya, `P` sebelumnya, `S` acak, `R` ulang, `←` `→` geser 5 detik.

## Menjalankan di Arch Linux

### 1. Pasang paket yang dibutuhkan

```bash
sudo pacman -S mpv python-mpv python-mutagen python-textual python-pyqt6
```

(`python-textual` untuk versi terminal, `python-pyqt6` untuk versi desktop. Pasang yang kamu pakai saja.)

### 2. Taruh lagu di `~/Music`

Folder `~/Music` dibaca otomatis, termasuk sub-foldernya. Contoh susunan:

```
~/Music/Santai/lagu-a.mp3
~/Music/Semangat/lagu-b.mp3
```

### 3. Pasang dan jalankan

```bash
git clone https://github.com/USERNAME/pemutar-musik.git
cd pemutar-musik
chmod +x install.sh
./install.sh
```

Setelah itu:

- **Terminal**: ketik `musik`
- **Jendela aplikasi**: ketik `musik-gui`, atau cari **Pemutar Musik** di menu aplikasi

Tanpa memasang, bisa langsung dijalankan:

```bash
python3 terminal/musik_tui.py            # membaca ~/Music
python3 terminal/musik_tui.py ~/Lagu     # membaca folder lain
python3 desktop/musik_gui.py
```

Jika muncul "command not found", tambahkan `~/.local/bin` ke PATH lalu buka ulang terminal:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Tombol versi terminal

| Tombol | Fungsi |
|---|---|
| `Enter` | Putar lagu yang dipilih |
| `Spasi` | Putar / jeda |
| `n` / `p` | Lagu berikutnya / sebelumnya |
| `l` | Ganti playlist |
| `a` | Tambah lagu terpilih ke Favorit |
| `d` | Hapus dari Favorit (saat di playlist Favorit) |
| `s` / `r` | Acak / ulang |
| `←` `→` | Mundur / maju 5 detik |
| `+` `-` | Volume |
| `/` | Cari (tekan `Enter` setelah mengetik) |
| `q` | Keluar |

### Playlist

- **Semua Lagu**: semua isi `~/Music`.
- **Satu playlist per sub-folder**: folder `~/Music/Semangat` otomatis menjadi playlist "Semangat".
- **Favorit**: dibuat dengan tombol `a`, disimpan di `~/.local/share/pemutar-musik/favorit.json`.

Pemutar hanya membaca folder saat dibuka, jadi buka ulang setelah menambah lagu.

## Opsional: dipasang di dashboard kitty

Tambahkan satu baris di file session kitty-mu:

```
launch --location=vsplit /home/NAMA_USER/.local/bin/musik
```

Lalu jalankan: `kitty --session ~/.config/kitty/dashboard.conf`.

Warna latar versi terminal adalah biru navy. Untuk latar transparan, ubah `TRANSPARAN = False` menjadi `True` di `terminal/musik_tui.py` (fitur ini belum diuji di semua terminal).

## Struktur proyek

```
pemutar-musik/
├── README.md
├── install.sh
├── web/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── terminal/
│   └── musik_tui.py
└── desktop/
    └── musik_gui.py
```

## Status

Dibuat dan diuji di Arch Linux (GNOME, kitty). Versi web dan desktop belum diuji secara luas. Jika menemukan masalah, silakan buka *issue*.

## Tentang lagu

Gunakan lagu milikmu sendiri atau yang berlisensi bebas (misalnya dari Jamendo, Free Music Archive, atau Internet Archive). Perhatikan lisensi tiap lagu sebelum memakainya di konten publik.
