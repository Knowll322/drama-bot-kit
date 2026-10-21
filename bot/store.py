"""Watchlist per chat: file JSON per chat_id di folder data/.

Struktur: { "<show_id>": {"name": str, "last_airdate": str|None} }
`last_airdate` = tanggal episode terakhir yang sudah pernah di-notify.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class WatchlistStore:
    def __init__(self, data_dir: str | Path = "data"):
        self._dir = Path(data_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, chat_id: int) -> Path:
        return self._dir / f"{chat_id}.json"

    def load(self, chat_id: int) -> dict[str, Any]:
        path = self._path(chat_id)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning("Watchlist rusak, mulai kosong: %s", path)
            return {}

    def save(self, chat_id: int, data: dict[str, Any]) -> None:
        path = self._path(chat_id)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)

    def add(self, chat_id: int, show_id: int, name: str, last_airdate: str | None = None) -> bool:
        """Tambah show. Return False kalau sudah ada."""
        data = self.load(chat_id)
        key = str(show_id)
        if key in data:
            return False
        data[key] = {"name": name, "last_airdate": last_airdate}
        self.save(chat_id, data)
        return True

    def remove(self, chat_id: int, show_id: int) -> bool:
        data = self.load(chat_id)
        if str(show_id) not in data:
            return False
        del data[str(show_id)]
        self.save(chat_id, data)
        return True

    def list_shows(self, chat_id: int) -> dict[str, Any]:
        return self.load(chat_id)

    def set_last_airdate(self, chat_id: int, show_id: int, airdate: str) -> None:
        data = self.load(chat_id)
        key = str(show_id)
        if key in data:
            data[key]["last_airdate"] = airdate
            self.save(chat_id, data)

    def all_subscribers(self) -> dict[int, dict[str, Any]]:
        """Semua chat yang punya watchlist — untuk job pengecekan periodik."""
        out: dict[int, dict[str, Any]] = {}
        for path in self._dir.glob("*.json"):
            try:
                chat_id = int(path.stem)
            except ValueError:
                continue
            data = self.load(chat_id)
            if data:
                out[chat_id] = data
        return out
