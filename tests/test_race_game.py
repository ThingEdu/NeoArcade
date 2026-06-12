"""Test bộ điều khiển + lịch sinh vật thể của Đua Xe Dế."""
import neoarcade.config as C
from neoarcade.dexe.game import RaceController, make_schedule
from neoarcade.storage.db import Leaderboard


def _to_play(c):
    while c.state != c.PLAY:
        c.update(1 / 60)


def test_schedule_always_leaves_a_free_lane():
    sched = make_schedule(7)
    obs_by_dist = {}
    for d, kind, _ in sched:
        if kind == "obstacle":
            obs_by_dist[d] = obs_by_dist.get(d, 0) + 1
    assert obs_by_dist and max(obs_by_dist.values()) <= 2   # luôn ≥1 làn trống / 3 làn


def test_menu_button0_starts_solo():
    c = RaceController()
    c.press(0)
    assert c.mode == "solo" and c.state == c.COUNTDOWN and len(c.worlds) == 1


def test_menu_button1_starts_duel():
    c = RaceController()
    c.press(1)
    assert c.mode == "duel" and len(c.worlds) == 2


def test_countdown_advances_to_play():
    c = RaceController()
    c.press(0)
    _to_play(c)
    assert c.state == c.PLAY


def test_solo_crash_records_energy():
    lb = Leaderboard()
    c = RaceController(leaderboard=lb)
    c.press(0)
    _to_play(c)
    w = c.worlds[0]
    w.collected = 5
    xf = (w.x - w.left) / (w.right - w.left)
    w.sched = [(w.dist + 3, "obstacle", xf)]
    w.taken = [False]
    w.cursor = 0
    for _ in range(4):
        c.update(1 / 60, [0.0])
        if c.state == c.RESULT:
            break
    assert c.state == c.RESULT and lb.best("dexe") >= 5


def test_result_button0_restarts():
    c = RaceController()
    c.mode = "solo"
    c.state = c.RESULT
    c.press(0)
    assert c.state == c.COUNTDOWN


def test_duel_winner_recorded_on_finish():
    c = RaceController()
    c.press(1)
    _to_play(c)
    c.worlds[0].dist = C.RACE_TARGET
    c.update(1 / 60, [0.0, 0.0])
    assert c.state == c.RESULT and c.winner == 0
