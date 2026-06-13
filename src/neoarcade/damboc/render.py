"""Lớp vẽ Đấm Bốc — solo: bao cát + đồng hồ lực; đấu: 2 võ sĩ đẩy vạch giữa."""
from __future__ import annotations

import math
import random

import pygame

from neoarcade import config as C
from neoarcade.ui.render import make_sky
from neoarcade.ui.sprites import draw_cricket, font, load_logo, scale_to
from neoarcade.ui.widgets import (
    Particle, center_text, draw_text, mode_card, pill, round_rect, wordmark,
)

FLOOR_Y = C.H - 90


class BoxRenderer:
    def __init__(self, screen, profile_name="keyboard"):
        self.screen = screen
        self.profile_name = profile_name
        self.t = 0.0
        self.shake = 0.0
        self.f_hero = font(72)
        self.f_big = font(46)
        self.f_md = font(26)
        self.f_sm = font(18)
        logo = load_logo()
        self.logo_big = scale_to(logo, w=250) if logo else None
        self.logo_sm = scale_to(logo, h=24) if logo else None
        self.sky = make_sky(C.W, C.H)
        self.fx = []

    def draw(self, ctrl, ev, lb, dt):
        self.t += dt
        self.shake = max(0.0, self.shake - dt * 50)
        for _pl in ev.punches:
            self.shake = 10.0
            for _ in range(6):
                self.fx.append(Particle(C.W // 2, C.H // 2, C.ORANGE_HOT))
        for p in self.fx:
            p.update(dt)
        self.fx = [p for p in self.fx if p.life > 0]

        if ctrl.state == ctrl.MENU:
            self._menu(ctrl, lb)
            wordmark(self.screen, self.f_sm, self.logo_sm, "Đấm Bốc · NeoArcade")
            return
        s = self.screen
        s.blit(self.sky, (0, 0))
        pygame.draw.rect(s, C.GREEN_CRICKET, (0, FLOOR_Y, C.W, C.H - FLOOR_Y))
        if ctrl.mode == "solo":
            self._solo(ctrl)
        else:
            self._duel(ctrl)
        if ctrl.state == ctrl.COUNTDOWN:
            center_text(s, self.f_hero, str(ev.countdown_tick or 1), C.W // 2, C.H // 2, C.BLUE_ELECTRIC, panel=True)
        if ctrl.state == ctrl.RESULT:
            self._result(ctrl)
        wordmark(s, self.f_sm, self.logo_sm, "Đấm Bốc · NeoArcade")

    # ---- SOLO: thử lực ----
    def _solo(self, ctrl):
        s = self.screen
        ox = int(random.uniform(-self.shake, self.shake))
        # bao cát
        bagx = C.W // 2 + ox
        pygame.draw.line(s, C.INK, (bagx, 60), (bagx, 110), 4)
        bag = pygame.Rect(bagx - 38, 110, 76, 200)
        round_rect(s, bag, C.ORANGE_HOT, C.ORANGE_WARM, 4, 26)
        for yy in range(150, 300, 40):
            pygame.draw.line(s, C.ORANGE_WARM, (bag.left, yy), (bag.right, yy), 3)
        draw_cricket(s, C.W // 2 - 130, FLOOR_Y - 30, C.BLUE_ELECTRIC, 1.0, 0.8, 6)
        for p in self.fx:
            p.draw(s)
        # đồng hồ lực (cột bên phải)
        meter = pygame.Rect(C.W - 120, 120, 56, 360)
        round_rect(s, meter, (255, 255, 255, 120), C.PINK_HOT, 3, 14)
        fh = int(meter.height * min(1.0, ctrl.power / 100))
        if fh > 4:
            round_rect(s, pygame.Rect(meter.left, meter.bottom - fh, meter.width, fh),
                       C.ORANGE_HOT, None, 0, 14)
        pky = meter.bottom - int(meter.height * min(1.0, ctrl.peak / 100))
        pygame.draw.line(s, C.PINK_HOT, (meter.left - 6, pky), (meter.right + 6, pky), 4)
        if ctrl.state == ctrl.PLAY:
            secs = max(0, int(ctrl.timer + 0.99))
            pill(s, self.f_big, C.W // 2, 40, f"{secs}s", C.BLUE_ELECTRIC)
            center_text(s, self.f_hero, f"{int(ctrl.power)}", C.W // 2, FLOOR_Y - 150, C.ORANGE_HOT)
            center_text(s, self.f_md, "ĐẤM NHANH! (đập nút)", C.W // 2, FLOOR_Y - 30, C.WHITE, panel=True)
            draw_text(s, self.f_sm, f"Kỷ lục {ctrl.best}", 20, 20, C.INK)

    # ---- ĐẤU: đẩy vạch ----
    def _duel(self, ctrl):
        s = self.screen
        p1x = 150 + int(ctrl.pos * 1.2)      # võ sĩ dịch theo vạch
        p2x = C.W - 150 + int(ctrl.pos * 1.2)
        draw_cricket(s, p1x, FLOOR_Y - 30, C.BLUE_ELECTRIC, 1.0, 0.8, 8)
        draw_cricket(s, p2x, FLOOR_Y - 30, C.ORANGE_HOT, 1.0, 0.8, -8)
        for p in self.fx:
            p.draw(s)
        # thanh đẩy
        bar = pygame.Rect(120, 150, C.W - 240, 30)
        round_rect(s, bar, (255, 255, 255, 140), C.INK, 3, 15)
        mid = bar.centerx + int(ctrl.pos / C.BX_WIN * (bar.width // 2))
        pygame.draw.rect(s, C.PINK_HOT, (mid - 6, bar.top - 8, 12, 46), border_radius=4)
        pygame.draw.line(s, C.BLUE_ELECTRIC, (bar.left, bar.top - 12), (bar.left, bar.bottom + 12), 4)
        pygame.draw.line(s, C.ORANGE_HOT, (bar.right, bar.top - 12), (bar.right, bar.bottom + 12), 4)
        if ctrl.state == ctrl.PLAY:
            secs = max(0, int(ctrl.timer + 0.99))
            pill(s, self.f_big, C.W // 2, 70, f"{secs}s", C.BLUE_ELECTRIC)
            draw_text(s, self.f_md, f"P1 {ctrl.punches[0]}", 30, 100, C.BLUE_ELECTRIC)
            t2 = self.f_md.render(f"P2 {ctrl.punches[1]}", True, C.ORANGE_HOT)
            s.blit(t2, (C.W - 30 - t2.get_width(), 100))
            center_text(s, self.f_md, "Đập nút đẩy đối thủ!", C.W // 2, FLOOR_Y + 30, C.WHITE)

    def _menu(self, ctrl, lb):
        s = self.screen
        s.blit(self.sky, (0, 0))
        pygame.draw.rect(s, C.GREEN_CRICKET, (0, FLOOR_Y, C.W, C.H - FLOOR_Y))
        if self.logo_big:
            s.blit(self.logo_big, self.logo_big.get_rect(center=(C.W // 2, 56)))
        draw_cricket(s, C.W // 2 - 250, 158, C.BLUE_ELECTRIC, 1.0, 0.8, 8)
        draw_cricket(s, C.W // 2 + 250, 158, C.ORANGE_HOT, 1.0, 0.8, -8)
        center_text(s, self.f_hero, "Đấm Bốc", C.W // 2, 150, C.BLUE_ELECTRIC)
        center_text(s, self.f_sm, "NeoArcade · đập nút thử lực / đẩy đối thủ", C.W // 2, 200, C.GREEN_CRICKET)
        mode_card(s, self.f_big, self.f_md, C.W // 2 - 180, 322, "SOLO", "Thử lực 6s", "Nút 1 · SPACE", C.BLUE_ELECTRIC)
        mode_card(s, self.f_big, self.f_md, C.W // 2 + 180, 322, "ĐẤU 2 NGƯỜI", "Đẩy đối thủ ngã", "Nút 2 · ENTER", C.ORANGE_HOT)
        center_text(s, self.f_sm, f"Điều khiển: {self.profile_name}   ·   ESC thoát", C.W // 2, C.H - 58, C.INK)

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
