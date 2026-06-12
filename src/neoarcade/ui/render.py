"""Lớp vẽ pygame: nền/cột/HUD/menu + hiệu ứng. Đọc trạng thái từ Controller (thuần)."""
from __future__ import annotations

import math
import random

import pygame

from neoarcade import config as C
from neoarcade.ui.sprites import draw_cricket, font, load_logo, scale_to

_sky_cache: dict = {}


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_sky(w, h):
    key = (w, h)
    if key not in _sky_cache:
        s = pygame.Surface((w, h))
        for y in range(h):
            s.fill(lerp(C.BLUE_CYAN, C.BLUE_SOFT, (y / h) ** 0.8), (0, y, w, 1))
        if w >= 700:   # mặt trời chỉ ở màn lớn (menu/solo)
            pygame.draw.circle(s, C.ORANGE_WARM, (w - 70, 70), 38)
            pygame.draw.circle(s, C.ORANGE_HOT, (w - 70, 70), 52, 6)
        _sky_cache[key] = s
    return _sky_cache[key]


class Cloud:
    def __init__(self, w):
        self.w = w
        self.x = random.uniform(0, w)
        self.y = random.uniform(40, 230)
        self.sc = random.uniform(0.5, 1.0)
        self.sp = random.uniform(10, 24)

    def update(self, dt):
        self.x -= self.sp * dt
        if self.x < -150 * self.sc:
            self.x = self.w + 120 * self.sc
            self.y = random.uniform(40, 230)

    def draw(self, s):
        srf = pygame.Surface((int(200 * self.sc), int(110 * self.sc)), pygame.SRCALPHA)
        for dx, dy, r in [(55, 64, 38), (100, 50, 48), (145, 66, 36), (100, 74, 42)]:
            pygame.draw.circle(srf, (*C.WHITE, 160), (int(dx * self.sc), int(dy * self.sc)), int(r * self.sc))
        s.blit(srf, (self.x, self.y))


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "col", "r")

    def __init__(self, x, y, col):
        a = random.uniform(0, math.tau)
        sp = random.uniform(70, 270)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * sp, math.sin(a) * sp - 70
        self.life, self.col, self.r = random.uniform(0.35, 0.75), col, random.randint(3, 6)

    def update(self, dt):
        self.life -= dt
        self.vy += 900 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, s):
        if self.life > 0:
            pygame.draw.circle(s, self.col, (int(self.x), int(self.y)), self.r)


