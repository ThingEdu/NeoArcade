"""Test lõi Đấm Bốc (thử lực / đẩy)."""
import neoarcade.config as C
from neoarcade.damboc.game import BoxController
from neoarcade.storage.db import Leaderboard


def _play(c):
    while c.state != c.PLAY:
        c.update(1 / 60)


def test_menu_starts_solo_and_duel():
    c = BoxController()
    c.press(0)
    assert c.mode == "solo"
    d = BoxController()
    d.press(1)
    assert d.mode == "duel"


def test_solo_punch_builds_power():
    c = BoxController()
    c.press(0)
    _play(c)
    for _ in range(5):
        c.press(0)
    assert c.power > 0 and c.peak > 0 and c.punches[0] == 5


def test_solo_power_decays_without_punch():
    c = BoxController()
    c.press(0)
    _play(c)
    for _ in range(5):
        c.press(0)
    before = c.power
    c.update(0.3)
    assert c.power < before


def test_solo_ends_records_peak():
    lb = Leaderboard()
    c = BoxController(leaderboard=lb)
    c.press(0)
    _play(c)
    for _ in range(15):
        c.press(0)
    c.timer = 0.01
    c.update(0.05)
    assert c.state == c.RESULT and lb.best("damboc") >= 1


def test_duel_p1_pushes_to_win():
    c = BoxController()
    c.press(1)
    _play(c)
    for _ in range(int(C.BX_WIN / C.BX_PUSH_STEP) + 2):
        c.press(0)
    c.update(1 / 60)
    assert c.state == c.RESULT and c.winner == 0


def test_duel_p2_pushes_to_win():
    c = BoxController()
    c.press(1)
    _play(c)
    for _ in range(int(C.BX_WIN / C.BX_PUSH_STEP) + 2):
        c.press(1)
    c.update(1 / 60)
    assert c.state == c.RESULT and c.winner == 1
