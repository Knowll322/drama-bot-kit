"""Demo offline Drama Bot — pencarian pakai data dummy + fetch nyata TVMaze (opsional).

    python demo.py           # dummy saja, aman offline
    python demo.py --live    # pakai API TVMaze beneran (butuh internet)
"""
from __future__ import annotations

import sys

from bot.tvmaze import Episode, _to_show, format_show, new_episodes_since

DUMMY = {
    "id": 1,
    "name": "Queen of Tears",
    "premiered": "2024-03-09",
    "status": "Ended",
    "rating": {"average": 8.7},
    "summary": "<p>Kisah <b>pernikahan</b> yang diuji krisis.</p>",
    "nextEpisodeAirdate": None,
}

DUMMY_EPS = [
    Episode(1, 1, "Pilot", "2026-10-01"),
    Episode(1, 2, "Cracks", "2026-10-08"),
    Episode(1, 3, "Storm", "2026-10-15"),
    Episode(1, 4, "Aftermath", "2026-11-01"),  # belum tayang (simulasi: > hari ini dianggap besok)
]


def _banner(t: str) -> None:
    print("\n" + "=" * 56)
    print(f"  {t}")
    print("=" * 56)


def demo_dummy() -> None:
    _banner("DEMO 1 — /cari (data dummy)")
    show = _to_show(DUMMY)
    print(format_show(show, with_summary=True))

    _banner("DEMO 2 — Deteksi episode baru")
    print("Semua episode:")
    for ep in DUMMY_EPS:
        print(f"  S{ep.season:02d}E{ep.number:02d} {ep.name} ({ep.airdate})")
    print("\nWatchlist last_airdate = 2026-10-01 -> episode yang harus di-notify:")

    # new_episodes_since butuh network; simulasi logikanya di sini
    from datetime import date

    today = date.today().isoformat()
    since = "2026-10-01"
    for ep in DUMMY_EPS:
        if ep.airdate and ep.airdate <= today and ep.airdate > since:
            print(f"  >>> NOTIF: {show.name} — S{ep.season:02d}E{ep.number:02d} {ep.name}")


def demo_live() -> None:
    _banner("DEMO LIVE — TVMaze API nyata")
    from bot.tvmaze import search_shows

    shows = search_shows("Queen of Tears", limit=3)
    if not shows:
        print("Tidak ada hasil.")
        return
    for s in shows:
        print()
        print(format_show(s))
    print("\nCek episode lampau show pertama...")
    try:
        eps = new_episodes_since(shows[0].id, None)
        print(f"  Total episode tayang: {len(eps)}")
        if eps:
            last = eps[-1]
            print(f"  Terbaru: S{last.season:02d}E{last.number:02d} {last.name} ({last.airdate})")
    except Exception as exc:
        print(f"  Gagal: {exc}")


if __name__ == "__main__":
    # Console Windows (cp1252) bisa crash pada nama drama berhuruf khusus
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("DRAMA BOT KIT — Demo")
    demo_dummy()
    if "--live" in sys.argv:
        demo_live()
    _banner("SELESAI")
    print("Untuk live: isi BOT_TOKEN di .env lalu python -m bot")
