"""Test leaderboard SQLite."""
from neoarcade.storage.db import Leaderboard


def test_add_and_best():
    lb = Leaderboard()
    lb.add("solo", "abc", 5)
    lb.add("solo", "xy", 12)
    assert lb.best("solo") == 12


def test_name_truncated_and_upper():
    lb = Leaderboard()
    lb.add("solo", "abcdef", 3)
    assert lb.top("solo")[0][0] == "ABC"


def test_top_ordering_and_limit():
    lb = Leaderboard()
    for i, s in enumerate([3, 9, 5, 1, 7, 8]):
        lb.add("solo", f"P{i}", s)
    assert [s for _, s in lb.top("solo", limit=3)] == [9, 8, 7]


def test_best_empty_is_zero():
    assert Leaderboard().best("duel") == 0


def test_today_filter_excludes_old():
    lb = Leaderboard()
    lb.add("solo", "old", 100, created_at="2000-01-01 10:00:00")
    lb.add("solo", "new", 5)
    today = lb.top("solo", today=True)
    assert ("OLD", 100) not in today
    assert any(n == "NEW" for n, _ in today)
