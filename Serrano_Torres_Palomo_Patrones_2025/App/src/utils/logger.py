"""Redirect all stdout writes to a file named `game.log` at the project root (App/)
and prefix each logged line with a timestamp.

Usage:
    from stdout_redirect import redirect_stdout_to_game_log
    redirect_stdout_to_game_log()

This module replaces ``sys.stdout`` with a small file-like object that appends
timestamped lines to the ``game.log`` file and flushes immediately. A restore
function is provided for tests or graceful shutdowns.
"""
from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime


class _StdoutFile:
    """A minimal file-like wrapper that writes timestamped lines to the given path.

    Behavior:
    - Writes are buffered until a newline is seen; completed lines are prefixed
      with a timestamp like: [YYYY-mm-dd HH:MM:SS.sss] <text>\n
    - If flush() is called and there is a partial line pending, the partial
      content is written out with a timestamp as a final fragment.

    - Thread-safe for concurrent writes.
    """

    def __init__(self, path: str) -> None:
        self._path = Path(path)
        # ensure parent exists (path may be <repo-root>/logs/game.log)
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        # open in append mode, use utf-8 encoding; small buffering (line-buffer)
        try:
            self._file = open(self._path, "a", encoding="utf-8", buffering=1)
        except Exception:
            # fallback to devnull file-like object to avoid breaking app
            import io

            self._file = io.TextIOWrapper(open(sys.devnull, "wb"), encoding="utf-8")
        self._lock = threading.Lock()
        self._buffer = ""  # hold incomplete line fragments

    def _now_ts(self) -> str:
        # timestamp with milliseconds
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def _write_line(self, line: str) -> None:
        # line already includes its terminating newline if it was present
        ts = self._now_ts()
        try:
            self._file.write(f"[{ts}] {line}")
            self._file.flush()
        except Exception:
            # swallow errors to avoid crashing the app due to logging failure
            pass

    def write(self, s: str) -> None:
        if not s:
            return
        with self._lock:
            try:
                self._buffer += s
                # process any complete lines in the buffer
                while True:
                    if "\n" in self._buffer:
                        line, rest = self._buffer.split("\n", 1)
                        # write the line with the newline restored
                        self._write_line(line + "\n")
                        self._buffer = rest
                    else:
                        break
            except Exception:
                pass

    def flush(self) -> None:
        with self._lock:
            try:
                # If there's a partial line, write it out as-is with a timestamp
                if self._buffer:
                    # do not add an extra newline here; keep it as fragment
                    self._write_line(self._buffer)
                    self._buffer = ""
                self._file.flush()
            except Exception:
                pass

    def close(self) -> None:
        with self._lock:
            try:
                # flush any pending buffer before closing
                if self._buffer:
                    self._write_line(self._buffer)
                    self._buffer = ""
                self._file.close()
            except Exception:
                pass

    @property
    def path(self) -> Path:
        return self._path


# Keep references so we can restore stdout later if needed
_original_stdout = sys.stdout
_redirect_instance: Optional[_StdoutFile] = None


def redirect_stdout_to_game_log() -> Path:
    """Redirect sys.stdout to `<project_root>/game.log` and return the log path.

    The log file is created inside the `App/` folder under `App/logs/game.log`.
    This module lives in `App/src/...`, so the App directory is two parents up
    (parents[2]). Using that keeps logs scoped to the game's App folder.
    Calling this function multiple times has no additional effect.
    """

    global _redirect_instance, _original_stdout
    if _redirect_instance is not None:
        return _redirect_instance.path

    # Resolve App root. File lives in App/src/utils/logger.py so parents[2]
    # is the App directory. Place logs at App/logs/game.log.
    project_root = Path(__file__).resolve().parents[2]
    log_path = project_root / "logs" / "game.log"

    # ensure logs directory exists
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        # ignore directory creation errors; _StdoutFile will also handle failures
        pass

    _redirect_instance = _StdoutFile(str(log_path))
    sys.stdout = _redirect_instance
    return log_path


def restore_stdout() -> None:
    """Restore the original sys.stdout and close the log file (if any).

    Safe to call multiple times.
    """

    global _redirect_instance, _original_stdout
    if _redirect_instance is None:
        return
    try:
        _redirect_instance.close()
    finally:
        sys.stdout = _original_stdout
        _redirect_instance = None
