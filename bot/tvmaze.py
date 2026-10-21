"""Klien TVMaze — API publik gratis, tanpa API key.

https://www.tvmaze.com/api — metadata acara TV termasuk jadwal episode.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import requests

BASE = "https://api.tvmaze.com"
TIMEOUT = 15.0


@dataclass(frozen=True)
class Show:
    id: int
    name: str
    year: str
    status: str
    rating: str
    summary: str  # plain text, tag HTML sudah dibersihkan
    next_airdate: str | None  # ISO date atau None


@dataclass(frozen=True)
class Episode:
    season: int
    number: int
    name: str
    airdate: str | None


def _strip_html(raw: str | None) -> str:
    if not raw:
        return ""
    import re

    text = re.sub(r"<[^>]+>", " ", raw)
    return " ".join(text.split())


def _to_show(data: dict[str, Any]) -> Show:
    rating = (data.get("rating") or {}).get("average")
    air = data.get("nextEpisodeAirdate")
    return Show(
        id=int(data["id"]),
        name=str(data.get("name", "?")),
        year=str(((data.get("premiered") or "")[:4]) or "?"),
        status=str(data.get("status", "?")),
        rating=str(rating) if rating else "-",
        summary=_strip_html(data.get("summary"))[:400],
        next_airdate=air if isinstance(air, str) else None,
    )


def search_shows(query: str, limit: int = 5) -> list[Show]:
    """Cari acara. Return maksimal `limit` hasil terbaik (skor TVMaze)."""
    resp = requests.get(f"{BASE}/search/shows", params={"q": query}, timeout=TIMEOUT)
    resp.raise_for_status()
    results = resp.json() or []
    shows = [_to_show(item["show"]) for item in results if item.get("show")]
    return shows[:limit]


def get_show(show_id: int) -> Show | None:
    resp = requests.get(f"{BASE}/shows/{show_id}", timeout=TIMEOUT)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return _to_show(resp.json())


def get_episodes(show_id: int) -> list[Episode]:
    resp = requests.get(f"{BASE}/shows/{show_id}/episodes", timeout=TIMEOUT)
    resp.raise_for_status()
    eps = []
    for e in resp.json() or []:
        eps.append(
            Episode(
                season=int(e.get("season") or 0),
                number=int(e.get("number") or 0),
                name=str(e.get("name") or "TBA"),
                airdate=e.get("airdate"),
            )
        )
    return eps


def new_episodes_since(show_id: int, since: str | None) -> list[Episode]:
    """Episode yang sudah tayang SETELAH tanggal `since` (ISO, bisa None = semua lampau)."""
    today = date.today().isoformat()
    out = []
    for ep in get_episodes(show_id):
        if not ep.airdate or ep.airdate > today:
            continue  # belum tayang
        if since is None or ep.airdate > since:
            out.append(ep)
    return out


def format_show(show: Show, with_summary: bool = False) -> str:
    lines = [
        f"{show.name} ({show.year})",
        f"Status: {show.status} | Rating: {show.rating}/10",
    ]
    if show.next_airdate:
        lines.append(f"Episode berikutnya: {show.next_airdate}")
    if with_summary and show.summary:
        lines.append(f"\n{show.summary}")
    lines.append(f"ID: {show.id} — /ikuti {show.id} untuk notifikasi episode baru")
    return "\n".join(lines)