class WorldView:
    """Trạng thái hình ảnh cho 1 World: mây, hạt, squash, cánh, scroll."""

    def __init__(self, vw, vh, color, band=None):
        self.vw, self.vh = vw, vh
        self.color, self.band = color, band
        self.clouds = [Cloud(vw) for _ in range(3)]
        self.particles = []
        self.squash = 1.0
        self.wing = 0.0
        self.scroll = 0.0
        self.rot = 0.0

    def feed(self, dt, world, step, flapped, playing):
        self.squash += (1.0 - self.squash) * min(1, dt * 12)
        self.wing = max(0.0, self.wing - dt * 6)
        for c in self.clouds:
            c.update(dt)
        if flapped:
            self.squash, self.wing = 0.62, 1.0
            for _ in range(5):
                self.particles.append(Particle(world.bird_x + 14, world.y + 14, C.BLUE_CYAN))
        if step and step.passed:
            for _ in range(10):
                self.particles.append(Particle(world.bird_x, world.y, C.GREEN_LIME))
        if step and step.hit:
            for _ in range(34):
                self.particles.append(Particle(world.bird_x, world.y,
                                               random.choice([C.ORANGE_HOT, C.PINK_HOT, C.GREEN_LIME])))
        if playing and world.alive and not world.stunned:
            self.scroll = (self.scroll + world.speed * dt) % 48
            self.rot = max(-22, min(70, world.v * 0.07))
        else:
            self.rot = 0
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

    def render(self, surf, world):
        surf.blit(make_sky(self.vw, self.vh), (0, 0))
        for c in self.clouds:
            c.draw(surf)
        for px, gy, _ in world.pipes:
            self._reed(surf, px, gy, world.gap)
        top = self.vh - C.GROUND_H
        pygame.draw.rect(surf, C.GREEN_CRICKET, (0, top, self.vw, C.GROUND_H))
        pygame.draw.rect(surf, C.GREEN_LIME, (0, top, self.vw, 9))
        for i in range(-1, self.vw // 48 + 2):
            x = i * 48 - self.scroll
            pygame.draw.polygon(surf, C.GREEN_LIME, [(x, top + 9), (x + 12, top - 6), (x + 24, top + 9)])
        for p in self.particles:
            p.draw(surf)
        flash = world.stunned and int(world.stun * 12) % 2 == 0
        if not flash:
            draw_cricket(surf, world.bird_x, world.y, self.color, self.squash, self.wing, self.rot, self.band)

    def _reed(self, surf, x, gy, gap):
        half = gap // 2
        for is_top, rect in ((True, pygame.Rect(x, 0, C.PIPE_W, gy - half)),
                             (False, pygame.Rect(x, gy + half, C.PIPE_W, self.vh))):
            pygame.draw.rect(surf, C.GREEN_CRICKET, rect, border_radius=16)
            pygame.draw.rect(surf, C.GREEN_DEEP, (rect.x + 12, rect.y + (6 if is_top else 0), 12, rect.height - 6), border_radius=6)
            pygame.draw.rect(surf, C.GREEN_LIME, rect, width=4, border_radius=16)
            cap_y = gy - half - 20 if is_top else gy + half
            cap = pygame.Rect(x - 6, cap_y, C.PIPE_W + 12, 24)
            pygame.draw.rect(surf, C.GREEN_LIME, cap, border_radius=11)
            pygame.draw.rect(surf, C.GREEN_CRICKET, cap, width=3, border_radius=11)


class Renderer:
    def __init__(self, screen, profile_name="keyboard"):
        self.screen = screen
        self.profile_name = profile_name
        self.f_hero = font(76)
        self.f_big = font(46)
        self.f_md = font(26)
        self.f_sm = font(18)
        logo = load_logo()
        self.logo_big = scale_to(logo, w=250) if logo else None
        self.logo_sm = scale_to(logo, h=24) if logo else None
        self.menu_clouds = [Cloud(C.W) for _ in range(4)]
        self.views: list[WorldView] = []
        self._game_id = -1
        self.subsurf: list = []

    def _sync(self, ctrl):
        if ctrl.game_id != self._game_id or len(self.views) != len(ctrl.worlds):
            self._game_id = ctrl.game_id
            if ctrl.mode == "solo":
                self.views = [WorldView(C.W, C.H, C.BLUE_ELECTRIC)]
            else:
                half = C.W // 2
                self.views = [WorldView(half, C.H, C.BLUE_ELECTRIC, band=C.PINK_HOT),
                              WorldView(half, C.H, C.ORANGE_HOT, band=C.GREEN_LIME)]
            self.subsurf = [pygame.Surface((v.vw, v.vh)) for v in self.views]

    def draw(self, ctrl, ev, lb, dt):
        for c in self.menu_clouds:
            c.update(dt)
        if ctrl.state == ctrl.MENU:
            self._menu(ctrl, lb)
        else:
            self._sync(ctrl)
            playing = ctrl.state == ctrl.PLAY
            for i, (v, w) in enumerate(zip(self.views, ctrl.worlds)):
                step = ev.steps[i] if (playing and i < len(ev.steps)) else None
                flapped = ev.flapped[i] if i < len(ev.flapped) else False
                v.feed(dt, w, step, flapped, playing)
            if ctrl.mode == "solo":
                self.views[0].render(self.subsurf[0], ctrl.worlds[0])
                self.screen.blit(self.subsurf[0], (0, 0))
                self._pill(C.W // 2, 56, str(ctrl.worlds[0].score), C.BLUE_ELECTRIC)
                self._text(self.f_sm, f"Kỷ lục {ctrl.best}", 20, 22, C.INK)
            else:
                for i, v in enumerate(self.views):
                    v.render(self.subsurf[i], ctrl.worlds[i])
                    self.screen.blit(self.subsurf[i], (i * (C.W // 2), 0))
                pygame.draw.line(self.screen, C.WHITE, (C.W // 2, 0), (C.W // 2, C.H), 4)
                self._hud_duel(ctrl)
            if ctrl.state == ctrl.COUNTDOWN:
                n = ev.countdown_tick or 1
                self._center_text(self.f_hero, str(n), C.W // 2, C.H // 2, C.BLUE_ELECTRIC, panel=True)
            if ctrl.state == ctrl.RESULT:
                self._result(ctrl, lb)
        self._wordmark()

    # ---------- màn hình ----------
    def _menu(self, ctrl, lb):
        s = self.screen
        s.blit(make_sky(C.W, C.H), (0, 0))
        for c in self.menu_clouds:
            c.draw(s)
        if self.logo_big:
            s.blit(self.logo_big, self.logo_big.get_rect(center=(C.W // 2, 56)))
        draw_cricket(s, C.W // 2 - 250, 158, C.BLUE_ELECTRIC, 1.0, 0.4, 8)
        draw_cricket(s, C.W // 2 + 250, 158, C.ORANGE_HOT, 1.0, 0.8, -8, band=C.GREEN_LIME)
        self._center_text(self.f_hero, "FlappyDe", C.W // 2, 148, C.BLUE_ELECTRIC)
        self._center_text(self.f_sm, "NeoArcade", C.W // 2, 198, C.GREEN_CRICKET)
        self._mode_card(C.W // 2 - 180, 322, "SOLO", "Đua bảng điểm", "Nút 1 · SPACE", C.BLUE_ELECTRIC)
        self._mode_card(C.W // 2 + 180, 322, "ĐẤU 2 NGƯỜI", "Đua tới đích", "Nút 2 · ENTER", C.ORANGE_HOT)
        top = lb.top("solo", limit=3, today=True) if lb else []
        if top:
            txt = "TOP hôm nay:  " + "   ".join(f"{n} {sc}" for n, sc in top)
            self._center_text(self.f_sm, txt, C.W // 2, C.H - 92, C.INK)
        self._center_text(self.f_sm, f"Điều khiển: {self.profile_name}   ·   ESC để thoát", C.W // 2, C.H - 56, C.INK)

    def _mode_card(self, cx, cy, title, sub, key, accent):
        card = pygame.Rect(0, 0, 300, 170)
        card.center = (cx, cy)
        self._round(card, C.WHITE, accent, 5, 26)
        pygame.draw.circle(self.screen, C.BLUE_SOFT, (card.left + 26, card.top + 26), 13)
        pygame.draw.circle(self.screen, C.GREEN_LIME, (card.right - 24, card.bottom - 24), 11)
        self._center_text(self.f_big, title, cx, cy - 36, accent)
        self._center_text(self.f_md, sub, cx, cy + 6, C.INK)
        self._center_text(self.f_md, key, cx, cy + 46, C.GREEN_CRICKET)

    def _hud_duel(self, ctrl):
        half = C.W // 2
        for i, w in enumerate(ctrl.worlds):
            x0 = i * half
            accent = C.BLUE_ELECTRIC if i == 0 else C.ORANGE_HOT
            strip = pygame.Rect(x0 + 10, 10, half - 20, 46)
            self._round(strip, (247, 247, 247, 235), accent, 4, 14)
            self._text(self.f_md, f"P{i + 1}", strip.left + 14, strip.top + 3, accent)
            sc = self.f_sm.render(f"{w.score}/{C.DUEL_TARGET} cột", True, C.INK)
            self.screen.blit(sc, (strip.right - 14 - sc.get_width(), strip.top + 8))
            bar = pygame.Rect(strip.left + 14, strip.bottom - 15, strip.width - 28, 9)
            self._round(bar, C.BLUE_SOFT, None, 0, 5)
            fw = int(bar.width * min(1, w.score / C.DUEL_TARGET))
            if fw > 5:
                fb = bar.copy()
                fb.width = fw
                self._round(fb, accent, None, 0, 5)
            if w.stunned:
                self._center_text(self.f_md, "CHOÁNG!", x0 + half // 2, C.H // 2, C.PINK_HOT, panel=True)

    def _result(self, ctrl, lb):
        ov = pygame.Surface((C.W, C.H), pygame.SRCALPHA)
        ov.fill((18, 26, 70, 120))
        self.screen.blit(ov, (0, 0))
        card = pygame.Rect(0, 0, 560, 250)
        card.center = (C.W // 2, C.H // 2)
        win = "THẮNG" in ctrl.result
        acc = C.ORANGE_HOT if win else C.BLUE_ELECTRIC
        self._round(card, C.WHITE, acc, 5, 30)
        self._center_text(self.f_hero, ctrl.result, C.W // 2, C.H // 2 - 52, acc)
        if ctrl.mode == "solo" and lb:
            top = lb.top("solo", limit=3)
            if top:
                self._center_text(self.f_sm, "  ".join(f"{n} {sc}" for n, sc in top),
                                  C.W // 2, C.H // 2 + 6, C.GREEN_CRICKET)
        self._center_text(self.f_md, "Nút 1 chơi lại  ·  Nút 2 về menu  ·  ESC thoát",
                          C.W // 2, C.H // 2 + 56, C.INK)

    # ---------- tiện ích ----------
    def _round(self, rect, fill, border=None, bw=0, rad=16):
        if len(fill) == 4:
            srf = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(srf, fill, (0, 0, *rect.size), border_radius=rad)
            self.screen.blit(srf, rect.topleft)
        else:
            pygame.draw.rect(self.screen, fill, rect, border_radius=rad)
        if border and bw:
            pygame.draw.rect(self.screen, border, rect, width=bw, border_radius=rad)

    def _pill(self, cx, cy, txt, color):
        img = self.f_big.render(txt, True, C.WHITE)
        r = img.get_rect(center=(cx, cy))
        pad = pygame.Rect(0, 0, max(r.width + 40, 78), 58)
        pad.center = (cx, cy)
        self._round(pad, color, C.WHITE, 4, 22)
        self.screen.blit(img, r)

    def _center_text(self, f, txt, x, y, col, panel=False):
        if panel:
            img = f.render(txt, True, col)
            pad = img.get_rect(center=(x, y)).inflate(54, 30)
            self._round(pad, C.WHITE, col, 5, 22)
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
        if self.logo_sm:
            lw, lh = self.logo_sm.get_size()
            txt = self.f_sm.render("FlappyDe", True, C.INK)
            pill = pygame.Rect(14, C.H - 38, 12 + lw + 10 + txt.get_width() + 12, lh + 8)
            self._round(pill, C.WHITE, C.BLUE_ELECTRIC, 2, 13)
            self.screen.blit(self.logo_sm, (pill.left + 12, pill.centery - lh // 2))
            self.screen.blit(txt, (pill.left + 12 + lw + 10, pill.centery - txt.get_height() // 2))
        else:
            pill = pygame.Rect(14, C.H - 36, 220, 26)
            self._round(pill, C.WHITE, C.BLUE_ELECTRIC, 2, 13)
            self._text(self.f_sm, "FlappyDe · NeoArcade", pill.left + 14, pill.centery - 9, C.INK)
