"""Test lõi đua xe (thuần)."""
import neoarcade.config as C
from neoarcade.dexe.world import RaceWorld


def w_solo(sched=None):
    return RaceWorld(C.W, C.H, sched or [], target=None, solo_hard=True)


def w_duel(sched=None, target=C.RACE_TARGET):
    return RaceWorld(C.W // 2, C.H, sched or [], target=target)


def _xf(w):
    return (w.x - w.left) / (w.right - w.left)


def test_steer_right_then_clamped():
    w = w_solo()
    x0 = w.x
    w.update(0.1, axis=1.0)
    assert w.x > x0
    for _ in range(200):
        w.update(0.05, axis=1.0)
    assert w.x <= w.right + 0.01


def test_steer_left_clamped():
    w = w_solo()
    for _ in range(200):
        w.update(0.05, axis=-1.0)
    assert w.x >= w.left - 0.01


def test_forward_distance_increases():
    w = w_solo()
    w.update(0.1, 0)
    assert w.dist > 0


def test_collect_energy_increments():
    w = w_solo()
    w.sched = [(w.dist + 5, "energy", _xf(w))]
    w.taken = [False]
    r = w.update(1 / 60, 0)
    assert w.collected == 1 and r.collected == 1


def test_obstacle_crashes_solo_to_dead():
    w = w_solo()
    w.sched = [(w.dist + 5, "obstacle", _xf(w))]
    w.taken = [False]
    r = w.update(1 / 60, 0)
    assert r.crashed is True and w.dead is True


def test_obstacle_duel_stuns_not_dead():
    w = w_duel()
    w.sched = [(w.dist + 5, "obstacle", _xf(w))]
    w.taken = [False]
    r = w.update(1 / 60, 0)
    assert r.crashed and w.stunned and not w.dead


def test_dodge_avoids_crash():
    w = w_solo()
    w.x = w.right                       # nép phải
    w.sched = [(w.dist + 5, "obstacle", 0.0)]   # chướng ngại sát trái
    w.taken = [False]
    r = w.update(1 / 60, 0)
    assert not r.crashed and not w.dead


def test_duel_finishes_at_target():
    w = w_duel(target=100)
    w.dist = 99
    r = w.update(1.0, 0)
    assert w.finished and r.finished


def test_stunned_no_forward_progress():
    w = w_duel()
    w.stun = 1.0
    d0 = w.dist
    w.update(0.1, 1.0)
    assert w.dist == d0
