from __future__ import annotations
import os
from PySide6.QtCore import Qt, QSettings, QRect, QUrl
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QProgressBar, QFileDialog, QMessageBox,
)
from PySide6.QtGui import QIcon, QPainter, QColor, QPixmap, QDesktopServices

from worker import DownloadWorker

APP_NAME = "KATA-Downloader"
DEFAULT_DIR = os.path.expanduser("~/Music")

# --- Paths -----------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# --- Palette (Neo-brutalist / Retro Mac B&W) -------------------------------
BG_GREY   = "#e5e5e5"
BLACK     = "#000000"
WHITE     = "#ffffff"
DITHER_BG = "#cccccc"

# --- Stylesheet ------------------------------------------------------------
NEO_QSS = f"""
QWidget {{
    background-color: {BG_GREY};
    color: {BLACK};
    font-family: "Inter", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 13px;
    font-weight: 700;
}}

QLabel {{ background: transparent; }}

QLineEdit, QComboBox {{
    background-color: {WHITE};
    border: 2px solid {BLACK};
    padding: 6px 8px;
    selection-background-color: {BLACK};
    selection-color: {WHITE};
}}

QComboBox::drop-down {{ border-left: 2px solid {BLACK}; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {WHITE}; border: 2px solid {BLACK};
    selection-background-color: {BLACK}; selection-color: {WHITE};
    outline: none;
}}

QPushButton {{
    background-color: {WHITE}; color: {BLACK};
    border: 2px solid {BLACK}; border-right: 4px solid {BLACK}; border-bottom: 4px solid {BLACK};
    padding: 8px 16px; font-weight: 900;
}}

QPushButton:hover {{ background-color: {BG_GREY}; }}

QPushButton:pressed {{
    border-right: 2px solid {BLACK}; border-bottom: 2px solid {BLACK};
    padding: 10px 14px 6px 18px; 
}}

QPushButton:disabled {{ background-color: {DITHER_BG}; color: #666666; border-color: #666666; }}
QMessageBox {{ background: {BG_GREY}; }}
QMessageBox QPushButton {{ min-width: 70px; }}
QStatusBar {{ background: {BG_GREY}; }}
"""

