"""Test store watchlist — JSON lokal, tanpa network."""
from bot.store import WatchlistStore


def test_add_and_list(tmp_path):
    store = WatchlistStore(tmp_path)
    assert store.add(1, 100, "Drama A") is True
    assert store.add(1, 100, "Drama A") is False  # duplikat
    data = store.list_shows(1)
    assert "100" in data and data["100"]["name"] == "Drama A"


def test_remove(tmp_path):
    store = WatchlistStore(tmp_path)
    store.add(1, 100, "Drama A")
    assert store.remove(1, 100) is True
    assert store.remove(1, 100) is False
    assert store.list_shows(1) == {}


def test_set_last_airdate(tmp_path):
    store = WatchlistStore(tmp_path)
    store.add(1, 100, "Drama A")
    store.set_last_airdate(1, 100, "2026-10-01")
    assert store.list_shows(1)["100"]["last_airdate"] == "2026-10-01"


def test_all_subscribers(tmp_path):
    store = WatchlistStore(tmp_path)
    store.add(1, 100, "A")
    store.add(2, 200, "B")
    store.add(2, 201, "C")
    subs = store.all_subscribers()
    assert set(subs) == {1, 2}
    assert len(subs[2]) == 2


def test_corrupt_file(tmp_path):
    store = WatchlistStore(tmp_path)
    (tmp_path / "9.json").write_text("{broken", encoding="utf-8")
    assert store.list_shows(9) == {}
