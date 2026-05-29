from __future__ import annotations

from dataclasses import dataclass, field
import sys
import time


@dataclass
class ProgressBar:
    total: int
    label: str = "progress"
    width: int = 28
    stream: object = field(default_factory=lambda: sys.stdout)
    started_at: float = field(default_factory=time.monotonic)
    last_len: int = 0

    def update(self, done: int, *, current: str = "", extra: str = "") -> None:
        done = max(0, min(done, self.total))
        pct = (done / self.total) if self.total else 1.0
        filled = int(self.width * pct)
        bar = "#" * filled + "-" * (self.width - filled)
        elapsed = time.monotonic() - self.started_at
        eta = _format_seconds((elapsed / done) * (self.total - done)) if done else "?"
        message = (
            f"\r{self.label} [{bar}] {done}/{self.total} "
            f"{pct * 100:5.1f}% elapsed {_format_seconds(elapsed)} ETA {eta}"
        )
        if current:
            message += f" | {current[:70]}"
        if extra:
            message += f" | {extra}"
        padding = " " * max(0, self.last_len - len(message))
        self.stream.write(message + padding)
        self.stream.flush()
        self.last_len = len(message)

    def finish(self, *, message: str = "done") -> None:
        self.update(self.total, extra=message)
        self.stream.write("\n")
        self.stream.flush()

    def newline(self) -> None:
        self.stream.write("\n")
        self.stream.flush()
        self.last_len = 0


def _format_seconds(seconds: float) -> str:
    if seconds < 0 or seconds == float("inf"):
        return "?"
    seconds = int(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h{minutes:02d}m"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"
