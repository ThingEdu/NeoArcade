"""Lõi Bóng Rổ Dế — THUẦN Python, test được.

Thanh LỰC dao động lên xuống; nhấn nút đúng lúc lực khớp khoảng cách rổ → VÀO.
Rổ đổi khoảng cách mỗi lần. Đếm giờ. solo 1 rổ / duel 2 rổ (nút 0 = P1, nút 1 = P2).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from neoarcade import config as C


@dataclass
class BasketEvents:
    shots: list = field(default_factory=list)     # (player, made)
    countdown_tick: int | None = None
    started: bool = False
    ended: bool = False


class BasketController:
    MENU, COUNTDOWN, PLAY, RESULT = "menu", "countdown", "play", "result"

    def __init__(self, leaderboard=None, seed=1):
        self.lb = leaderboard
        self.rng = random.Random(seed)
        self.state = self.MENU
        self.mode = None
        self.baskets = [0]
        self.hoop = [0.0]
        self.phase_t = [0.0]
        self.ph = ["aim"]
        self.fly_t = [0.0]
        self.shot_power = [0.0]
        self.shot_made = [False]
        self.timer = 0.0
        self.count = 0.0
        self.result = ""
        self.winner = None
        self.best = leaderboard.best("bongro") if leaderboard else 0
        self.game_id = 0
        self._pending = [False, False]

    def _n(self):
        return len(self.baskets)

    def _hoop(self):
        return self.rng.uniform(C.BR_HOOP_MIN, C.BR_HOOP_MAX)

    def power(self, k):
        return (math.sin(self.phase_t[k]) + 1) / 2

    def required(self, k):
        return (self.hoop[k] - C.BR_LAUNCH_X) / C.BR_RANGE

    def start(self, mode):
        n = 1 if mode == "solo" else 2
        self.mode = mode
        self.game_id += 1
        self.baskets = [0] * n
        self.hoop = [self._hoop() for _ in range(n)]
        self.phase_t = [self.rng.uniform(0, 6) for _ in range(n)]
        self.ph = ["aim"] * n
        self.fly_t = [0.0] * n
        self.shot_power = [0.0] * n
        self.shot_made = [False] * n
        self.timer = C.BR_TIME
        self.count = C.COUNTDOWN
        self.result = ""
        self.winner = None
        self._pending = [False, False]
        self.state = self.COUNTDOWN

    def press(self, btn):
        if btn not in (0, 1):
            return
        if self.state == self.MENU:
            self.start("solo" if btn == 0 else "duel")
        elif self.state == self.RESULT:
            self.start(self.mode) if btn == 0 else setattr(self, "state", self.MENU)
        elif btn < self._n():
            self._pending[btn] = True

    def _shoot(self, k, ev):
        p = self.power(k)
        self.shot_power[k] = p
        landing = C.BR_LAUNCH_X + p * C.BR_RANGE
        made = abs(landing - self.hoop[k]) < C.BR_POWER_TOL * C.BR_RANGE
        self.shot_made[k] = made
        if made:
            self.baskets[k] += 1
        self.ph[k] = "fly"
        self.fly_t[k] = C.BR_SHOT_ANIM
        ev.shots.append((k, made))

    def update(self, dt) -> BasketEvents:
        ev = BasketEvents()
        if self.state == self.COUNTDOWN:
            self.count -= dt
            ev.countdown_tick = max(1, int(self.count) + 1)
            if self.count <= 0:
                self.state = self.PLAY
                ev.started = True
            return ev
        if self.state != self.PLAY:
            return ev
        self.timer -= dt
        for k in range(self._n()):
            if self.ph[k] == "aim":
                self.phase_t[k] += C.BR_OSC * 2 * math.pi * dt
                if self._pending[k]:
                    self._pending[k] = False
                    self._shoot(k, ev)
            else:
                self._pending[k] = False
                self.fly_t[k] -= dt
                if self.fly_t[k] <= 0:
                    self.ph[k] = "aim"
                    self.hoop[k] = self._hoop()
        if self.timer <= 0:
            self._end(ev)
        return ev

    def _end(self, ev):
        ev.ended = True
        if self.mode == "solo":
            self.best = max(self.best, self.baskets[0])
            if self.lb:
                self.lb.add("bongro", "DE", self.baskets[0], int(C.BR_TIME * 1000))
            self.result = f"{self.baskets[0]} rổ"
        else:
            self.winner = 0 if self.baskets[0] >= self.baskets[1] else 1
            if self.lb:
                self.lb.add("bongro_duel", f"P{self.winner + 1}", self.baskets[self.winner], 0, won=1)
            self.result = f"P{self.winner + 1} THẮNG  ({self.baskets[0]}–{self.baskets[1]})"
        self.state = self.RESULT
