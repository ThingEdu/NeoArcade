"""Lõi Đấm Bốc — THUẦN Python, test được.

solo : đập nút liên tục trong BX_TIME giây để dồn LỰC (tụt dần nếu ngừng); điểm = lực đỉnh.
duel : 2 người đập nút đẩy vạch về phía đối thủ; đẩy tới ±BX_WIN = thắng (hoặc hết giờ ai dẫn).
"""
from __future__ import annotations

from dataclasses import dataclass

from neoarcade import config as C


@dataclass
class BoxEvents:
    punches: list = None        # [player] vừa đấm khung này
    countdown_tick: int | None = None
    started: bool = False
    ended: bool = False

    def __post_init__(self):
        if self.punches is None:
            self.punches = []


class BoxController:
    MENU, COUNTDOWN, PLAY, RESULT = "menu", "countdown", "play", "result"

    def __init__(self, leaderboard=None, seed=1):
        self.lb = leaderboard
        self.state = self.MENU
        self.mode = None
        self.power = 0.0        # solo: lực hiện tại
        self.peak = 0.0
        self.pos = 0.0          # duel: vạch (-BX_WIN..BX_WIN); +=P1 đẩy, -=P2
        self.punches = [0, 0]
        self.timer = 0.0
        self.count = 0.0
        self.result = ""
        self.winner = None
        self.best = leaderboard.best("damboc") if leaderboard else 0
        self.game_id = 0
        self._queue: list = []

    def start(self, mode):
        self.mode = mode
        self.game_id += 1
        self.power = 0.0
        self.peak = 0.0
        self.pos = 0.0
        self.punches = [0, 0]
        self.timer = C.BX_TIME if mode == "solo" else C.BX_DUEL_TIME
        self.count = C.COUNTDOWN
        self.result = ""
        self.winner = None
        self._queue = []
        self.state = self.COUNTDOWN

    def press(self, btn):
        if btn not in (0, 1):
            return
        if self.state == self.MENU:
            self.start("solo" if btn == 0 else "duel")
        elif self.state == self.RESULT:
            self.start(self.mode) if btn == 0 else setattr(self, "state", self.MENU)
        elif self.state == self.PLAY:
            if self.mode == "solo":
                if btn == 0:
                    self.power = min(100.0, self.power + C.BX_GAIN)
                    self.peak = max(self.peak, self.power)
                    self.punches[0] += 1
                    self._queue.append(0)
            else:
                if btn == 0:
                    self.pos = min(C.BX_WIN, self.pos + C.BX_PUSH_STEP)
                else:
                    self.pos = max(-C.BX_WIN, self.pos - C.BX_PUSH_STEP)
                self.punches[btn] += 1
                self._queue.append(btn)

    def update(self, dt) -> BoxEvents:
        ev = BoxEvents()
        if self.state == self.COUNTDOWN:
            self.count -= dt
            ev.countdown_tick = max(1, int(self.count) + 1)
            if self.count <= 0:
                self.state = self.PLAY
                ev.started = True
            return ev
        if self.state != self.PLAY:
            return ev
        ev.punches, self._queue = self._queue, []
        self.timer -= dt
        if self.mode == "solo":
            self.power = max(0.0, self.power - C.BX_DECAY * dt)
            self.peak = max(self.peak, self.power)
            if self.timer <= 0:
                self._end(ev)
        elif abs(self.pos) >= C.BX_WIN:          # thắng do đẩy tới đích (kiểm tra TRƯỚC khi trôi)
            self._end(ev)
        else:
            if self.pos > 0:
                self.pos = max(0.0, self.pos - C.BX_PUSH_DECAY * dt)
            elif self.pos < 0:
                self.pos = min(0.0, self.pos + C.BX_PUSH_DECAY * dt)
            if self.timer <= 0:
                self._end(ev)
        return ev

    def _end(self, ev):
        ev.ended = True
        if self.mode == "solo":
            score = int(self.peak)
            self.best = max(self.best, score)
            if self.lb:
                self.lb.add("damboc", "DE", score, int(C.BX_TIME * 1000))
            self.result = f"{score} lực"
        else:
            self.winner = 0 if self.pos >= 0 else 1
            if self.lb:
                self.lb.add("damboc_duel", f"P{self.winner + 1}", abs(int(self.pos)), 0, won=1)
            self.result = f"P{self.winner + 1} THẮNG!"
        self.state = self.RESULT
