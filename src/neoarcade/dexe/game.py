"""Bộ điều khiển Đua Xe Dế — THUẦN (test được). update() nhận trục lái (axis) mỗi khung.

2 nút (khớp ThingBot) cho menu/kết quả; trong trận điều khiển bằng TRỤC LÁI:
  menu   : nút 0 = SOLO, nút 1 = ĐẤU
  kết quả: nút 0 = chơi lại, nút 1 = menu
"""
from __future__ import annotations

import random

from neoarcade import config as C
from neoarcade.engine.game import FrameEvents
from neoarcade.dexe.world import RaceWorld

LANES = [0.18, 0.5, 0.82]


def make_schedule(seed: int) -> list[tuple]:
    """Sinh lịch chướng ngại + năng lượng, luôn chừa ≥1 làn trống để né được."""
    rnd = random.Random(seed)
    sched: list[tuple] = []
    rows = int(C.RACE_TARGET / C.SPAWN_GAP) + 6
    for k in range(rows):
        d = (k + 2) * C.SPAWN_GAP
        n_obs = 1 if k < 6 else rnd.choice([1, 1, 2])
        obs = rnd.sample(range(3), n_obs)
        for li in obs:
            sched.append((d, "obstacle", LANES[li]))
        free = [i for i in range(3) if i not in obs]
        if free and rnd.random() < 0.7:
            sched.append((d, "energy", LANES[rnd.choice(free)]))
    sched.sort(key=lambda t: t[0])
    return sched


class RaceController:
    MENU, COUNTDOWN, PLAY, RESULT = "menu", "countdown", "play", "result"

    def __init__(self, leaderboard=None, seed: int = 1):
        self.lb = leaderboard
        self._seed = seed
        self.state = self.MENU
        self.mode: str | None = None
        self.worlds: list[RaceWorld] = []
        self.count = 0.0
        self.result = ""
        self.winner: int | None = None
        self.best = leaderboard.best("dexe") if leaderboard else 0
        self.play_ms = 0
        self.game_id = 0

    def start(self, mode: str) -> None:
        self.mode = mode
        self.game_id += 1
        self.play_ms = 0
        self.winner = None
        self.result = ""
        self._seed += 1
        sched = make_schedule(self._seed)
        if mode == "solo":
            self.worlds = [RaceWorld(C.W, C.H, sched, target=None, solo_hard=True)]
        else:
            half = C.W // 2
            self.worlds = [RaceWorld(half, C.H, sched, target=C.RACE_TARGET),
                           RaceWorld(half, C.H, sched, target=C.RACE_TARGET)]
        self.count = C.COUNTDOWN
        self.state = self.COUNTDOWN

    def press(self, btn: int) -> None:
        if btn not in (0, 1):
            return
        if self.state == self.MENU:
            self.start("solo" if btn == 0 else "duel")
        elif self.state == self.RESULT:
            if btn == 0:
                self.start(self.mode)
            else:
                self.state = self.MENU

    def update(self, dt: float, axes: list[float] | None = None) -> FrameEvents:
        axes = axes if axes is not None else [0.0] * len(self.worlds)
        ev = FrameEvents(flapped=[False] * len(self.worlds))
        if self.state == self.COUNTDOWN:
            self.count -= dt
            ev.countdown_tick = max(1, int(self.count) + 1)
            if self.count <= 0:
                self.state = self.PLAY
                ev.started = True
        elif self.state == self.PLAY:
            self.play_ms += int(dt * 1000)
            for i, w in enumerate(self.worlds):
                ev.steps.append(w.update(dt, axes[i] if i < len(axes) else 0.0))
            if self._check_end():
                ev.ended = True
        return ev

    def _check_end(self) -> bool:
        if self.mode == "solo":
            w = self.worlds[0]
            if w.dead:
                self.best = max(self.best, w.collected)
                if self.lb:
                    self.lb.add("dexe", "DE", w.collected, self.play_ms)
                self.result = f"{w.collected} năng lượng"
                self.state = self.RESULT
                return True
        else:
            p1, p2 = self.worlds
            if p1.finished or p2.finished:
                self.winner = 0 if p1.finished else 1
                if self.lb:
                    self.lb.add("dexe_duel", f"P{self.winner + 1}",
                                self.worlds[self.winner].collected, self.play_ms, won=1)
                self.result = f"P{self.winner + 1} VỀ ĐÍCH!"
                self.state = self.RESULT
                return True
        return False
