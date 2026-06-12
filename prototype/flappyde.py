"""FlappyDe — game đầu tiên trong bộ NeoArcade (ThingEdu).

Điều khiển 1 nút: nhấn = con Dế vỗ cánh bay lên, né khe giữa các thân sậy.
Giao diện theo bộ nhận diện Dế Foundation (DE STEM).

CHẾ ĐỘ:
  • SOLO       — 1 người, đua bảng điểm (vô tận, khó dần).
  • ĐẤU 2 NGƯỜI — màn chia đôi, đua tới vạch đích cố định; chạm cột = choáng 1.2s.

HỒ SƠ ĐIỀU KHIỂN (control profile) — game chỉ nghe "flap(player)", nguồn nào cũng được:
  • keyboard : P1 = SPACE, P2 = ENTER   (bàn phím ngoài — bản demo/triển lãm)
  • thingbot : P1/P2 = nút bấm trên mạch ThingBot ESP32 (qua neo-hw, bản chính thức)
  • jumppad  : (tương lai) nút cảm ứng — học sinh NHẢY LÊN để vỗ cánh (vận động thật)
Đổi profile ở CONTROL_PROFILE. Bản prototype hiện chạy 'keyboard'.

Chạy:  .venv/bin/python flappyde.py
"""
from __future__ import annotations

import math
import os
import random

import pygame

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def load_logo():
    """Logo Dế Foundation (nền trong suốt). None nếu thiếu file → fallback chữ."""
    try:
        return pygame.image.load(os.path.join(ASSET_DIR, "logo_de.png")).convert_alpha()
    except Exception:
        return None


def scale_to(img, w=None, h=None):
    iw, ih = img.get_size()
    if w is None:
        w = int(iw * h / ih)
    if h is None:
        h = int(ih * w / iw)
    return pygame.transform.smoothscale(img, (w, h))

# ---------- Cấu hình ----------
W, H = 900, 600
FPS = 60
GRAVITY = 1500.0
FLAP_V = -420.0
PIPE_W = 84
PIPE_SPACING = 270
GROUND_H = 80
DUEL_TARGET = 18          # số cột để về đích (đấu 2 người)
DUEL_GAP = 195            # khe cố định khi đấu (công bằng)
SOLO_GAP0 = 205           # khe ban đầu solo
BASE_SPEED = 220.0
SPEED_PER_POINT = 6.0
STUN_TIME = 1.2

CONTROL_PROFILE = "keyboard"   # keyboard | thingbot | jumppad

# ---------- Bảng màu Dế Foundation ----------
BLUE_ELECTRIC = (35, 71, 251)    # #2347FB
BLUE_WING = (104, 134, 252)
BLUE_CYAN = (148, 246, 255)      # #94F6FF
BLUE_SOFT = (216, 239, 255)      # #D8EFFF
PINK_HOT = (215, 29, 144)        # #D71D90
ORANGE_HOT = (231, 77, 30)       # #E74D1E
ORANGE_WARM = (240, 112, 32)     # #F07020
GREEN_CRICKET = (12, 112, 105)   # #0C7069
GREEN_DEEP = (9, 84, 78)
GREEN_LIME = (213, 242, 68)      # #D5F244
GREEN_SOFT = (241, 255, 211)     # #F1FFD3
INK = (18, 18, 18)
WHITE = (247, 247, 247)

FONT_STACK = "arialroundedmtbold,avenirnextrounded,avenirnext,nunito,inter,helveticaneue,arial"
_sky_cache: dict = {}


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def font(size, bold=True):
    return pygame.font.SysFont(FONT_STACK, size, bold=bold)


def make_sky(w, h):
    key = (w, h)
    if key not in _sky_cache:
        s = pygame.Surface((w, h))
        for y in range(h):
            s.fill(lerp(BLUE_CYAN, BLUE_SOFT, (y / h) ** 0.8), (0, y, w, 1))
        # mặt trời cam — chỉ vẽ ở màn lớn (menu/solo); màn chia đôi bỏ để khỏi chen HUD
        if w >= 700:
            pygame.draw.circle(s, ORANGE_WARM, (w - 70, 70), 38)
            pygame.draw.circle(s, (*ORANGE_HOT, 60), (w - 70, 70), 52, 6)
        _sky_cache[key] = s
    return _sky_cache[key]


