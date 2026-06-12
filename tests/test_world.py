"""Test lõi mô phỏng World (thuần, không pygame)."""
import neoarcade.config as C
from neoarcade.engine.world import World


def w_solo(gaps=None):
    return World(C.W, C.H, gaps or [300] * 30, target=None, solo_hard=True)


def w_duel(gaps=None, target=C.DUEL_TARGET):
    return World(C.W // 2, C.H, gaps or [300] * 30, target=target)


def test_flap_sets_upward_velocity():
    w = w_solo()
    w.v = 120
    assert w.flap() is True
    assert w.v == C.FLAP_V


def test_gravity_pulls_down_when_no_flap():
    w = w_solo()
    y0 = w.y
    w.update(0.1)
    assert w.y > y0
    assert w.v > 0


def test_pass_pipe_increments_score():
    w = w_solo()
    w.y = C.H / 2
    w.pipes = [[10, int(C.H / 2), False]]   # x+PIPE_W=94 < bird_x → vượt qua
    w.next_idx = 1
    r = w.update(1 / 60)
    assert w.score == 1 and r.passed == 1


def test_solo_dies_on_ground():
    w = w_solo()
    w.y = C.H - C.GROUND_H - C.BIRD_R + 4
    r = w.update(1 / 60)
    assert w.dead is True and r.hit is True


def test_solo_dies_on_ceiling():
    w = w_solo()
    w.y = 5
    r = w.update(1 / 60)
    assert w.dead is True


def test_solo_gap_shrinks_with_score():
    w = w_solo()
    g0 = w.gap
    w.score = 20
    assert w.gap < g0
    w.score = 10_000
    assert w.gap == C.SOLO_GAP_MIN


def test_speed_increases_in_solo_hard():
    w = w_solo()
    s0 = w.speed
    w.score = 10
    assert w.speed > s0


def test_duel_hit_causes_stun_not_death():
    w = w_duel()
    w.y = C.H + 50
    r = w.update(1 / 60)
    assert r.hit is True
    assert w.stunned is True
    assert w.dead is False


def test_stunned_cannot_flap():
    w = w_duel()
    w.stun = 1.0
    assert w.flap() is False


def test_invuln_after_stun_in_duel():
    w = w_duel()
    w.y = C.H + 50
    w.update(1 / 60)
    assert w.invuln > 0


def test_duel_finishes_at_target():
    w = w_duel(target=2)
    w.score = 1
    w.y = C.H / 2
    w.pipes = [[10, int(C.H / 2), False]]
    w.next_idx = 1
    r = w.update(1 / 60)
    assert w.score == 2 and w.finished is True and r.finished is True
