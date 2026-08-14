"""
Cross-platform "open in browser" helpers.

Handles the quirks of each environment:
- Windows / Linux / macOS -> stdlib `webbrowser`
- Termux (Android)        -> `termux-open-url` (webbrowser is unreliable there)
- iOS (Pythonista/a-Shell) -> `webbrowser` generally works; we still fall
                               back to printing the URL if nothing succeeds
                               so the user can tap/copy it manually.
"""

from __future__ import annotations
import os
import shutil
import subprocess
import webbrowser

# The two destinations every command offers at the end of its run.
SITES = {
    "1": ("Abhidhamma Teachings", "https://abhidhamma.ishanoshada.com/"),
    "2": ("Lahari Mantras", "https://lahari-mantras.ishanoshada.com/"),
}


def is_termux() -> bool:
    return "com.termux" in os.environ.get("PREFIX", "") or shutil.which(
        "termux-open-url"
    ) is not None


def open_url(url: str) -> bool:
    """Try every strategy available on this platform. Returns True on success."""
    # 1. Termux has its own opener that hands off to the Android intent system.
    if is_termux():
        try:
            subprocess.run(["termux-open-url", url], check=False)
            return True
        except Exception:
            pass

    # 2. Standard library - works on Windows, macOS, Linux, and most iOS
    #    terminal apps that register a URL handler.
    try:
        if webbrowser.open(url, new=2):
            return True
    except Exception:
        pass

    # 3. Last resort: OS-level open commands.
    try:
        if os.name == "nt":
            os.startfile(url)  # type: ignore[attr-defined]
            return True
        elif shutil.which("open"):  # macOS / iOS shells that expose `open`
            subprocess.run(["open", url], check=False)
            return True
        elif shutil.which("xdg-open"):  # Linux
            subprocess.run(["xdg-open", url], check=False)
            return True
    except Exception:
        pass

    return False
