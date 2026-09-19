from __future__ import annotations
from PySide6.QtCore import QThread, Signal
from core import download_mp3, DownloadCancelled


class DownloadWorker(QThread):
    progress = Signal(dict)      # raw yt-dlp progress dict
    finished_ok = Signal(str)    # final filepath
    failed = Signal(str)         # error message
    cancelled = Signal()

    def __init__(self, url: str, output_dir: str, quality: str):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.quality = quality
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    def _is_cancelled(self) -> bool:
        return self._cancel

    def run(self) -> None:
        try:
            path = download_mp3(
                self.url,
                self.output_dir,
                self.quality,
                on_progress=self.progress.emit,
                cancel_flag=self._is_cancelled,
            )
            self.finished_ok.emit(path)
        except DownloadCancelled:
            self.cancelled.emit()
        except Exception as e:
            self.failed.emit(str(e))