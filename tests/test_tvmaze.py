"""Test parsing/format TVMaze — data dummy, tanpa network."""
from bot.tvmaze import Episode, _strip_html, _to_show, format_show

SHOW_JSON = {
    "id": 169,
    "name": "Breaking Bad",
    "premiered": "2008-01-20",
    "status": "Ended",
    "rating": {"average": 9.2},
    "summary": "<p>A <b>chemistry</b> teacher turns to crime.</p>",
    "nextEpisodeAirdate": None,
}


def test_strip_html():
    assert _strip_html("<p>Hello <b>world</b></p>") == "Hello world"
    assert _strip_html(None) == ""


def test_to_show():
    s = _to_show(SHOW_JSON)
    assert s.id == 169
    assert s.name == "Breaking Bad"
    assert s.year == "2008"
    assert s.rating == "9.2"
    assert "chemistry" in s.summary and "<" not in s.summary
    assert s.next_airdate is None


def test_to_show_no_rating():
    s = _to_show({**SHOW_JSON, "rating": None})
    assert s.rating == "-"


def test_format_show_basic():
    s = _to_show(SHOW_JSON)
    text = format_show(s)
    assert "Breaking Bad (2008)" in text
    assert "/ikuti 169" in text
    assert "chemistry" not in text  # summary tidak ikut tanpa with_summary


def test_format_show_with_summary():
    s = _to_show(SHOW_JSON)
    text = format_show(s, with_summary=True)
    assert "chemistry" in text


def test_episode_fields():
    ep = Episode(season=1, number=5, name="Gray Matter", airdate="2008-02-24")
    assert ep.season == 1 and ep.number == 5 and ep.airdate == "2008-02-24"
