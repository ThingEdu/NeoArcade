"""Đấm Bốc — vòng lặp chính (nút bấm / ThingBot). python -m neoarcade.damboc.app"""
from __future__ import annotations

import argparse
import os

import pygame

from neoarcade import config as C
from neoarcade.damboc.game import BoxController
from neoarcade.damboc.render import BoxRenderer
from neoarcade.input.profiles import get_profile
from neoarcade.storage.db import Leaderboard
from neoarcade.ui.sound import SoundManager


def run(profile_name="keyboard", db_path="neoarcade.db", sound=True):
    pygame.init()
    screen = pygame.display.set_mode((C.W, C.H))
    pygame.display.set_caption("Đấm Bốc — NeoArcade · Dế Foundation")
    clock = pygame.time.Clock()
    lb = Leaderboard(db_path)
    ctrl = BoxController(leaderboard=lb)
    profile = get_profile(profile_name)
    renderer = BoxRenderer(screen, profile_name=profile.name)
    snd = SoundManager(enabled=sound)

    prev_tick, running = None, True
    while running:
        dt = min(clock.tick(C.FPS) / 1000.0, 0.05)
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
        for btn in profile.buttons(events):
            ctrl.press(btn)
        ev = ctrl.update(dt)
        for _pl in ev.punches:
            snd.play("hit")
        if ev.ended:
            snd.play("win")
        if ev.countdown_tick is not None and ev.countdown_tick != prev_tick:
            snd.play("count")
        prev_tick = ev.countdown_tick
        renderer.draw(ctrl, ev, lb, dt)
        pygame.display.flip()
    lb.close()
    pygame.quit()


def main():
    ap = argparse.ArgumentParser(description="Đấm Bốc — NeoArcade")
    ap.add_argument("--profile", default="keyboard", choices=["keyboard", "thingbot"])
    ap.add_argument("--db", default=os.environ.get("NEOARCADE_DB", "neoarcade.db"))
    ap.add_argument("--no-sound", action="store_true")
    args = ap.parse_args()
    run(profile_name=args.profile, db_path=args.db, sound=not args.no_sound)


if __name__ == "__main__":
    main()
