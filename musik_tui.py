#!/usr/bin/env python3
"""Pemutar musik terminal. Jalankan: musik  (atau: python3 musik_tui.py ~/Music)"""
import random, sys, time
from pathlib import Path
import mpv
from mutagen import File as MFile
from rich.text import Text
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, ProgressBar, Static

EXT = {".mp3", ".flac", ".wav", ".ogg", ".m4a", ".opus"}
FOLDER = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / "Music"

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
    CSS = """
    Screen {background: #14101f; color: #efeaff;}
    #kiri {width: 45%; border-right: solid #2f2850;}
    #cari {margin: 1;}
    ListView {background: #14101f;}
    ListItem.-highlight {background: #2d2450;}
    #now {height: 7; content-align: center middle; text-align: center; text-style: bold; color: #c4b5fd;}
    #bar {padding: 0 4;}
    #status {text-align: center; color: #9a90c4; margin-top: 1;}
    """
    BINDINGS = [
        ("space", "jeda", "Putar/Jeda"), ("n", "next", "Next"), ("p", "prev", "Prev"),
        ("s", "toggle_acak", "Acak"), ("r", "toggle_ulang", "Ulang"),
        ("left", "seek(-5)", "-5s"), ("right", "seek(5)", "+5s"),
        ("plus", "vol(5)", "Vol+"), ("minus", "vol(-5)", "Vol-"),
        ("slash", "cari", "Cari"), ("q", "quit", "Keluar"),
    ]

    async def on_mount(self):
        self.player = mpv.MPV(video=False, idle=True, ytdl=False, input_default_bindings=False)
        self.player.volume = 80
        files = sorted(FOLDER.rglob("*")) if FOLDER.exists() else []
        self.semua = [baca(p) for p in files if p.suffix.lower() in EXT]
        self.tampil, self.idx, self.acak, self.ulang, self.mulai = list(self.semua), -1, False, False, 0
        await self.isi_daftar()
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

    async def isi_daftar(self):
        lv = self.query_one("#daftar", ListView)
        await lv.clear()
        await lv.extend([ListItem(Label(f"{l['judul']} - {l['artis']}", markup=False)) for l in self.tampil])

    async def on_input_changed(self, e):
        q = e.value.lower()
        self.tampil = [l for l in self.semua if q in (l["judul"] + l["artis"]).lower()]
        self.idx = -1
        await self.isi_daftar()

    def on_input_submitted(self, e):
        self.query_one("#daftar").focus()

    def on_list_view_selected(self, e):
        self.putar(e.list_view.index)

    def putar(self, i):
        if not self.tampil:
            return
        self.idx = i % len(self.tampil)
        l = self.tampil[self.idx]
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
    Pemutar().run()
