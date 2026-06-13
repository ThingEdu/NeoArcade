"""Lõi mô phỏng 1 người chơi FlappyDe — THUẦN Python, test 100% (không pygame)."""
from __future__ import annotations

from dataclasses import dataclass

from neoarcade import config as C


@dataclass
class StepResult:
    """Sự kiện sinh ra trong 1 bước update — để lớp UI tạo hiệu ứng."""
    passed: int = 0      # số cột vừa vượt qua trong bước này
    hit: bool = False
    finished: bool = False
    night: bool = False  # vừa mở "thế giới đêm" (bay vượt đỉnh màn hình)


class World:
    """Một thế giới Flappy độc lập cho 1 người chơi.

    target=None  → solo (chạm là chết, khó dần).
    target=N     → đấu (về đích N cột; chạm thì choáng + bất tử rồi chơi tiếp).
    """

    def __init__(self, vw: int, vh: int, gaps: list[int],
                 target: int | None = None, solo_hard: bool = False):
        self.vw, self.vh = vw, vh
        self.gaps = gaps
        self.target = target
        self.solo_hard = solo_hard
        self.bird_x = int(vw * 0.27)
        self.reset()

    def reset(self) -> None:
        self.y = self.vh / 2
        self.v = 0.0
        self.score = 0
        self.next_idx = 0
        self.pipes: list[list] = []      # mỗi cột: [x, gap_y, passed]
        self.stun = 0.0
        self.invuln = 0.0
        self.dead = False
        self.finished = False
        self.night = False               # thế giới đêm (easter egg)

    # ---- thuộc tính dẫn xuất ----
    @property
    def speed(self) -> float:
        base = C.BASE_SPEED + (self.score * C.SPEED_PER_POINT if self.solo_hard else 0)
        return base * (C.NIGHT_SPEED if self.night else 1.0)

    @property
    def gap(self) -> int:
        g = C.DUEL_GAP if self.target is not None else max(C.SOLO_GAP_MIN, C.SOLO_GAP0 - self.score * 2)
        return max(C.SOLO_GAP_MIN - 12, g - C.NIGHT_GAP) if self.night else g

    @property
    def stunned(self) -> bool:
        return self.stun > 0

    @property
    def alive(self) -> bool:
        return not self.dead and not self.finished

    # ---- điều khiển ----
    def flap(self) -> bool:
        """Vỗ cánh. Trả về True nếu có hiệu lực (để UI phát hiệu ứng/âm thanh)."""
        if self.dead or self.finished or self.stun > 0:
            return False
        self.v = C.FLAP_V
        return True

    # ---- mô phỏng ----
    def _spawn(self) -> None:
        gy = self.gaps[self.next_idx % len(self.gaps)]
        lo = 100 + self.gap // 2
        hi = self.vh - C.GROUND_H - 100 - self.gap // 2
        gy = max(lo, min(hi, gy))
        self.pipes.append([self.vw + C.PIPE_W, gy, False])
        self.next_idx += 1

    def update(self, dt: float) -> StepResult:
        res = StepResult()
        if self.finished or self.dead:
            return res
        if self.invuln > 0:
            self.invuln -= dt
        if self.stun > 0:                    # choáng: đóng băng + bất tử
            self.stun -= dt
            self.v = 0
            return res

        self.v += C.GRAVITY * dt
        self.y += self.v * dt

        # bay VƯỢT ĐỈNH màn hình → mở "thế giới đêm" (1 lần)
        if not self.night and self.y < -C.BIRD_R:
            self.night = True
            res.night = True

        if not self.pipes or self.pipes[-1][0] < self.vw - C.PIPE_SPACING:
            self._spawn()
        for pipe in self.pipes:
            pipe[0] -= self.speed * dt
            if not pipe[2] and pipe[0] + C.PIPE_W < self.bird_x:
                pipe[2] = True
                self.score += 1
                res.passed += 1
                if self.target is not None and self.score >= self.target:
                    self.finished = True
                    res.finished = True
        self.pipes = [p for p in self.pipes if p[0] > -C.PIPE_W]

        if self.invuln <= 0 and self._hit():
            res.hit = True
            self._on_hit()
        return res

    def _hit(self) -> bool:
        bx, by, br = self.bird_x, self.y, C.BIRD_R
        # KHÔNG chết khi vượt trần (để mở thế giới đêm); chỉ chết khi chạm đất
        if by + br > self.vh - C.GROUND_H:
            return True
        for px, gy, _ in self.pipes:
            if px < bx + br and px + C.PIPE_W > bx - br:
                if by - br < gy - self.gap // 2 or by + br > gy + self.gap // 2:
                    return True
        return False

    def _on_hit(self) -> None:
        if self.target is not None:          # đấu: choáng rồi chơi tiếp
            self.stun = C.STUN_TIME
            self.invuln = C.STUN_TIME + C.INVULN_EXTRA
            self.v = 0
            self.y = self.vh / 2
            for p in self.pipes:
                p[0] += C.HIT_PUSHBACK
        else:                                # solo: chết
            self.dead = True
