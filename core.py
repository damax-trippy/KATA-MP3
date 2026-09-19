from __future__ import annotations
import os
from typing import Callable, Optional
import yt_dlp


class DownloadCancelled(Exception):
    pass


def download_mp3(
    url: str,
    output_dir: str,
    quality: str = "192",
    on_progress: Optional[Callable[[dict], None]] = None,
    cancel_flag: Optional[Callable[[], bool]] = None,
) -> str:
    """
    Download a single URL as MP3.

    on_progress: called with the yt-dlp progress dict.
    cancel_flag: callable returning True to abort.
    Returns the final filepath.
    """
    os.makedirs(output_dir, exist_ok=True)

    def hook(d: dict) -> None:
        if cancel_flag and cancel_flag():
            raise DownloadCancelled("Cancelled by user")
        if on_progress:
            on_progress(d)

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            },
            {"key": "FFmpegMetadata"},
        ],
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "progress_hooks": [hook],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        final_path = ydl.prepare_filename(info)
        # yt-dlp's prepare_filename returns the pre-postprocess extension
        base, _ = os.path.splitext(final_path)
        return base + ".mp3"