"""Bộ điều khiển trạng thái FlappyDe — THUẦN Python (test được, không pygame).

Chỉ có 2 nút (khớp ThingBot). Ý nghĩa nút theo trạng thái:
  menu   : nút 0 = chơi SOLO,  nút 1 = chơi ĐẤU
  chơi   : nút 0 = vỗ cánh P1, nút 1 = vỗ cánh P2
  kết quả: nút 0 = chơi lại,   nút 1 = về menu
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from neoarcade import config as C
from neoarcade.engine.world import StepResult, World


@dataclass
class FrameEvents:
    """Sự kiện 1 khung — để UI tạo hiệu ứng/âm thanh."""
    steps: list[StepResult] = field(default_factory=list)
    flapped: list[bool] = field(default_factory=list)
    countdown_tick: int | None = None
    started: bool = False
    ended: bool = False


class Controller:
    MENU, COUNTDOWN, PLAY, RESULT = "menu", "countdown", "play", "result"

    def __init__(self, leaderboard=None, seed: int = 1):
        self.lb = leaderboard
        self._seed = seed
        self.state = self.MENU
        self.mode: str | None = None
        self.worlds: list[World] = []
        self.count = 0.0
        self.result = ""
        self.winner: int | None = None
        self.best = leaderboard.best("solo") if leaderboard else 0
        self.play_ms = 0
        self.game_id = 0
        self._pending_flap = [False, False]
        self._prev_ceil = 0

    # ---- bố cục cột ----
    def _gaps(self) -> list[int]:
        self._seed += 1
        rnd = random.Random(self._seed)
        return [rnd.randint(150, C.H - C.GROUND_H - 150) for _ in range(C.DUEL_TARGET + 6)]

    # ---- vòng đời ----
    def start(self, mode: str) -> None:
        self.mode = mode
        self.game_id += 1
        self.play_ms = 0
        self.winner = None
        self.result = ""
        gaps = self._gaps()
        if mode == "solo":
            self.worlds = [World(C.W, C.H, gaps, target=None, solo_hard=True)]
        else:
            half = C.W // 2
            self.worlds = [World(half, C.H, gaps, target=C.DUEL_TARGET),
                           World(half, C.H, gaps, target=C.DUEL_TARGET)]
        self.count = C.COUNTDOWN
        self.state = self.COUNTDOWN
        self._pending_flap = [False, False]

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
        else:  # countdown | play → đánh dấu vỗ cánh
            if btn < len(self.worlds):
                self._pending_flap[btn] = True

    def update(self, dt: float) -> FrameEvents:
        ev = FrameEvents(flapped=[False] * len(self.worlds))
        if self.state == self.COUNTDOWN:
            for i, w in enumerate(self.worlds):
                if self._pending_flap[i]:
                    self._pending_flap[i] = False
            self.count -= dt
            ev.countdown_tick = max(1, int(self.count) + 1)
            if self.count <= 0:
                self.state = self.PLAY
                ev.started = True
        elif self.state == self.PLAY:
            self.play_ms += int(dt * 1000)
            for i, w in enumerate(self.worlds):
                if self._pending_flap[i]:
                    ev.flapped[i] = w.flap()
                    self._pending_flap[i] = False
                ev.steps.append(w.update(dt))
            if self._check_end():
                ev.ended = True
        return ev

    def _check_end(self) -> bool:
        if self.mode == "solo":
            w = self.worlds[0]
            if w.dead:
                self.best = max(self.best, w.score)
                if self.lb:
                    self.lb.add("solo", "DE", w.score, self.play_ms)
                self.result = f"{w.score} điểm"
                self.state = self.RESULT
                return True
        else:
            p1, p2 = self.worlds
            if p1.finished or p2.finished:
                self.winner = 0 if p1.finished else 1
                if self.lb:
                    self.lb.add("duel", f"P{self.winner + 1}",
                                self.worlds[self.winner].score, self.play_ms, won=1)
                self.result = f"P{self.winner + 1} THẮNG!"
                self.state = self.RESULT
                return True
        return False
