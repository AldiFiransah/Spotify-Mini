#!/usr/bin/env python3
"""Pemutar musik desktop (Qt). Jalankan: python3 musik_gui.py"""
import locale, random, sys
from pathlib import Path
from mutagen import File as MFile
from PyQt6.QtCore import QSettings, Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QListWidgetItem, QMainWindow, QPushButton, QSlider, QStyle, QVBoxLayout, QWidget)

EXT = {".mp3", ".flac", ".wav", ".ogg", ".m4a", ".opus"}
CSS = """
QMainWindow, QWidget#root {background:#14101f;}
QWidget {color:#efeaff; font-size:13px;}
#kiri {background:#1b1630; border-right:1px solid #2f2850;}
QLineEdit {background:#14101f; border:1px solid #2f2850; border-radius:8px; padding:8px;}
QListWidget {background:transparent; border:0; outline:0;}
QListWidget::item {padding:6px; border-radius:8px;}
QListWidget::item:hover {background:#262040;}
QListWidget::item:selected {background:#3b2d6b; color:#fff;}
QPushButton {background:#2d2450; border:0; border-radius:8px; padding:8px 14px;}
QPushButton:hover {background:#3b2d6b;}
QPushButton:checked {background:#8b5cf6; color:#1b1630;}
#pilih {background:#8b5cf6; color:#1b1630; font-weight:600;}
#play {background:#a78bfa; border-radius:24px; min-width:48px; max-width:48px; min-height:48px; max-height:48px;}
#judul {font-size:24px; font-weight:600;}
#artis {color:#a79ccf; font-size:15px;}
#bawah {background:#1b1630; border-top:1px solid #2f2850;}
QSlider::groove:horizontal {height:4px; background:#2f2850; border-radius:2px;}
QSlider::sub-page:horizontal {background:#a78bfa; border-radius:2px;}
QSlider::handle:horizontal {background:#ddd6fe; width:12px; height:12px; margin:-4px 0; border-radius:6px;}
"""

def fmt(s):
    return f"{int(s // 60)}:{int(s % 60):02d}"

