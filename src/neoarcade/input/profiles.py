"""Hồ sơ điều khiển — chuẩn hoá mọi nguồn về "nút 0 / nút 1" (khớp ThingBot 2 nút).

Game/Controller chỉ nhận `press(btn)`; đổi profile KHÔNG sửa logic game.
  • keyboard : nút 0 = SPACE/W, nút 1 = ENTER/UP (demo/triển lãm, dự phòng).
  • thingbot : 2 nút trên mạch ThingBot ESP32 qua neo-hw (bản chính thức).
  • jumppad  : (tương lai) đế cảm ứng — học sinh nhảy lên để bấm nút 0.
"""
from __future__ import annotations

import pygame


class KeyboardProfile:
    name = "keyboard"
    KEY_TO_BTN = {
        pygame.K_SPACE: 0, pygame.K_w: 0,
        pygame.K_RETURN: 1, pygame.K_KP_ENTER: 1, pygame.K_UP: 1,
    }

    def button_for_key(self, key: int) -> int | None:
        return self.KEY_TO_BTN.get(key)

    def buttons(self, events) -> list[int]:
        """Trả về danh sách nút (0/1) vừa được nhấn trong khung này."""
        out = []
        for e in events:
            if e.type == pygame.KEYDOWN:
                b = self.KEY_TO_BTN.get(e.key)
                if b is not None:
                    out.append(b)
        return out


class ThingbotProfile:
    """Đọc 2 nút trên ThingBot qua neo-hw. Yêu cầu cài neo-hw + phần cứng."""
    name = "thingbot"

    def __init__(self, pin_map_path: str | None = None):
        try:
            from neo_hw import (  # type: ignore
                SimulatorBackend,
                TelemetrixBackend,
                find_thingbot_ports,
            )
        except Exception as exc:  # pragma: no cover - phụ thuộc phần cứng
            raise RuntimeError("Chưa cài neo-hw — không dùng được profile thingbot") from exc

        self._queue: list[int] = []
        ports = find_thingbot_ports()
        self.backend = (TelemetrixBackend(com_port=ports[0].device)
                        if ports else SimulatorBackend())
        # Map nút mạch → id 0/1 (đổi chân trong pin_map_path nếu cần).
        self._pins = {0: 4, 1: 5}
        for btn, pin in self._pins.items():
            self.backend.setup_input(pin)
            self.backend.register_callback(pin, lambda v, b=btn: self._queue.append(b) if v else None)

    def buttons(self, events) -> list[int]:  # events bỏ qua, đọc từ phần cứng
        out, self._queue = self._queue, []
        return out


def get_profile(name: str = "keyboard"):
    """Lấy profile theo tên; tự fallback về keyboard nếu thingbot không sẵn sàng."""
    if name == "thingbot":
        try:
            return ThingbotProfile()
        except Exception as exc:
            print(f"[input] {exc} → fallback keyboard")
            return KeyboardProfile()
    return KeyboardProfile()
