"""Test bộ điều khiển trạng thái (2 nút khớp ThingBot)."""
import neoarcade.config as C
from neoarcade.engine.game import Controller
from neoarcade.storage.db import Leaderboard


def _to_play(c):
    while c.state != c.PLAY:
        c.update(1 / 60)


def test_menu_button0_starts_solo():
    c = Controller()
    c.press(0)
    assert c.mode == "solo" and c.state == c.COUNTDOWN and len(c.worlds) == 1


def test_menu_button1_starts_duel():
    c = Controller()
    c.press(1)
    assert c.mode == "duel" and len(c.worlds) == 2


def test_countdown_advances_to_play():
    c = Controller()
    c.press(0)
    _to_play(c)
    assert c.state == c.PLAY


def test_solo_death_goes_to_result_and_records_score():
    lb = Leaderboard()
    c = Controller(leaderboard=lb)
    c.press(0)
    _to_play(c)
    c.worlds[0].score = 4
    c.worlds[0].y = C.H + 80          # ép chết
    for _ in range(6):
        c.update(1 / 60)
        if c.state == c.RESULT:
            break
    assert c.state == c.RESULT
    assert lb.best("solo") >= 4


def test_result_button0_restarts_same_mode():
    c = Controller()
    c.mode = "solo"
    c.state = c.RESULT
    c.press(0)
    assert c.state == c.COUNTDOWN and c.mode == "solo"


def test_result_button1_returns_to_menu():
    c = Controller()
    c.mode = "solo"
    c.state = c.RESULT
    c.press(1)
    assert c.state == c.MENU