def baca(p):
    d = {"path": p, "judul": p.stem, "artis": "Artis tidak diketahui", "cover": None}
    try:
        e = MFile(p, easy=True)
        if e:
            d["judul"] = (e.get("title") or [d["judul"]])[0]
            d["artis"] = (e.get("artist") or [d["artis"]])[0]
        t = MFile(p)
        data = None
        if t is not None:
            if getattr(t, "pictures", None):
                data = t.pictures[0].data
            elif t.tags:
                for k in t.tags.keys():
                    if str(k).startswith("APIC"):
                        data = t.tags[k].data
                        break
                if data is None and "covr" in t.tags:
                    data = bytes(t.tags["covr"][0])
        if data:
            pm = QPixmap()
            if pm.loadFromData(data):
                d["cover"] = pm.scaled(420, 420, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    except Exception:
        pass
    return d

class Pemutar(QMainWindow):
    def __init__(self):
        super().__init__()
        import mpv
        self.player = mpv.MPV(video=False, idle=True, ytdl=False, input_default_bindings=False)
        self.player.volume = 80
        self.set = QSettings("pemutar-musik", "pemutar-musik")
        self.semua, self.tampil, self.idx, self.mulai = [], [], -1, 0
        self.default = self.bikin_default()
        self.setWindowTitle("Pemutar Musik")
        self.resize(1000, 640)

        root = QWidget(objectName="root")
        self.setCentralWidget(root)
        utama = QVBoxLayout(root)
        utama.setContentsMargins(0, 0, 0, 0)
        utama.setSpacing(0)
        atas = QHBoxLayout()
        atas.setSpacing(0)
        utama.addLayout(atas, 1)

        kiri = QWidget(objectName="kiri")
        kiri.setFixedWidth(340)
        kl = QVBoxLayout(kiri)
        self.pilih = QPushButton("Pilih folder musik", objectName="pilih")
        self.pilih.clicked.connect(self.pilih_folder)
        self.cari = QLineEdit(placeholderText="Cari lagu... (Enter untuk selesai)")
        self.cari.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.cari.textChanged.connect(self.isi_daftar)
        self.cari.returnPressed.connect(self.cari.clearFocus)
        self.daftar = QListWidget()
        self.daftar.setIconSize(self.default.size() / 5)
        self.daftar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.daftar.itemClicked.connect(lambda it: self.putar(self.daftar.row(it)))
        for w in (self.pilih, self.cari, self.daftar):
            kl.addWidget(w)
        atas.addWidget(kiri)

        kanan = QVBoxLayout()
        kanan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.cover.setPixmap(self.default)
        self.judul = QLabel("Belum ada lagu", objectName="judul", alignment=Qt.AlignmentFlag.AlignCenter)
        self.artis = QLabel("Pilih folder musik untuk mulai", objectName="artis", alignment=Qt.AlignmentFlag.AlignCenter)
        for w in (self.cover, self.judul, self.artis):
            kanan.addWidget(w)
        atas.addLayout(kanan, 1)

        bawah = QWidget(objectName="bawah")
        bl = QVBoxLayout(bawah)
        ctrl = QHBoxLayout()
        ctrl.addStretch()
        st = self.style().StandardPixmap
        self.b_acak = QPushButton("Acak", checkable=True)
        self.b_prev = QPushButton(icon=self.style().standardIcon(st.SP_MediaSkipBackward))
        self.b_play = QPushButton(objectName="play", icon=self.style().standardIcon(st.SP_MediaPlay))
        self.b_next = QPushButton(icon=self.style().standardIcon(st.SP_MediaSkipForward))
        self.b_ulang = QPushButton("Ulang", checkable=True)
        for b in (self.b_acak, self.b_prev, self.b_play, self.b_next, self.b_ulang):
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            ctrl.addWidget(b)
        ctrl.addStretch()
        bl.addLayout(ctrl)
        bar = QHBoxLayout()
        self.t_now, self.t_dur = QLabel("0:00"), QLabel("0:00")
        self.seek = QSlider(Qt.Orientation.Horizontal, maximum=1000)
        self.vol = QSlider(Qt.Orientation.Horizontal, maximum=100, value=80)
        self.vol.setFixedWidth(110)
        for w in (self.t_now, self.seek, self.t_dur, QLabel("Vol"), self.vol):
            bar.addWidget(w)
        bl.addLayout(bar)
        utama.addWidget(bawah)

        self.b_play.clicked.connect(self.jeda)
        self.b_next.clicked.connect(self.next)
        self.b_prev.clicked.connect(lambda: self.putar(self.idx - 1))
        self.seek.sliderReleased.connect(self.geser)
        self.vol.valueChanged.connect(lambda v: setattr(self.player, "volume", v))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tik)
        self.timer.start(300)

        folder = self.set.value("folder", str(Path.home() / "Music"))
        if Path(folder).exists():
            self.muat(Path(folder))

    def bikin_default(self):
        pm = QPixmap(420, 420)
        pm.fill(Qt.GlobalColor.transparent)
        from PyQt6.QtGui import QColor, QFont, QPainter
        p = QPainter(pm)
        p.setBrush(QColor("#2d2450"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, 420, 420, 24, 24)
        p.setPen(QColor("#a78bfa"))
        p.setFont(QFont("sans", 150))
        p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "♪")
        p.end()
        return pm

    def pilih_folder(self):
        f = QFileDialog.getExistingDirectory(self, "Pilih folder musik", str(Path.home() / "Music"))
        if f:
            self.set.setValue("folder", f)
            self.muat(Path(f))

    def muat(self, folder):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        files = sorted(p for p in folder.rglob("*") if p.suffix.lower() in EXT)
        self.semua = [baca(p) for p in files]
        QApplication.restoreOverrideCursor()
        self.idx = -1
        self.isi_daftar()
        if not self.semua:
            self.judul.setText("Tidak ada lagu ditemukan")
            self.artis.setText(f"Taruh file MP3/FLAC di {folder}")

    def isi_daftar(self):
        q = self.cari.text().lower()
        self.tampil = [l for l in self.semua if q in (l["judul"] + l["artis"]).lower()]
        self.daftar.clear()
        for l in self.tampil:
            it = QListWidgetItem(QIcon(l["cover"] or self.default), f"{l['judul']}\n{l['artis']}")
            self.daftar.addItem(it)

    def putar(self, i):
        if not self.tampil:
            return
        self.idx = i % len(self.tampil)
        l = self.tampil[self.idx]
        self.player.play(str(l["path"]))
        self.player.pause = False
        self.cnt = 0
        self.judul.setText(l["judul"])
        self.artis.setText(l["artis"])
        self.cover.setPixmap(l["cover"] or self.default)
        self.setWindowTitle(f"{l['judul']} · Pemutar Musik")
        self.daftar.setCurrentRow(self.idx)

    def next(self):
        if self.b_acak.isChecked() and self.tampil:
            self.putar(random.randrange(len(self.tampil)))
        else:
            self.putar(self.idx + 1)

    def jeda(self):
        if self.idx < 0:
            self.putar(0)
        else:
            self.player.pause = not self.player.pause

    def geser(self):
        d = self.player.duration
        if d:
            self.player.seek(self.seek.value() / 1000 * d, reference="absolute")

    def tik(self):
        p = self.player
        pos, dur = p.time_pos, p.duration
        st = self.style().StandardPixmap
        self.b_play.setIcon(self.style().standardIcon(st.SP_MediaPlay if (p.pause or self.idx < 0) else st.SP_MediaPause))
        if pos is not None and dur:
            self.t_now.setText(fmt(pos))
            self.t_dur.setText(fmt(dur))
            if not self.seek.isSliderDown():
                self.seek.setValue(int(pos / dur * 1000))
        elif self.idx >= 0 and p.idle_active:
            self.cnt = getattr(self, "cnt", 0) + 1
            if self.cnt > 6:
                self.putar(self.idx) if self.b_ulang.isChecked() else self.next()

    def keyPressEvent(self, e):
        k = e.key()
        K = Qt.Key
        if k == K.Key_Space: self.jeda()
        elif k == K.Key_N: self.next()
        elif k == K.Key_P: self.putar(self.idx - 1)
        elif k == K.Key_S: self.b_acak.toggle()
        elif k == K.Key_R: self.b_ulang.toggle()
        elif k == K.Key_Right and self.idx >= 0: self.player.seek(5)
        elif k == K.Key_Left and self.idx >= 0: self.player.seek(-5)
        else: super().keyPressEvent(e)

    def closeEvent(self, e):
        self.player.terminate()
        super().closeEvent(e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    locale.setlocale(locale.LC_NUMERIC, "C")  # wajib agar libmpv tidak crash bersama Qt
    app.setStyleSheet(CSS)
    w = Pemutar()
    w.show()
    sys.exit(app.exec())