def _smooth(surf, color, pts, width):
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for j in range(9):
            t = j / 8
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if len(out) > 1:
        pygame.draw.lines(surf, color, False, out, width)


def draw_cricket(target, cx, cy, color=BLUE_ELECTRIC, squash=1.0, wing=0.0, rot=0.0, band=None):
    """Con Dế phẳng một-màu, quay phải — bám sát logo Dế Foundation."""
    surf = pygame.Surface((150, 150), pygame.SRCALPHA)
    cxl, cyl = 70, 80

    def P(x, y):
        return (cxl + x, cyl + y)

    sq = 0.82 + 0.18 * squash
    bw, bh = int(58 * sq), int(32 / sq)
    pygame.draw.line(surf, color, P(-8, 7), P(-26, 18), 8)
    pygame.draw.line(surf, color, P(-26, 18), P(-12, 25), 8)
    pygame.draw.line(surf, color, P(10, 11), P(8, 24), 4)
    pygame.draw.polygon(surf, color, [P(-40, 1), P(-8, -bh // 2 + 3), P(-8, bh // 2 - 3)])
    pygame.draw.ellipse(surf, color, (P(-14, -bh // 2)[0], P(-14, -bh // 2)[1], bw, bh))
    lift = int(wing * 7)
    pygame.draw.ellipse(surf, BLUE_WING, (P(-10, -bh // 2 - 3 - lift)[0], P(-10, -bh // 2 - 3 - lift)[1], int(38 * sq), 18))
    if band:
        pygame.draw.line(surf, band, P(20, -bh // 2 + 7), P(34, -bh // 2 + 5), 5)
    pygame.draw.circle(surf, WHITE, P(26, -3), 7)
    pygame.draw.circle(surf, INK, P(28, -3), 3)
    pygame.draw.circle(surf, WHITE, P(29, -4), 1)
    _smooth(surf, color, [P(28, -9), P(40, -22), P(52, -38), P(60, -52)], 3)
    _smooth(surf, color, [P(26, -7), P(34, -16), P(44, -28), P(50, -42)], 3)
    pygame.draw.circle(surf, color, P(60, -52), 3)
    pygame.draw.circle(surf, color, P(50, -42), 3)
    if rot:
        surf = pygame.transform.rotate(surf, -rot)
    target.blit(surf, surf.get_rect(center=(cx, cy)))


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "col", "r")

    def __init__(self, x, y, col):
        a = random.uniform(0, math.tau)
        s = random.uniform(70, 270)
        self.x, self.y, self.vx, self.vy = x, y, math.cos(a) * s, math.sin(a) * s - 70
        self.life, self.col, self.r = random.uniform(0.35, 0.75), col, random.randint(3, 6)

    def update(self, dt):
        self.life -= dt
        self.vy += 900 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, s):
        if self.life > 0:
            pygame.draw.circle(s, self.col, (int(self.x), int(self.y)), self.r)


class Cloud:
    def __init__(self, w):
        self.w = w
        self.x = random.uniform(0, w)
        self.y = random.uniform(40, 220)
        self.sc = random.uniform(0.5, 1.0)
        self.sp = random.uniform(10, 24)

    def update(self, dt):
        self.x -= self.sp * dt
        if self.x < -140 * self.sc:
            self.x = self.w + 120 * self.sc
            self.y = random.uniform(40, 220)

    def draw(self, s):
        srf = pygame.Surface((int(200 * self.sc), int(110 * self.sc)), pygame.SRCALPHA)
        for dx, dy, r in [(55, 64, 38), (100, 50, 48), (145, 66, 36), (100, 74, 42)]:
            pygame.draw.circle(srf, (*WHITE, 160), (int(dx * self.sc), int(dy * self.sc)), int(r * self.sc))
        s.blit(srf, (self.x, self.y))


class World:
    """Một thế giới Flappy cho 1 người chơi, tự vẽ vào surface (vw, vh)."""

    def __init__(self, vw, vh, gaps, color, label, band=None, target=None, solo_hard=False):
        self.vw, self.vh = vw, vh
        self.gaps = gaps
        self.color, self.label, self.band = color, label, band
        self.target = target          # số cột để thắng (đấu); None = solo vô tận
        self.solo_hard = solo_hard
        self.bird_x = int(vw * 0.27)
        self.clouds = [Cloud(vw) for _ in range(3)]
        self.reset()

    def reset(self):
        self.y = self.vh / 2
        self.v = 0.0
        self.score = 0
        self.next_idx = 0
        self.pipes = []   # [x, gap_y, passed]
        self.particles = []
        self.squash = 1.0
        self.wing = 0.0
        self.rot = 0.0
        self.scroll = 0.0
        self.stun = 0.0
        self.invuln = 0.0
        self.dead = False
        self.finished = False

    @property
    def speed(self):
        return BASE_SPEED + (self.score * SPEED_PER_POINT if self.solo_hard else 0)

    @property
    def gap(self):
        if self.target is not None:
            return DUEL_GAP
        return max(140, SOLO_GAP0 - self.score * 2)

    def flap(self):
        if self.dead or self.finished or self.stun > 0:
            return
        self.v = FLAP_V
        self.squash = 0.62
        self.wing = 1.0
        for _ in range(5):
            self.particles.append(Particle(self.bird_x + 14, self.y + 14, BLUE_CYAN))

    def _spawn(self):
        gy = self.gaps[self.next_idx % len(self.gaps)]
        gy = max(100 + self.gap // 2, min(self.vh - GROUND_H - 100 - self.gap // 2, gy))
        self.pipes.append([self.vw + PIPE_W, gy, False])
        self.next_idx += 1

    def update(self, dt):
        self.squash += (1.0 - self.squash) * min(1, dt * 12)
        self.wing = max(0.0, self.wing - dt * 6)
        for c in self.clouds:
            c.update(dt)
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        if self.finished or self.dead:
            return
        if self.invuln > 0:
            self.invuln -= dt
        if self.stun > 0:                 # choáng: đóng băng + bất tử, không rơi/va chạm
            self.stun -= dt
            self.v = 0
            self.rot = 0
            return
        self.scroll = (self.scroll + self.speed * dt) % 48
        self.v += GRAVITY * dt
        self.y += self.v * dt
        self.rot = max(-22, min(70, self.v * 0.07))

        if not self.pipes or self.pipes[-1][0] < self.vw - PIPE_SPACING:
            self._spawn()
        for pipe in self.pipes:
            pipe[0] -= self.speed * dt
            if not pipe[2] and pipe[0] + PIPE_W < self.bird_x:
                pipe[2] = True
                self.score += 1
                for _ in range(10):
                    self.particles.append(Particle(self.bird_x, self.y, GREEN_LIME))
                if self.target and self.score >= self.target:
                    self.finished = True
        self.pipes = [p for p in self.pipes if p[0] > -PIPE_W]

        if self.invuln <= 0 and self._hit():
            self._on_hit()

    def _hit(self):
        bx, by, br = self.bird_x, self.y, 16
        if by - br < 0 or by + br > self.vh - GROUND_H:
            return True
        for px, gy, _ in self.pipes:
            if px < bx + br and px + PIPE_W > bx - br:
                if by - br < gy - self.gap // 2 or by + br > gy + self.gap // 2:
                    return True
        return False

    def _on_hit(self):
        for _ in range(30):
            self.particles.append(Particle(self.bird_x, self.y, random.choice([ORANGE_HOT, PINK_HOT, GREEN_LIME])))
        if self.target is not None:      # đấu: choáng rồi chơi tiếp
            self.stun = STUN_TIME
            self.invuln = STUN_TIME + 0.5  # bất tử thêm 0.5s sau khi tỉnh để thoát cột
            self.v = 0
            self.y = self.vh / 2
            for p in self.pipes:          # lùi nhẹ → mất thời gian
                p[0] += 70
        else:                             # solo: chết
            self.dead = True

    def render(self, surf):
        surf.blit(make_sky(self.vw, self.vh), (0, 0))
        for c in self.clouds:
            c.draw(surf)
        for px, gy, _ in self.pipes:
            self._reed(surf, px, gy)
        # đất
        top = self.vh - GROUND_H
        pygame.draw.rect(surf, GREEN_CRICKET, (0, top, self.vw, GROUND_H))
        pygame.draw.rect(surf, GREEN_LIME, (0, top, self.vw, 9))
        for i in range(-1, self.vw // 48 + 2):
            x = i * 48 - self.scroll
            pygame.draw.polygon(surf, GREEN_LIME, [(x, top + 9), (x + 12, top - 6), (x + 24, top + 9)])
        for p in self.particles:
            p.draw(surf)
        flash = self.stun > 0 and int(self.stun * 12) % 2 == 0
        if not flash:
            draw_cricket(surf, self.bird_x, self.y, self.color, self.squash, self.wing, self.rot, self.band)

    def _reed(self, surf, x, gy):
        half = self.gap // 2
        for is_top, rect in ((True, pygame.Rect(x, 0, PIPE_W, gy - half)),
                             (False, pygame.Rect(x, gy + half, PIPE_W, self.vh))):
            pygame.draw.rect(surf, GREEN_CRICKET, rect, border_radius=16)
            pygame.draw.rect(surf, GREEN_DEEP, (rect.x + 12, rect.y + (6 if is_top else 0), 12, rect.height - 6), border_radius=6)
            pygame.draw.rect(surf, GREEN_LIME, rect, width=4, border_radius=16)
            cap_y = gy - half - 20 if is_top else gy + half
            cap = pygame.Rect(x - 6, cap_y, PIPE_W + 12, 24)
            pygame.draw.rect(surf, GREEN_LIME, cap, border_radius=11)
            pygame.draw.rect(surf, GREEN_CRICKET, cap, width=3, border_radius=11)


class FlappyDe:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("FlappyDe — NeoArcade · Dế Foundation")
        self.clock = pygame.time.Clock()
        self.f_hero = font(76)
        self.f_big = font(46)
        self.f_md = font(26)
        self.f_sm = font(18)
        self.best = 0
        logo = load_logo()
        self.logo_big = scale_to(logo, w=250) if logo else None     # menu
        self.logo_sm = scale_to(logo, h=24) if logo else None       # watermark
        self.menu_clouds = [Cloud(W) for _ in range(4)]
        self.state = "menu"   # menu | countdown | play | result
        self.mode = None      # solo | duel
        self.count = 0.0
        self.result = ""

    # ---- bố cục ----
    def _new_gaps(self):
        rnd = random.Random(20260612 + (self.best * 7))
        return [rnd.randint(150, H - GROUND_H - 150) for _ in range(DUEL_TARGET + 6)]

    def start(self, mode):
        self.mode = mode
        gaps = self._new_gaps()
        if mode == "solo":
            self.worlds = [World(W, H, gaps, BLUE_ELECTRIC, "Dế", target=None, solo_hard=True)]
        else:
            half = W // 2
            self.worlds = [
                World(half, H, gaps, BLUE_ELECTRIC, "P1", band=PINK_HOT, target=DUEL_TARGET),
                World(half, H, gaps, ORANGE_HOT, "P2", band=GREEN_LIME, target=DUEL_TARGET),
            ]
        self.subsurf = [pygame.Surface((w.vw, w.vh)) for w in self.worlds]
        self.count = 3.0
        self.state = "countdown"

    def flap(self, player):
        if self.state == "play" and player < len(self.worlds):
            self.worlds[player].flap()

    # ---- vòng lặp ----
    def update(self, dt):
        for c in self.menu_clouds:
            c.update(dt)
        if self.state == "countdown":
            for w in self.worlds:
                w.update(0)  # giữ animation nhẹ
            self.count -= dt
            if self.count <= 0:
                self.state = "play"
        elif self.state == "play":
            for w in self.worlds:
                w.update(dt)
            self._check_end()

    def _check_end(self):
        if self.mode == "solo":
            w = self.worlds[0]
            if w.dead:
                self.best = max(self.best, w.score)
                self.result = ("KỶ LỤC MỚI!" if w.score >= self.best and w.score > 0 else f"{w.score} điểm")
                self.state = "result"
        else:
            p1, p2 = self.worlds
            if p1.finished or p2.finished:
                self.result = "P1 THẮNG! 🎉" if p1.finished else "P2 THẮNG! 🎉"
                self.state = "result"

    def draw(self):
        s = self.screen
        if self.state == "menu":
            self._draw_menu()
        else:
            if self.mode == "solo":
                self.worlds[0].render(self.subsurf[0])
                s.blit(self.subsurf[0], (0, 0))
                self._hud_solo()
            else:
                for i, w in enumerate(self.worlds):
                    w.render(self.subsurf[i])
                    s.blit(self.subsurf[i], (i * (W // 2), 0))
                pygame.draw.line(s, WHITE, (W // 2, 0), (W // 2, H), 4)
                self._hud_duel()
            if self.state == "countdown":
                n = max(1, int(math.ceil(self.count)))
                self._center_text(self.f_hero, str(n), W // 2, H // 2, BLUE_ELECTRIC, panel=True)
            if self.state == "result":
                self._draw_result()
        self._wordmark()
        pygame.display.flip()

    def _draw_menu(self):
        s = self.screen
        s.blit(make_sky(W, H), (0, 0))
        for c in self.menu_clouds:
            c.draw(s)
        # logo Dế Foundation thật ở đỉnh
        if self.logo_big:
            s.blit(self.logo_big, self.logo_big.get_rect(center=(W // 2, 56)))
        else:
            self._center_text(self.f_sm, "Dế Foundation", W // 2, 50, BLUE_ELECTRIC)
        draw_cricket(s, W // 2 - 250, 158, BLUE_ELECTRIC, 1.0, 0.4, 8)
        draw_cricket(s, W // 2 + 250, 158, ORANGE_HOT, 1.0, 0.8, -8, band=GREEN_LIME)
        self._center_text(self.f_hero, "FlappyDe", W // 2, 148, BLUE_ELECTRIC)
        self._center_text(self.f_sm, "NeoArcade", W // 2, 198, GREEN_CRICKET)
        # 2 thẻ chế độ
        self._mode_card(W // 2 - 180, 322, "SOLO", "Đua bảng điểm", "Nhấn  SPACE", BLUE_ELECTRIC)
        self._mode_card(W // 2 + 180, 322, "ĐẤU 2 NGƯỜI", "Đua tới đích", "Nhấn  ENTER", ORANGE_HOT)
        self._center_text(self.f_sm, f"Điều khiển: {CONTROL_PROFILE}   ·   ESC để thoát", W // 2, H - 56, INK)

    def _mode_card(self, cx, cy, title, sub, key, accent):
        card = pygame.Rect(0, 0, 300, 180)
        card.center = (cx, cy)
        self._round(card, WHITE, accent, 5, 26)
        pygame.draw.circle(self.screen, BLUE_SOFT, (card.left + 26, card.top + 26), 13)
        pygame.draw.circle(self.screen, GREEN_LIME, (card.right - 24, card.bottom - 24), 11)
        self._center_text(self.f_big, title, cx, cy - 38, accent)
        self._center_text(self.f_md, sub, cx, cy + 6, INK)
        self._center_text(self.f_md, key, cx, cy + 48, GREEN_CRICKET)

    def _hud_solo(self):
        w = self.worlds[0]
        self._pill(W // 2, 56, str(w.score), BLUE_ELECTRIC)
        self._text(self.f_sm, f"Kỷ lục {self.best}", 20, 22, INK)

    def _hud_duel(self):
        half = W // 2
        for i, w in enumerate(self.worlds):
            x0 = i * half
            accent = BLUE_ELECTRIC if i == 0 else ORANGE_HOT
            # dải header gọn, nằm trong lề mỗi nửa (che phần trên cho sạch)
            strip = pygame.Rect(x0 + 10, 10, half - 20, 46)
            self._round(strip, (247, 247, 247, 235), accent, 4, 14)
            self._text(self.f_md, w.label, strip.left + 14, strip.top + 3, accent)
            sc = self.f_sm.render(f"{w.score}/{DUEL_TARGET} cột", True, INK)
            self.screen.blit(sc, (strip.right - 14 - sc.get_width(), strip.top + 8))
            # thanh tiến độ về đích (trong header)
            bar = pygame.Rect(strip.left + 14, strip.bottom - 15, strip.width - 28, 9)
            self._round(bar, BLUE_SOFT, None, 0, 5)
            fw = int(bar.width * min(1, w.score / DUEL_TARGET))
            if fw > 5:
                fb = bar.copy()
                fb.width = fw
                self._round(fb, accent, None, 0, 5)
            if w.stun > 0:
                self._center_text(self.f_md, "CHOÁNG!", x0 + half // 2, H // 2, PINK_HOT, panel=True)

    def _draw_result(self):
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((18, 26, 70, 120))
        self.screen.blit(ov, (0, 0))
        card = pygame.Rect(0, 0, 560, 240)
        card.center = (W // 2, H // 2)
        acc = ORANGE_HOT if ("THẮNG" in self.result or "KỶ LỤC" in self.result) else BLUE_ELECTRIC
        self._round(card, WHITE, acc, 5, 30)
        self._center_text(self.f_hero, self.result, W // 2, H // 2 - 40, acc)
        self._center_text(self.f_md, "SPACE chơi lại   ·   M về menu   ·   ESC thoát", W // 2, H // 2 + 50, INK)

    # ---- tiện ích vẽ ----
    def _round(self, rect, fill, border=None, bw=0, rad=16):
        pygame.draw.rect(self.screen, fill, rect, border_radius=rad)
        if border and bw:
            pygame.draw.rect(self.screen, border, rect, width=bw, border_radius=rad)

    def _pill(self, cx, cy, txt, color):
        img = self.f_big.render(txt, True, WHITE)
        r = img.get_rect(center=(cx, cy))
        pad = pygame.Rect(0, 0, max(r.width + 40, 78), 58)
        pad.center = (cx, cy)
        self._round(pad, color, WHITE, 4, 22)
        self.screen.blit(img, r)

    def _center_text(self, f, txt, x, y, col, panel=False):
        if panel:
            img = f.render(txt, True, col)
            r = img.get_rect(center=(x, y))
            pad = r.inflate(54, 30)
            self._round(pad, WHITE, col, 5, 22)
        self._text(f, txt, x, y, col, center=True)

    def _text(self, f, txt, x, y, col, center=False):
        sh = f.render(txt, True, (0, 0, 0))
        img = f.render(txt, True, col)
        r = img.get_rect()
        if center:
            r.center = (x, y)
        else:
            r.topleft = (x, y)
        self.screen.blit(sh, (r.x + 2, r.y + 2))
        self.screen.blit(img, r)

    def _wordmark(self):
        s = self.screen
        if self.logo_sm:
            lw, lh = self.logo_sm.get_size()
            txt = self.f_sm.render("FlappyDe", True, INK)
            pill = pygame.Rect(14, H - 38, 12 + lw + 10 + txt.get_width() + 12, lh + 8)
            self._round(pill, WHITE, BLUE_ELECTRIC, 2, 13)
            s.blit(self.logo_sm, (pill.left + 12, pill.centery - lh // 2))
            s.blit(txt, (pill.left + 12 + lw + 10, pill.centery - txt.get_height() // 2))
        else:
            pill = pygame.Rect(14, H - 36, 220, 26)
            self._round(pill, WHITE, BLUE_ELECTRIC, 2, 13)
            self._text(self.f_sm, "FlappyDe · NeoArcade", pill.left + 14, pill.centery - 9, INK)

    # ---- input ----
    def on_key(self, key):
        if key == pygame.K_ESCAPE:
            return False
        if self.state == "menu":
            if key == pygame.K_SPACE:
                self.start("solo")
            elif key == pygame.K_RETURN:
                self.start("duel")
        elif self.state == "result":
            if key == pygame.K_SPACE:
                self.start(self.mode)
            elif key == pygame.K_m:
                self.state = "menu"
        else:  # countdown | play  → flap
            if key in (pygame.K_SPACE, pygame.K_w):
                self.flap(0)
            elif key in (pygame.K_RETURN, pygame.K_UP):
                self.flap(1)
        return True

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if not self.on_key(e.key):
                        running = False
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    FlappyDe().run()
