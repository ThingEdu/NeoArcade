"""Lớp vẽ Bóng Rổ Dế — rổ + Dế ném + thanh lực dao động (canh lực để VÀO)."""
from __future__ import annotations

import math

import pygame

from neoarcade import config as C
from neoarcade.ui.render import make_sky
from neoarcade.ui.sprites import draw_cricket, font, load_logo, scale_to
from neoarcade.ui.widgets import (
    Particle, center_text, draw_text, mode_card, pill, round_rect, wordmark,
)

FLOOR_Y = C.H - 96
BARW = 240


class BasketRenderer:
    def __init__(self, screen, profile_name="keyboard"):
        self.screen = screen
        self.profile_name = profile_name
        self.t = 0.0
        self.f_hero = font(72)
        self.f_big = font(46)
        self.f_md = font(26)
        self.f_sm = font(18)
        logo = load_logo()
        self.logo_big = scale_to(logo, w=250) if logo else None
        self.logo_sm = scale_to(logo, h=24) if logo else None
        self.sky = make_sky(C.W, C.H)
        self.fx = []

    def _cx(self, k, n):
        return C.W // 2 if n == 1 else (int(C.W * 0.28) if k == 0 else int(C.W * 0.72))

    def _hoop_y(self, ctrl, k):
        return 130 + int(self.required(ctrl, k) * 150)   # xa hơn = cao hơn

    def required(self, ctrl, k):
        return max(0.0, min(1.0, ctrl.required(k)))

    def draw(self, ctrl, ev, lb, dt):
        self.t += dt
        for k, made in ev.shots:
            cx = self._cx(k, ctrl._n())
            for _ in range(14):
                self.fx.append(Particle(cx, self._hoop_y(ctrl, k), C.ORANGE_HOT if made else C.PINK_HOT))
        for p in self.fx:
            p.update(dt)
        self.fx = [p for p in self.fx if p.life > 0]

        if ctrl.state == ctrl.MENU:
            self._menu(ctrl, lb)
            wordmark(self.screen, self.f_sm, self.logo_sm, "Bóng Rổ Dế · NeoArcade")
            return
        s = self.screen
        s.blit(self.sky, (0, 0))
        pygame.draw.rect(s, C.ORANGE_WARM, (0, FLOOR_Y, C.W, C.H - FLOOR_Y))
        pygame.draw.rect(s, C.ORANGE_HOT, (0, FLOOR_Y, C.W, 6))
        n = ctrl._n()
        for k in range(n):
            self._court(ctrl, k, n)
        for p in self.fx:
            p.draw(s)
        for k in range(n):
            self._bar(ctrl, k, n)
        if ctrl.state == ctrl.PLAY:
            self._hud(ctrl)
        if ctrl.state == ctrl.COUNTDOWN:
            center_text(s, self.f_hero, str(ev.countdown_tick or 1), C.W // 2, C.H // 2, C.BLUE_ELECTRIC, panel=True)
        if ctrl.state == ctrl.RESULT:
            self._result(ctrl)
        wordmark(s, self.f_sm, self.logo_sm, "Bóng Rổ Dế · NeoArcade")

    def _court(self, ctrl, k, n):
        s = self.screen
        cx = self._cx(k, n)
        hy = self._hoop_y(ctrl, k)
        accent = C.BLUE_ELECTRIC if (n == 1 or k == 0) else C.ORANGE_HOT
        # bảng rổ + vành + lưới
        pygame.draw.rect(s, C.WHITE, (cx - 4, hy - 60, 8, 60))
        pygame.draw.rect(s, C.WHITE, (cx - 40, hy - 60, 80, 56), 4)
        pygame.draw.ellipse(s, C.ORANGE_HOT, (cx - 34, hy - 6, 68, 16), 5)
        for dx in range(-30, 31, 12):
            pygame.draw.line(s, (255, 255, 255, 160), (cx + dx, hy), (cx + int(dx * 0.5), hy + 28), 1)
        # Dế ném
        draw_cricket(s, cx, FLOOR_Y - 24, accent, 1.0, 0.5, 0)
        # bóng
        if ctrl.ph[k] == "fly":
            t = 1 - ctrl.fly_t[k] / C.BR_SHOT_ANIM
            made = ctrl.shot_made[k]
            ty = hy + (40 if not made else 0)
            bx = cx + (0) * t
            by = (FLOOR_Y - 40) + (ty - (FLOOR_Y - 40)) * t - 120 * math.sin(math.pi * t)
            self._ball(bx, by)
            if t > 0.7:
                center_text(s, self.f_md, "VÀO!" if made else "trượt", cx, hy - 90,
                            C.ORANGE_HOT if made else C.PINK_HOT, panel=True)
        else:
            self._ball(cx, FLOOR_Y - 40)

    def _ball(self, x, y):
        x, y = int(x), int(y)
        pygame.draw.circle(self.screen, C.ORANGE_WARM, (x, y), 15)
        pygame.draw.circle(self.screen, C.INK, (x, y), 15, 2)
        pygame.draw.arc(self.screen, C.INK, (x - 15, y - 15, 30, 30), 0.4, 2.3, 2)

    def _bar(self, ctrl, k, n):
        s = self.screen
        cx = self._cx(k, n)
        accent = C.BLUE_ELECTRIC if (n == 1 or k == 0) else C.ORANGE_HOT
        bar = pygame.Rect(cx - BARW // 2, C.H - 50, BARW, 18)
        round_rect(s, bar, (255, 255, 255, 120), accent, 3, 9)
        # vùng mục tiêu (lực cần)
        req = self.required(ctrl, k)
        tol = C.BR_POWER_TOL
        zx = bar.left + int((req - tol) * BARW)
        round_rect(s, pygame.Rect(zx, bar.top, int(2 * tol * BARW), 18), C.GREEN_LIME, None, 0, 9)
        # con trỏ lực hiện tại
        px = bar.left + int(ctrl.power(k) * BARW)
        pygame.draw.rect(s, accent, (px - 3, bar.top - 4, 6, 26), border_radius=3)

    def _hud(self, ctrl):
        secs = max(0, int(ctrl.timer + 0.99))
        pill(self.screen, self.f_big, C.W // 2, 44, f"{secs}s", C.BLUE_ELECTRIC)
        if ctrl.mode == "solo":
            self._chip(20, 14, "Rổ", ctrl.baskets[0], C.ORANGE_HOT)
            draw_text(self.screen, self.f_sm, f"Kỷ lục {ctrl.best}", 24, 66, C.INK)
        else:
            self._chip(20, 14, "P1", ctrl.baskets[0], C.BLUE_ELECTRIC)
            self._chip(C.W - 150, 14, "P2", ctrl.baskets[1], C.ORANGE_HOT)

    def _chip(self, x, y, label, val, accent):
        r = pygame.Rect(x, y, 130, 44)
        round_rect(self.screen, r, (247, 247, 247, 235), accent, 4, 14)
        draw_text(self.screen, self.f_md, label, r.left + 12, r.top + 7, accent)
        num = self.f_md.render(str(val), True, C.INK)
        self.screen.blit(num, (r.right - 14 - num.get_width(), r.top + 7))

    def _menu(self, ctrl, lb):
        s = self.screen
        s.blit(self.sky, (0, 0))
        pygame.draw.rect(s, C.ORANGE_WARM, (0, FLOOR_Y, C.W, C.H - FLOOR_Y))
        if self.logo_big:
            s.blit(self.logo_big, self.logo_big.get_rect(center=(C.W // 2, 56)))
        self._ball(C.W // 2 - 250, 160)
        draw_cricket(s, C.W // 2 + 250, 158, C.ORANGE_HOT, 1.0, 0.7, -6)
        center_text(s, self.f_hero, "Bóng Rổ Dế", C.W // 2, 150, C.BLUE_ELECTRIC)
        center_text(s, self.f_sm, "NeoArcade · canh lực ném vào rổ", C.W // 2, 200, C.GREEN_CRICKET)
        mode_card(s, self.f_big, self.f_md, C.W // 2 - 180, 320, "SOLO", "Đua rổ 45s", "Nút 1 · SPACE", C.BLUE_ELECTRIC)
        mode_card(s, self.f_big, self.f_md, C.W // 2 + 180, 320, "ĐẤU 2 NGƯỜI", "Ai nhiều rổ hơn", "Nút 2 · ENTER", C.ORANGE_HOT)
        center_text(s, self.f_sm, f"Điều khiển: {self.profile_name}   ·   ESC thoát", C.W // 2, C.H - 86, C.INK)

    def _result(self, ctrl):
        ov = pygame.Surface((C.W, C.H), pygame.SRCALPHA)
        ov.fill((18, 26, 70, 130))
        self.screen.blit(ov, (0, 0))
        card = pygame.Rect(0, 0, 560, 240)
        card.center = (C.W // 2, C.H // 2)
        acc = C.ORANGE_HOT if "THẮNG" in ctrl.result else C.BLUE_ELECTRIC
        round_rect(self.screen, card, C.WHITE, acc, 5, 30)
        center_text(self.screen, self.f_hero, ctrl.result, C.W // 2, C.H // 2 - 46, acc)
        center_text(self.screen, self.f_md, "Nút 1 chơi lại  ·  Nút 2 menu  ·  ESC thoát",
                    C.W // 2, C.H // 2 + 52, C.INK)
