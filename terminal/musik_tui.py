#!/usr/bin/env python3
"""Pemutar musik terminal dengan playlist. Jalankan: musik"""
import json, random, sys, time
from pathlib import Path
import mpv
from mutagen import File as MFile
from rich.text import Text
from textual.app import App
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, ProgressBar, Static

EXT = {".mp3", ".flac", ".wav", ".ogg", ".m4a", ".opus"}
FOLDER = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / "Music"
FAV_FILE = Path.home() / ".local/share/pemutar-musik/favorit.json"

# Ubah ke True kalau mau latar transparan (wallpaper kitty tembus pandang)
TRANSPARAN = False
BG = "ansi_default" if TRANSPARAN else "#050b2e"

def baca(p):
    judul, artis = p.stem, "Artis tidak diketahui"
    try:
        t = MFile(p, easy=True)
        if t:
            judul = (t.get("title") or [judul])[0]
            artis = (t.get("artist") or [artis])[0]
    except Exception:
        pass
    return {"path": p, "judul": judul, "artis": artis}

def fmt(s):
    return f"{int(s // 60)}:{int(s % 60):02d}"

class Pemutar(App):
    TITLE = "Pemutar Musik"
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    Screen {background: __BG__; color: #7fa0ff;}
    Header {background: #0f1f66; color: #9db8ff;}
    HeaderIcon {color: #4f7cff;}
    Footer {background: #0f1f66;}
    FooterKey {background: #0f1f66;}
    FooterKey .footer-key--key {color: #cfe0ff; background: #1a2f7a; text-style: bold;}
    FooterKey .footer-key--description {color: #7fa0ff;}
    #kiri {width: 45%; border-right: solid #1a2f7a;}
    #cari {margin: 1;}
    Input {background: __BG__; color: #cfe0ff; border: tall #1a2f7a;}
    Input:focus {border: tall #4f7cff;}
    Input > .input--placeholder {color: #2c4aa8;}
    ListView {background: __BG__;}
    ListItem {background: __BG__; color: #7fa0ff;}
    ListView > ListItem.-highlight {background: #1a2f7a; color: #cfe0ff;}
    #now {height: 7; content-align: center middle; text-align: center; text-style: bold; color: #4f7cff;}
    #bar {padding: 0 4;}
    Bar > .bar--bar {color: #4f7cff; background: #1a2f7a;}
    Bar > .bar--complete {color: #4f7cff;}
    #status {text-align: center; color: #5b7fd9; margin-top: 1;}
    """.replace("__BG__", BG)
    BINDINGS = [
        Binding("space", "jeda", "Putar/Jeda"), Binding("n", "next", "Next"), Binding("p", "prev", "Prev"),
        Binding("l", "playlist_next", "Playlist"), Binding("a", "fav_tambah", "+Favorit"),
        Binding("d", "fav_hapus", "-Favorit"), Binding("s", "toggle_acak", "Acak"),
        Binding("r", "toggle_ulang", "Ulang"), Binding("slash", "cari", "Cari"), Binding("q", "quit", "Keluar"),
        Binding("left", "seek(-5)", "-5s", show=False), Binding("right", "seek(5)", "+5s", show=False),
        Binding("plus", "vol(5)", "Vol+", show=False), Binding("minus", "vol(-5)", "Vol-", show=False),
    ]

    async def on_mount(self):
        self.player = mpv.MPV(video=False, idle=True, ytdl=False, input_default_bindings=False)
        self.player.volume = 80
        files = sorted(FOLDER.rglob("*")) if FOLDER.exists() else []
        self.semua = [baca(p) for p in files if p.suffix.lower() in EXT]
        try:
            self.fav = json.loads(FAV_FILE.read_text())
        except Exception:
            self.fav = []
        self.tampil, self.sumber, self.sedang = [], [], None
        self.idx, self.acak, self.ulang, self.mulai = -1, False, False, 0
        self.playlists = self.bangun_playlist()
        await self.pilih_playlist("Semua Lagu")
        self.query_one("#daftar").focus()
        self.set_interval(0.5, self.tik)
        if not self.semua:
            self.query_one("#now").update(f"Tidak ada lagu di {FOLDER}\nTaruh file MP3/FLAC di sana")

    def compose(self):
        yield Header()
        with Horizontal():
            with Vertical(id="kiri"):
                yield Input(placeholder="Cari lagu...", id="cari")
                yield ListView(id="daftar")
            with Vertical():
                yield Static("Pilih lagu lalu tekan Enter", id="now")
                yield ProgressBar(total=100, show_eta=False, show_percentage=False, id="bar")
                yield Static("", id="status")
        yield Footer()

    # ---- Playlist: "Semua Lagu", tiap sub-folder, dan "Favorit" ----
    def bangun_playlist(self):
        pl, subs = {"Semua Lagu": self.semua}, {}
        for l in self.semua:
            try:
                rel = l["path"].relative_to(FOLDER)
            except ValueError:
                continue
            if len(rel.parts) > 1:
                subs.setdefault(rel.parts[0], []).append(l)
        for n in sorted(subs):
            pl[n] = subs[n]
        peta = {str(l["path"]): l for l in self.semua}
        pl["Favorit"] = [peta[p] for p in self.fav if p in peta]
        return pl

    async def pilih_playlist(self, nama):
        self.pl_nama, self.sumber = nama, self.playlists[nama]
        self.tampil = list(self.sumber)
        self.sub_title = f"Playlist: {nama} ({len(self.sumber)} lagu)  -  tekan l untuk ganti"
        self.query_one("#cari").value = ""
        await self.isi_daftar()

    async def action_playlist_next(self):
        nama = list(self.playlists)
        await self.pilih_playlist(nama[(nama.index(self.pl_nama) + 1) % len(nama)])

    def simpan_fav(self):
        FAV_FILE.parent.mkdir(parents=True, exist_ok=True)
        FAV_FILE.write_text(json.dumps(self.fav))
        self.playlists = self.bangun_playlist()

    def terpilih(self):
        i = self.query_one("#daftar", ListView).index
        return self.tampil[i] if i is not None and 0 <= i < len(self.tampil) else None

    async def action_fav_tambah(self):
        l = self.terpilih()
        if not l:
            return
        p = str(l["path"])
        if p not in self.fav:
            self.fav.append(p)
            self.simpan_fav()
            self.notify(f"Ditambah ke Favorit: {l['judul']}")
        else:
            self.notify("Sudah ada di Favorit")

    async def action_fav_hapus(self):
        l = self.terpilih()
        if self.pl_nama != "Favorit" or not l:
            self.notify("Buka playlist Favorit (tombol l) untuk menghapus")
            return
        self.fav.remove(str(l["path"]))
        self.simpan_fav()
        await self.pilih_playlist("Favorit")

    # ---- Daftar & pencarian ----
    async def isi_daftar(self):
        lv = self.query_one("#daftar", ListView)
        await lv.clear()
        await lv.extend([ListItem(Label(f"{l['judul']} - {l['artis']}", markup=False)) for l in self.tampil])
        self.idx = self.tampil.index(self.sedang) if self.sedang in self.tampil else -1

    async def on_input_changed(self, e):
        q = e.value.lower()
        self.tampil = [l for l in self.sumber if q in (l["judul"] + l["artis"]).lower()]
        await self.isi_daftar()

    def on_input_submitted(self, e):
        self.query_one("#daftar").focus()

    def on_list_view_selected(self, e):
        self.putar(e.list_view.index)

    # ---- Pemutaran ----
    def putar(self, i):
        if not self.tampil:
            return
        self.idx = i % len(self.tampil)
        l = self.sedang = self.tampil[self.idx]
        self.player.play(str(l["path"]))
        self.player.pause = False
        self.mulai = time.monotonic()
        self.query_one("#now").update(Text(f"♪\n{l['judul']}\n{l['artis']}"))
        self.query_one("#daftar").index = self.idx

    def action_next(self):
        self.putar(random.randrange(len(self.tampil)) if self.acak and self.tampil else self.idx + 1)

    def action_prev(self):
        self.putar(self.idx - 1)

    def action_jeda(self):
        if self.idx < 0:
            self.putar(0)
        else:
            self.player.pause = not self.player.pause

    def action_toggle_acak(self):
        self.acak = not self.acak

    def action_toggle_ulang(self):
        self.ulang = not self.ulang

    def action_seek(self, d: int):
        if self.idx >= 0:
            self.player.seek(d)

    def action_vol(self, d: int):
        self.player.volume = max(0, min(100, self.player.volume + d))

    def action_cari(self):
        self.query_one("#cari").focus()

    def tik(self):
        p = self.player
        pos, dur = p.time_pos, p.duration
        if pos is not None and dur:
            self.query_one("#bar").update(progress=pos / dur * 100)
            ikon = "⏸" if p.pause else "▶"
            self.query_one("#status").update(
                f"{ikon} {fmt(pos)} / {fmt(dur)}   vol {int(p.volume)}%   "
                f"acak {'on' if self.acak else 'off'}   ulang {'on' if self.ulang else 'off'}")
        elif self.idx >= 0 and p.idle_active and time.monotonic() - self.mulai > 2:
            self.putar(self.idx) if self.ulang else self.action_next()

    def on_unmount(self):
        self.player.terminate()

if __name__ == "__main__":
    try:
        app = Pemutar(ansi_color=TRANSPARAN)
    except TypeError:
        app = Pemutar()
    app.run()