class PixelProgressBar(QProgressBar):
    SEGMENT_PX = 6
    BORDER_PX = 2

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)

        r = self.rect()
        inner = r.adjusted(self.BORDER_PX, self.BORDER_PX, -self.BORDER_PX, -self.BORDER_PX)
        if inner.width() <= 0 or inner.height() <= 0:
            return

        p.fillRect(inner, QColor(BG_GREY))
        self._checker(p, inner, QColor(DITHER_BG), offset=0)

        rng = self.maximum() - self.minimum()
        frac = 0.0 if rng <= 0 else (self.value() - self.minimum()) / rng
        frac = max(0.0, min(1.0, frac))
        fill_w = int(inner.width() * frac)
        if fill_w > 0:
            fill = QRect(inner.left(), inner.top(), fill_w, inner.height())
            p.fillRect(fill, QColor(BLACK))
            self._checker(p, fill, QColor(WHITE), offset=self.SEGMENT_PX)

        pen = p.pen()
        pen.setColor(QColor(BLACK))
        pen.setWidth(self.BORDER_PX)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        half = self.BORDER_PX // 2
        p.drawRect(r.adjusted(half, half, -half - 1, -half - 1))

    @staticmethod
    def _checker(p: QPainter, rect: QRect, color: QColor, offset: int = 0):
        p.fillRect(rect, p.background().color() if False else Qt.transparent)
        seg = PixelProgressBar.SEGMENT_PX
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        y = rect.top()
        row = 0
        while y < rect.bottom():
            x = rect.left() + (offset if row % 2 else 0)
            while x < rect.right():
                w = min(seg, rect.right() - x + 1)
                h = min(seg, rect.bottom() - y + 1)
                if w > 0 and h > 0:
                    p.drawRect(x, y, w, h)
                x += seg * 2
            y += seg
            row += 1

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KATA-MP3")
        self.setFixedSize(500, 660)
        self.setStyleSheet(NEO_QSS)
        
        window_icon_path = os.path.join(ASSETS_DIR, "icon.png")
        if os.path.exists(window_icon_path):
            self.setWindowIcon(QIcon(window_icon_path))

        self.settings = QSettings(APP_NAME, APP_NAME)
        self.worker: DownloadWorker | None = None

        self._build_ui()
        self._restore_settings()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(54, 54)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet(
            f"border: 2px solid {BLACK}; border-right: 4px solid {BLACK}; border-bottom: 4px solid {BLACK}; background:{WHITE};"
        )
        
        ui_icon_path = os.path.join(ASSETS_DIR, "icon-2.png")
        if os.path.exists(ui_icon_path):
            pixmap = QPixmap(ui_icon_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)

        title = QLabel("KATA-MP3")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: 20px; font-weight: 900; letter-spacing: 1px;"
            f"border: 2px solid {BLACK}; border-right: 4px solid {BLACK}; border-bottom: 4px solid {BLACK}; background:{WHITE}; padding: 12px;"
        )
        
        title_row.addWidget(self.icon_label)
        title_row.addWidget(title, stretch=1)
        layout.addLayout(title_row)
        layout.addSpacing(10)

        layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel("OUTPUT FOLDER:"))
        folder_row = QHBoxLayout()
        folder_row.setSpacing(12)
        
        self.folder_input = QLineEdit()
        browse_btn = QPushButton("BROWSE…")
        browse_btn.clicked.connect(self._pick_folder)
        self.open_btn = QPushButton("OPEN FOLDER")
        self.open_btn.clicked.connect(self._open_folder)
        
        folder_row.addWidget(self.folder_input)
        folder_row.addWidget(browse_btn)
        folder_row.addWidget(self.open_btn)
        layout.addLayout(folder_row)

        layout.addWidget(QLabel("QUALITY (KBPS):"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["128", "192", "256", "320"])
        self.quality_combo.setCurrentText("192")
        layout.addWidget(self.quality_combo)

        layout.addSpacing(10)
        self.progress = PixelProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(30)
        layout.addWidget(self.progress)

        self.status_label = QLabel("IDLE")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"border: 2px solid {BLACK}; background: {WHITE}; padding: 8px;")
        layout.addWidget(self.status_label)

        layout.addSpacing(10)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        
        self.download_btn = QPushButton("DOWNLOAD")
        self.download_btn.clicked.connect(self._start_download)
        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.clicked.connect(self._cancel_download)
        self.cancel_btn.setEnabled(False)
        
        btn_row.addWidget(self.download_btn)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)
        layout.addStretch(1)

    def _restore_settings(self):
        self.folder_input.setText(self.settings.value("output_dir", DEFAULT_DIR, str))
        self.quality_combo.setCurrentText(self.settings.value("quality", "192", str))

    def _save_settings(self):
        self.settings.setValue("output_dir", self.folder_input.text())
        self.settings.setValue("quality", self.quality_combo.currentText())

    def closeEvent(self, event):
        self._save_settings()
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(3000)
        super().closeEvent(event)

    def _pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "CHOOSE OUTPUT FOLDER", self.folder_input.text() or DEFAULT_DIR)
        if folder:
            self.folder_input.setText(folder)

    def _open_folder(self):
        path = self.folder_input.text() or DEFAULT_DIR
        if os.path.isdir(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.warning(self, "NOT FOUND", f"FOLDER DOESN'T EXIST:\n{path}")

    def _start_download(self):
        url = self.url_input.text().strip()
        out_dir = self.folder_input.text().strip() or DEFAULT_DIR
        quality = self.quality_combo.currentText()

        if not url:
            QMessageBox.warning(self, "MISSING URL", "PASTE A YOUTUBE URL FIRST.")
            return

        self.progress.setValue(0)
        self.status_label.setText("STARTING…")
        self._set_busy(True)

        self.worker = DownloadWorker(url, out_dir, quality)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.cancelled.connect(self._on_cancelled)
        self.worker.start()

    def _cancel_download(self):
        if self.worker and self.worker.isRunning():
            self.status_label.setText("CANCELLING…")
            self.worker.cancel()

    def _set_busy(self, busy: bool):
        self.download_btn.setEnabled(not busy)
        self.cancel_btn.setEnabled(busy)
        self.url_input.setEnabled(not busy)

    def _on_progress(self, d: dict):
        if d.get("status") != "downloading":
            return
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        done = d.get("downloaded_bytes", 0)
        pct = int(done / total * 100) if total else 0
        self.progress.setValue(pct)

        speed = d.get("speed") or 0
        eta = d.get("eta") or 0
        speed_mb = speed / 1024 / 1024
        self.status_label.setText(f"{pct}%  •  {speed_mb:.2f} MB/S  •  ETA {eta}S")

    def _on_finished(self, path: str):
        self.progress.setValue(100)
        self.status_label.setText("DONE")
        self._set_busy(False)
        QMessageBox.information(self, "DOWNLOAD COMPLETE", f"SAVED:\n{path}")

    def _on_failed(self, msg: str):
        self.status_label.setText("FAILED")
        self._set_busy(False)
        QMessageBox.critical(self, "DOWNLOAD FAILED", msg)

    def _on_cancelled(self):
        self.status_label.setText("CANCELLED")
        self.progress.setValue(0)
        self._set_busy(False)