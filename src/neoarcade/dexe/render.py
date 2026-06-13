"""Lớp vẽ Đua Xe Dế (pygame) — top-down "Thành phố Blue", cùng style Dế Foundation."""
from __future__ import annotations

import random

import pygame

from neoarcade import config as C
from neoarcade.ui.sprites import draw_cricket, font, load_logo, scale_to
from neoarcade.ui.widgets import (
    Particle,
    center_text,
    draw_text,
    mode_card,
    pill,
    round_rect,
    wordmark,
)

ROAD = (44, 56, 92)        # mặt nhựa xanh đậm
ROAD_EDGE = C.GREEN_LIME


class RaceRenderer:
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
        self._game_id = -1
        self.fx: list = []
        self.shake: list = []
        self.subsurf: list = []

    def _sync(self, ctrl):
        if ctrl.game_id != self._game_id or len(self.fx) != len(ctrl.worlds):
            self._game_id = ctrl.game_id
            self.fx = [[] for _ in ctrl.worlds]
            self.shake = [0.0 for _ in ctrl.worlds]
            self.subsurf = [pygame.Surface((w.vw, w.vh)) for w in ctrl.worlds]

    def draw(self, ctrl, ev, lb, dt):
        if ctrl.state == ctrl.MENU:
            self._menu(ctrl, lb)
            wordmark(self.screen, self.f_sm, self.logo_sm, "Đua Xe Dế · NeoArcade")
            return
        self._sync(ctrl)
        playing = ctrl.state == ctrl.PLAY
        half = C.W // 2
        for i, w in enumerate(ctrl.worlds):
            step = ev.steps[i] if (playing and i < len(ev.steps)) else None
            self._feed(i, w, step, dt)
            self._road(self.subsurf[i], w, self._accent(i), i)
            ox = int(random.uniform(-self.shake[i], self.shake[i])) if self.shake[i] else 0
            oy = int(random.uniform(-self.shake[i], self.shake[i])) if self.shake[i] else 0
            self.screen.blit(self.subsurf[i], (i * (half if ctrl.mode == "duel" else 0) + ox, oy))
        if ctrl.mode == "duel":
            pygame.draw.line(self.screen, C.WHITE, (half, 0), (half, C.H), 4)
            self._hud_duel(ctrl)
        else:
            self._hud_solo(ctrl)
        if ctrl.state == ctrl.COUNTDOWN:
            center_text(self.screen, self.f_hero, str(ev.countdown_tick or 1),
                        C.W // 2, C.H // 2, C.BLUE_ELECTRIC, panel=True)
        if ctrl.state == ctrl.RESULT:
            self._result(ctrl, lb)
        wordmark(self.screen, self.f_sm, self.logo_sm, "Đua Xe Dế · NeoArcade")

    def _accent(self, i):
        return C.BLUE_ELECTRIC if i == 0 else C.ORANGE_HOT

    # ---- hiệu ứng ----
    def _feed(self, idx, world, step, dt):
        fx = self.fx[idx]
        if step:
            if step.collected:
                for _ in range(8):
                    fx.append(Particle(world.x, world.car_y - 12, C.GREEN_LIME))
            if step.crashed:
                for _ in range(22):
                    fx.append(Particle(world.x, world.car_y,
                                       random.choice([C.ORANGE_HOT, C.PINK_HOT, C.WHITE])))
                self.shake[idx] = 14.0
        for p in fx:
            p.update(dt)
        self.fx[idx] = [p for p in fx if p.life > 0]
        self.shake[idx] = max(0.0, self.shake[idx] - dt * 60)

    # ---- cảnh đường ----
    def _road(self, surf, world, accent, idx):
        vw, vh = world.vw, world.vh
        surf.fill(C.GREEN_CRICKET)
        rl, rr = int(world.road_left), int(world.road_right)
        self._buildings(surf, world, 0, rl)
        self._buildings(surf, world, rr, vw)
        pygame.draw.rect(surf, ROAD, (rl, 0, rr - rl, vh))
        pygame.draw.rect(surf, ROAD_EDGE, (rl - 6, 0, 6, vh))
        pygame.draw.rect(surf, ROAD_EDGE, (rr, 0, 6, vh))
        lane_w = (rr - rl) / 3
        off = world.dist % 64
        for lane in (1, 2):
            x = rl + lane * lane_w
            y = -64 + off
            while y < vh:
                pygame.draw.rect(surf, C.WHITE, (int(x) - 3, int(y), 6, 36), border_radius=3)
                y += 64
        for d, kind, xf in self._items(world):
            self._item(surf, kind, world.item_x(xf), world.item_screen_y(d))
        flash = world.stunned and int(world.stun * 12) % 2 == 0
        if not flash:
            self._car(surf, world.x, world.car_y, accent)
        for p in self.fx[idx]:
            p.draw(surf)
        if world.stunned:
            center_text(surf, self.f_md, "XOAY!", vw // 2, vh // 2, C.PINK_HOT, panel=True)

    def _buildings(self, surf, world, x0, x1):
        pygame.draw.rect(surf, C.GREEN_CRICKET, (x0, 0, x1 - x0, world.vh))
        off = int(world.dist) % 120
        bw = max(20, x1 - x0 - 10)
        y = -120 + off
        while y < world.vh:
            b = pygame.Rect(x0 + 5, y + 12, bw, 92)
            round_rect(surf, b, C.BLUE_ELECTRIC, None, 0, 8)
            for wy in range(b.top + 10, b.bottom - 8, 20):
                for wx in range(b.left + 8, b.right - 6, 18):
                    pygame.draw.rect(surf, C.BLUE_CYAN, (wx, wy, 8, 8))
            y += 120

    def _items(self, world):
        for i, (d, kind, xf) in enumerate(world.sched):
            if world.taken[i]:
                continue
            y = world.item_screen_y(d)
            if -40 < y < world.vh + 40:
                yield d, kind, xf

    def _item(self, surf, kind, x, y):
        x, y = int(x), int(y)
        if kind == "energy":
            pygame.draw.circle(surf, C.GREEN_LIME, (x, y), C.ENERGY_R)
            pygame.draw.circle(surf, C.WHITE, (x, y), C.ENERGY_R - 5)
            pygame.draw.polygon(surf, C.GREEN_CRICKET,
                                [(x - 3, y - 7), (x + 3, y - 1), (x - 1, y - 1), (x + 3, y + 7), (x - 3, y + 1), (x + 1, y + 1)])
        else:
            pygame.draw.polygon(surf, C.ORANGE_HOT, [(x, y - 22), (x - 18, y + 18), (x + 18, y + 18)])
            pygame.draw.rect(surf, C.WHITE, (x - 11, y - 2, 22, 6))
            pygame.draw.rect(surf, C.ORANGE_WARM, (x - 20, y + 15, 40, 7), border_radius=3)

    def _car(self, surf, cx, cy, accent):
        cx, cy = int(cx), int(cy)
        w, h = C.CAR_W, C.CAR_H
        body = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        for wy in (cy - h // 2 + 8, cy + h // 2 - 22):
            pygame.draw.rect(surf, C.INK, (body.left - 5, wy, 6, 16), border_radius=3)
            pygame.draw.rect(surf, C.INK, (body.right - 1, wy, 6, 16), border_radius=3)
        round_rect(surf, body, accent, C.INK, 0, 14)
        pygame.draw.circle(surf, C.WHITE, (body.left + 9, body.top + 7), 4)
        pygame.draw.circle(surf, C.WHITE, (body.right - 9, body.top + 7), 4)
        ws = pygame.Rect(cx - w // 2 + 7, cy - h // 2 + 16, w - 14, 24)
        round_rect(surf, ws, C.BLUE_SOFT, None, 0, 8)
        # Dé tài xế: mắt + 2 râu vươn lên
        pygame.draw.circle(surf, C.WHITE, (cx - 6, ws.top + 12), 4)
        pygame.draw.circle(surf, C.INK, (cx - 6, ws.top + 12), 2)
        pygame.draw.circle(surf, C.WHITE, (cx + 6, ws.top + 12), 4)
        pygame.draw.circle(surf, C.INK, (cx + 6, ws.top + 12), 2)
        pygame.draw.line(surf, accent, (cx - 4, body.top + 4), (cx - 12, body.top - 12), 2)
        pygame.draw.line(surf, accent, (cx + 4, body.top + 4), (cx + 12, body.top - 12), 2)
        pygame.draw.circle(surf, accent, (cx - 12, body.top - 12), 2)
        pygame.draw.circle(surf, accent, (cx + 12, body.top - 12), 2)

    # ---- HUD / menu / kết quả ----
    def _menu(self, ctrl, lb):
        s = self.screen
        s.fill(C.GREEN_CRICKET)
        pygame.draw.rect(s, ROAD, (C.W // 2 - 150, 0, 300, C.H))
        for lane in (-50, 50):
            y = (pygame.time.get_ticks() // 10) % 64
            yy = -64 + y
            while yy < C.H:
                pygame.draw.rect(s, C.WHITE, (C.W // 2 + lane - 3, yy, 6, 36), border_radius=3)
                yy += 64
        if self.logo_big:
            s.blit(self.logo_big, self.logo_big.get_rect(center=(C.W // 2, 60)))
        draw_cricket(s, C.W // 2 - 250, 160, C.BLUE_ELECTRIC, 1.0, 0.4, 8)
        draw_cricket(s, C.W // 2 + 250, 160, C.ORANGE_HOT, 1.0, 0.8, -8, band=C.GREEN_LIME)
        center_text(s, self.f_hero, "Đua Xe Dế", C.W // 2, 150, C.BLUE_ELECTRIC)
        center_text(s, self.f_sm, "NeoArcade · hốt năng lượng Blue", C.W // 2, 200, C.GREEN_LIME)
        mode_card(s, self.f_big, self.f_md, C.W // 2 - 180, 330, "SOLO", "Đua điểm", "Nút 1 · SPACE", C.BLUE_ELECTRIC)
        mode_card(s, self.f_big, self.f_md, C.W // 2 + 180, 330, "ĐẤU 2 NGƯỜI", "Đua tới đích", "Nút 2 · ENTER", C.ORANGE_HOT)
        top = lb.top("dexe", limit=3) if lb else []
        if top:
            center_text(s, self.f_sm, "TOP: " + "   ".join(f"{n} {sc}" for n, sc in top),
                        C.W // 2, C.H - 92, C.WHITE)
        center_text(s, self.f_sm, f"Lái: A/D · ←/→   ·   {self.profile_name}   ·   ESC thoát",
                    C.W // 2, C.H - 56, C.WHITE)

    def _hud_solo(self, ctrl):
        w = ctrl.worlds[0]
        pill(self.screen, self.f_big, C.W // 2, 56, str(w.collected), C.GREEN_CRICKET)
        pygame.draw.circle(self.screen, C.GREEN_LIME, (C.W // 2 - 66, 56), 11)
        pygame.draw.circle(self.screen, C.WHITE, (C.W // 2 - 66, 56), 5)
        draw_text(self.screen, self.f_sm, f"Kỷ lục {ctrl.best}", 20, 22, C.WHITE)
        draw_text(self.screen, self.f_sm, f"{int(w.dist / 100)} m", C.W - 90, 22, C.WHITE)

    def _hud_duel(self, ctrl):
        half = C.W // 2
        for i, w in enumerate(ctrl.worlds):
            x0 = i * half
            accent = self._accent(i)
            strip = pygame.Rect(x0 + 10, 10, half - 20, 46)
            round_rect(self.screen, strip, (247, 247, 247, 235), accent, 4, 14)
            draw_text(self.screen, self.f_md, f"P{i + 1}", strip.left + 14, strip.top + 3, accent)
            sc = self.f_sm.render(f"{w.collected}", True, C.INK)
            self.screen.blit(sc, (strip.right - 14 - sc.get_width(), strip.top + 8))
            pygame.draw.circle(self.screen, C.GREEN_LIME,
                               (strip.right - 22 - sc.get_width(), strip.top + 16), 7)
            bar = pygame.Rect(strip.left + 14, strip.bottom - 15, strip.width - 28, 9)
            round_rect(self.screen, bar, C.BLUE_SOFT, None, 0, 5)
            fw = int(bar.width * w.progress)
            if fw > 5:
                fb = bar.copy()
                fb.width = fw
                round_rect(self.screen, fb, accent, None, 0, 5)

    def _result(self, ctrl, lb):
        ov = pygame.Surface((C.W, C.H), pygame.SRCALPHA)
        ov.fill((18, 26, 70, 120))
        self.screen.blit(ov, (0, 0))
        card = pygame.Rect(0, 0, 560, 250)
        card.center = (C.W // 2, C.H // 2)
        win = "ĐÍCH" in ctrl.result
        acc = C.ORANGE_HOT if win else C.BLUE_ELECTRIC
        round_rect(self.screen, card, C.WHITE, acc, 5, 30)
        center_text(self.screen, self.f_hero, ctrl.result, C.W // 2, C.H // 2 - 52, acc)
        if ctrl.mode == "solo" and lb:
            top = lb.top("dexe", limit=3)
            if top:
                center_text(self.screen, self.f_sm, "  ".join(f"{n} {sc}" for n, sc in top),
                            C.W // 2, C.H // 2 + 6, C.GREEN_CRICKET)
        center_text(self.screen, self.f_md, "Nút 1 chơi lại  ·  Nút 2 menu  ·  ESC thoát",
                    C.W // 2, C.H // 2 + 56, C.INK)
