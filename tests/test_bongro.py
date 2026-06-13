"""Test lõi Bóng Rổ Dế (canh lực)."""
import math

import neoarcade.config as C
from neoarcade.bongro.game import BasketController
from neoarcade.storage.db import Leaderboard


def _play(c):
    while c.state != c.PLAY:
        c.update(1 / 60)


def _set_power(c, k, target):
    target = max(0.0, min(1.0, target))
    c.phase_t[k] = math.asin(max(-1.0, min(1.0, 2 * target - 1)))


def test_menu_starts_solo_and_duel():
    c = BasketController()
    c.press(0)
    assert c.mode == "solo" and c._n() == 1
    d = BasketController()
    d.press(1)
    assert d.mode == "duel" and d._n() == 2


def test_shoot_at_required_power_scores():
    c = BasketController()
    c.press(0)
    _play(c)
    _set_power(c, 0, c.required(0))
    c.press(0)
    ev = c.update(0.0)
    assert c.baskets[0] == 1 and (0, True) in ev.shots and c.ph[0] == "fly"


def test_shoot_wrong_power_misses():
    c = BasketController()
    c.press(0)
    _play(c)
    req = c.required(0)
    _set_power(c, 0, req - 0.5 if req > 0.5 else req + 0.5)
    c.press(0)
    ev = c.update(0.0)
    assert c.baskets[0] == 0 and (0, False) in ev.shots


def test_fly_returns_to_aim_with_new_hoop():
    c = BasketController()
    c.press(0)
    _play(c)
    c.press(0)
    c.update(0.0)
    assert c.ph[0] == "fly"
    for _ in range(int(C.BR_SHOT_ANIM * 60) + 3):
        c.update(1 / 60)
    assert c.ph[0] == "aim"


def test_timer_ends_to_result():
    c = BasketController()
    c.press(0)
    _play(c)
    c.timer = 0.01
    c.update(0.05)
    assert c.state == c.RESULT


def test_solo_records_best():
    lb = Leaderboard()
    c = BasketController(leaderboard=lb)
    c.press(0)
    _play(c)
    c.baskets[0] = 7
    c.timer = 0.01
    c.update(0.05)
    assert lb.best("bongro") >= 7
