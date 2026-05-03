from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from threading import Lock
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


@dataclass
class WatchState:
    running: bool = False
    folder: Optional[str] = None
    debounce_seconds: float = 2.0
    events_seen: int = 0
    ingests_triggered: int = 0
    last_event_at: Optional[float] = None
    last_ingest_at: Optional[float] = None


class _Handler(FileSystemEventHandler):
    def __init__(self, manager: 'IngestWatchManager'):
        self.manager = manager

    def on_any_event(self, event):
        if event.is_directory:
            return
        self.manager._on_fs_event()


class IngestWatchManager:
    def __init__(self, ingest_callback):
        self._observer: Optional[Observer] = None
        self._lock = Lock()
        self.state = WatchState()
        self.ingest_callback = ingest_callback

    def start(self, folder: str, debounce_seconds: float = 2.0) -> Dict[str, Any]:
        p = Path(folder).expanduser().resolve()
        if not p.exists() or not p.is_dir():
            raise FileNotFoundError(f"Folder not found: {p}")

        with self._lock:
            if self._observer:
                self.stop()
            self.state = WatchState(running=True, folder=str(p), debounce_seconds=float(debounce_seconds))
            self._observer = Observer()
            self._observer.schedule(_Handler(self), str(p), recursive=True)
            self._observer.start()
        return self.status()

    def stop(self) -> Dict[str, Any]:
        with self._lock:
            if self._observer:
                self._observer.stop()
                self._observer.join(timeout=3)
                self._observer = None
            self.state.running = False
        return self.status()

    def status(self) -> Dict[str, Any]:
        s = self.state
        return {
            "running": s.running,
            "folder": s.folder,
            "debounce_seconds": s.debounce_seconds,
            "events_seen": s.events_seen,
            "ingests_triggered": s.ingests_triggered,
            "last_event_at": s.last_event_at,
            "last_ingest_at": s.last_ingest_at,
        }

    def _on_fs_event(self):
        with self._lock:
            now = time.time()
            self.state.events_seen += 1
            self.state.last_event_at = now
            if self.state.last_ingest_at and (now - self.state.last_ingest_at) < self.state.debounce_seconds:
                return
            folder = self.state.folder
            self.state.last_ingest_at = now
            self.state.ingests_triggered += 1

        if folder:
            self.ingest_callback(folder, watch_triggered=True)
