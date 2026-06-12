"""Lõi đua xe 1 người — THUẦN Python (không pygame), test được.

Top-down: xe ở gần đáy, đường cuộn xuống theo quãng đường `dist`.
Lái trái/phải bằng `axis` ∈ [-1, 1]. Né chướng ngại, hốt viên năng lượng.
  target=None → solo (đụng là chết, nhanh dần).
  target=N    → đấu (về đích N px; đụng thì xoay vòng + bất tử rồi chạy tiếp).

`schedule`: list (dist, kind, xfrac) — kind ∈ {"obstacle","energy"}, xfrac ∈ [0,1] ngang đường.
Cả 2 người dùng chung schedule → công bằng.
"""
from __future__ import annotations

from dataclasses import dataclass

from neoarcade import config as C


@dataclass
class RaceStep:
    collected: int = 0
    crashed: bool = False
    finished: bool = False


class RaceWorld:
    def __init__(self, vw: int, vh: int, schedule: list[tuple], target: int | None = None,
                 solo_hard: bool = False):
        self.vw, self.vh = vw, vh
        self.sched = schedule
        self.target = target
        self.solo_hard = solo_hard
        self.car_y = vh - 130
        self.reset()

    def reset(self) -> None:
        self.x = self.vw / 2
        self.dist = 0.0
        self.cursor = 0
        self.taken = [False] * len(self.sched)
        self.collected = 0
        self.stun = 0.0
        self.invuln = 0.0
        self.dead = False
        self.finished = False

    # ---- thuộc tính ----
    @property
    def left(self) -> float:
        return C.ROAD_MARGIN + C.CAR_W / 2

    @property
    def right(self) -> float:
        return self.vw - C.ROAD_MARGIN - C.CAR_W / 2

    @property
    def speed(self) -> float:
        return C.RACE_SPEED + (self.dist * C.RACE_SPEED_PER if self.solo_hard else 0)

    @property
    def stunned(self) -> bool:
        return self.stun > 0

    @property
    def alive(self) -> bool:
        return not self.dead and not self.finished

    @property
    def progress(self) -> float:
        return min(1.0, self.dist / self.target) if self.target else 0.0

    def item_x(self, xfrac: float) -> float:
        return self.left + xfrac * (self.right - self.left)

    def item_screen_y(self, dist: float) -> float:
        return self.car_y - (dist - self.dist)

    # ---- mô phỏng ----
    def update(self, dt: float, axis: float = 0.0) -> RaceStep:
        res = RaceStep()
        if self.finished or self.dead:
            return res
        if self.invuln > 0:
            self.invuln -= dt
        if self.stun > 0:                 # xoay vòng: không tiến/lái, bất tử
            self.stun -= dt
            return res

        self.x += axis * C.STEER_SPEED * dt
        self.x = max(self.left, min(self.right, self.x))
        self.dist += self.speed * dt
        if self.target is not None and self.dist >= self.target:
            self.finished = True
            res.finished = True
        self._interact(res)
        return res

    def _interact(self, res: RaceStep) -> None:
        while self.cursor < len(self.sched) and self.sched[self.cursor][0] < self.dist - C.CAR_H:
            self.cursor += 1
        i = self.cursor
        while i < len(self.sched) and self.sched[i][0] <= self.dist + C.CAR_H:
            d, kind, xfrac = self.sched[i]
            if not self.taken[i]:
                half_h = C.OBSTACLE_H / 2 if kind == "obstacle" else C.ENERGY_R
                half_w = C.OBSTACLE_W / 2 if kind == "obstacle" else C.ENERGY_R
                if abs(d - self.dist) < C.CAR_H / 2 + half_h and \
                        abs(self.item_x(xfrac) - self.x) < C.CAR_W / 2 + half_w:
                    if kind == "energy":
                        self.taken[i] = True
                        self.collected += 1
                        res.collected += 1
                    elif self.invuln <= 0:           # obstacle
                        self.taken[i] = True
                        res.crashed = True
                        self._crash()
            i += 1

    def _crash(self) -> None:
        if self.target is not None:       # đấu: xoay vòng rồi chạy tiếp
            self.stun = C.RACE_STUN
            self.invuln = C.RACE_STUN + C.RACE_INVULN_EXTRA
        else:                             # solo: chết
            self.dead = True
