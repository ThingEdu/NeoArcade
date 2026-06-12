"""Test hồ sơ điều khiển (mapping nút). Dùng event giả để khỏi cần màn hình."""
import pygame

from neoarcade.input.profiles import KeyboardProfile, get_profile


class FakeEvent:
    def __init__(self, type_, key):
        self.type = type_
        self.key = key


def test_keyboard_key_mapping():
    p = KeyboardProfile()
    assert p.button_for_key(pygame.K_SPACE) == 0
    assert p.button_for_key(pygame.K_w) == 0
    assert p.button_for_key(pygame.K_RETURN) == 1
    assert p.button_for_key(pygame.K_UP) == 1
    assert p.button_for_key(pygame.K_a) is None


def test_keyboard_buttons_from_events():
    p = KeyboardProfile()
    evs = [
        FakeEvent(pygame.KEYDOWN, pygame.K_SPACE),
        FakeEvent(pygame.KEYDOWN, pygame.K_RETURN),
        FakeEvent(pygame.KEYUP, pygame.K_SPACE),     # bỏ qua KEYUP
        FakeEvent(pygame.KEYDOWN, pygame.K_a),       # không map → bỏ
    ]
    assert p.buttons(evs) == [0, 1]


def test_get_profile_thingbot_falls_back_without_hardware():
    assert get_profile("thingbot").name == "keyboard"
    assert get_profile("keyboard").name == "keyboard"
