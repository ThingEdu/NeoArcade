"""Nguồn 'bàn tay' cho Bắt Dế.

  HandCamera : webcam + MediaPipe Hands (đầu ngón trỏ) → toạ độ tay (px), kèm khung hình.
  MouseHands : fallback dev/không camera — con trỏ chuột làm 1 bàn tay.

read() → (bg_surface | None, hands_px)  với hands_px = list[(x, y)] trong hệ C.W×C.H.
"""
from __future__ import annotations

import pygame

from neoarcade import config as C


class MouseHands:
    name = "mouse"
    has_camera = False

    def read(self):
        mx, my = pygame.mouse.get_pos()
        return None, [(float(mx), float(my))]

    def close(self):
        pass


class HandCamera:
    name = "camera"
    has_camera = True

    def __init__(self, max_hands: int = 2, cam: int = 0):
        # Import cv2/mediapipe Ở ĐÂY (sau pygame.init() của app) để SDL của pygame
        # nạp trước → cảnh báo "Class SDL... implemented in both" của macOS là VÔ HẠI:
        # ta chỉ dùng cv2 để đọc webcam, cửa sổ luôn là của pygame.
        import cv2
        import mediapipe as mp
        self.cv2 = cv2
        self.cap = cv2.VideoCapture(cam)
        if not self.cap.isOpened():
            raise RuntimeError("Không mở được webcam")
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=max_hands, model_complexity=0,
            min_detection_confidence=0.6, min_tracking_confidence=0.5)

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None, []
        frame = self.cv2.flip(frame, 1)                      # soi gương (selfie)
        rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)
        hands_px = []
        if res.multi_hand_landmarks:
            for lm in res.multi_hand_landmarks:
                tip = lm.landmark[8]                         # đầu ngón trỏ
                hands_px.append((tip.x * C.W, tip.y * C.H))
        surf = pygame.image.frombuffer(rgb.tobytes(), (rgb.shape[1], rgb.shape[0]), "RGB")
        if surf.get_size() != (C.W, C.H):
            surf = pygame.transform.smoothscale(surf, (C.W, C.H))
        return surf, hands_px

    def close(self):
        try:
            self.cap.release()
            self.hands.close()
        except Exception:
            pass


def get_hand_source(prefer: str = "camera", max_hands: int = 2):
    if prefer == "camera":
        try:
            return HandCamera(max_hands=max_hands)
        except Exception as exc:
            print(f"[vision] {exc} → fallback chuột (di chuột để bắt Dế)")
    return MouseHands()
