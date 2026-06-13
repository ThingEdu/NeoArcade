"""NeoArcade — màn hình tổng (launcher): chọn 1 trong các game rồi mở.

Mỗi game chạy ở TIẾN TRÌNH RIÊNG (cô lập camera/cv2/pygame); thoát game (ESC)
sẽ quay về màn này.

  ← → (hoặc A/D) chọn · ENTER/SPACE chơi · ESC thoát · hoặc bấm chuột vào thẻ.
"""
from __future__ import annotations

import math
import subprocess
import sys

import pygame

from neoarcade import config as C
from neoarcade.ui.render import make_sky
from neoarcade.ui.sprites import draw_cricket, font, load_logo, scale_to
from neoarcade.ui.widgets import center_text, round_rect, wordmark

GAMES = [
    dict(title="FlappyDe", move="Phản xạ · 1 nút", control="Nút bấm / nhảy",
         module="neoarcade.app", args=["--profile", "keyboard"],
         accent=C.BLUE_ELECTRIC, icon="cricket"),
    dict(title="Đua Xe Dế", move="Lái né · vận động tinh", control="Cần lái / nút",
         module="neoarcade.dexe.app", args=["--profile", "keyboard"],
         accent=C.ORANGE_HOT, icon="car"),
]
# Game camera (Bắt Dế, …) đã tách sang nền tảng riêng NeoAiSport (github.com/ThingEdu/NeoAiSport).

TW, TH, GAP = 250, 310, 28


class Hub:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.W, C.H))
        pygame.display.set_caption("NeoArcade — Dế Foundation")
        self.clock = pygame.time.Clock()
        self.f_hero = font(72)
        self.f_big = font(34)
        self.f_md = font(24)
        self.f_sm = font(18)
        logo = load_logo()
        self.logo_big = scale_to(logo, w=250) if logo else None
        self.logo_sm = scale_to(logo, h=24) if logo else None
        self.sel = 0
        self.t = 0.0

    def _tiles_x0(self):
        n = len(GAMES)
        return (C.W - (n * TW + (n - 1) * GAP)) // 2

    def _tile_rect(self, i):
        return pygame.Rect(self._tiles_x0() + i * (TW + GAP), 240, TW, TH)

    def _tile_at(self, pos):
        for i in range(len(GAMES)):
            if self._tile_rect(i).collidepoint(pos):
                return i
        return None

    def launch(self, game):
        pygame.display.iconify()
        try:
            subprocess.run([sys.executable, "-m", game["module"], *game["args"]])
        except Exception as exc:
            print(f"[hub] không mở được {game['title']}: {exc}")
        self.screen = pygame.display.set_mode((C.W, C.H))   # khôi phục cửa sổ hub
        pygame.event.clear()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(C.FPS) / 1000.0
            self.t += dt
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                    elif e.key in (pygame.K_LEFT, pygame.K_a):
                        self.sel = (self.sel - 1) % len(GAMES)
                    elif e.key in (pygame.K_RIGHT, pygame.K_d):
                        self.sel = (self.sel + 1) % len(GAMES)
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                        self.launch(GAMES[self.sel])
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    i = self._tile_at(e.pos)
                    if i is not None:
                        self.sel = i
                        self.launch(GAMES[i])
                elif e.type == pygame.MOUSEMOTION:
                    i = self._tile_at(e.pos)
                    if i is not None:
                        self.sel = i
            self.draw()
            pygame.display.flip()
        pygame.quit()

    # ---- vẽ ----
    def draw(self):
        s = self.screen
        s.blit(make_sky(C.W, C.H), (0, 0))
        # vài con Dế nhảy nền
        for k in range(3):
            x = (120 + k * 320 + int(self.t * 40)) % (C.W + 120) - 60
            y = 150 + int(18 * math.sin(self.t * 2 + k))
            draw_cricket(s, x, y, [C.BLUE_SOFT, C.GREEN_LIME, C.BLUE_CYAN][k], 1.0, 0.5, 6)
        if self.logo_big:
            s.blit(self.logo_big, self.logo_big.get_rect(center=(C.W // 2, 54)))
        center_text(s, self.f_hero, "NeoArcade", C.W // 2, 138, C.BLUE_ELECTRIC)
        center_text(s, self.f_sm, "Chọn trò chơi", C.W // 2, 188, C.GREEN_DEEP)
        for i, g in enumerate(GAMES):
            self._tile(i, g)
        center_text(s, self.f_sm, "A / D (hoặc chuột) chọn   ·   ENTER chơi   ·   ESC thoát",
                    C.W // 2, C.H - 38, C.INK)
        wordmark(s, self.f_sm, self.logo_sm, "NeoArcade")

    def _tile(self, i, g):
        s = self.screen
        r = self._tile_rect(i)
        active = i == self.sel
        if active:
            r = r.inflate(16, 16)
        round_rect(s, r, C.WHITE, g["accent"], 6 if active else 3, 26)
        pygame.draw.circle(s, C.BLUE_SOFT, (r.left + 24, r.top + 24), 12)
        pygame.draw.circle(s, C.GREEN_LIME, (r.right - 22, r.bottom - 22), 10)
        self._icon(g["icon"], r.centerx, r.top + 96, g["accent"])
        center_text(s, self.f_big, g["title"], r.centerx, r.top + 196, g["accent"])
        center_text(s, self.f_sm, g["move"], r.centerx, r.top + 232, C.INK)
        center_text(s, self.f_sm, g["control"], r.centerx, r.top + 256, C.GREEN_DEEP)
        if active:
            chip = pygame.Rect(0, 0, 150, 36)
            chip.center = (r.centerx, r.bottom - 26)
            round_rect(s, chip, g["accent"], None, 0, 18)
            center_text(s, self.f_sm, "CHƠI  ›", chip.centerx, chip.centery, C.WHITE)

    def _icon(self, kind, cx, cy, accent):
        s = self.screen
        if kind == "cricket":
            draw_cricket(s, cx, cy, accent, 1.0, 0.6 + 0.4 * math.sin(self.t * 6), 6)
        elif kind == "car":
            w, h = 46, 70
            body = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
            for wy in (cy - h // 2 + 8, cy + h // 2 - 20):
                pygame.draw.rect(s, C.INK, (body.left - 5, wy, 6, 15), border_radius=3)
                pygame.draw.rect(s, C.INK, (body.right - 1, wy, 6, 15), border_radius=3)
            round_rect(s, body, accent, C.INK, 0, 13)
            round_rect(s, pygame.Rect(cx - w // 2 + 7, cy - h // 2 + 14, w - 14, 22), C.BLUE_SOFT, None, 0, 8)
            pygame.draw.line(s, accent, (cx - 4, body.top + 2), (cx - 11, body.top - 12), 2)
            pygame.draw.line(s, accent, (cx + 4, body.top + 2), (cx + 11, body.top - 12), 2)
        else:  # hand: vòng bắt + con Dế
            draw_cricket(s, cx + 18, cy + 6, C.PINK_HOT, 1.0, 0.5, -8)
            r = 30 + int(3 * math.sin(self.t * 5))
            pygame.draw.circle(s, C.GREEN_LIME, (cx - 8, cy), r, 6)
            pygame.draw.circle(s, C.WHITE, (cx - 8, cy), r, 1)
            pygame.draw.circle(s, C.GREEN_LIME, (cx - 8, cy), 6)


def main():
    Hub().run()


if __name__ == "__main__":
    main()
