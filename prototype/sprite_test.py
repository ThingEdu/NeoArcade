"""Thử sprite con Dế cho sát logo Dế Foundation — render PNG để soi."""
import math
import pygame

BLUE_ELECTRIC = (35, 71, 251)   # #2347FB (đúng logo)
BLUE_WING = (104, 134, 252)     # tint sáng cùng tông cho cánh (vẫn 'một màu')
BLUE_CYAN = (148, 246, 255)
BLUE_SOFT = (216, 239, 255)
INK = (18, 18, 18)
WHITE = (255, 255, 255)
PINK_HOT = (215, 29, 144)


def _smooth(surf, color, pts, width):
    """Vẽ đường cong mượt qua các điểm (Catmull-Rom đơn giản)."""
    out = []
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        for t in [j / 8 for j in range(9)]:
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if len(out) > 1:
        pygame.draw.lines(surf, color, False, out, width)


def draw_cricket(target, cx, cy, scale=1.0, color=BLUE_ELECTRIC,
                 squash=1.0, wing=0.0, rot=0.0, band=None):
    """Con Dế phẳng một-màu, quay phải: thân lá, đầu tròn + mắt trắng,
    2 râu dài cong, chân nhảy. Bám sát logo Dế Foundation."""
    S = 150
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cxl, cyl = 70, 80

    def P(x, y):
        return (cxl + x, cyl + y)

    sq = 0.82 + 0.18 * squash          # giảm biên độ méo
    bw = int(58 * sq)
    bh = int(32 / sq)

    # chân nhảy (hind leg) — nét đặc trưng con dế
    pygame.draw.line(surf, color, P(-8, 7), P(-26, 18), 8)
    pygame.draw.line(surf, color, P(-26, 18), P(-12, 25), 8)
    pygame.draw.line(surf, color, P(10, 11), P(8, 24), 4)      # chân trước

    # thân lá: đuôi nhọn trái + bầu phải (đầu)
    pygame.draw.polygon(surf, color, [P(-40, 1), P(-8, -bh // 2 + 3), P(-8, bh // 2 - 3)])
    pygame.draw.ellipse(surf, color, (P(-14, -bh // 2)[0], P(-14, -bh // 2)[1], bw, bh))

    # cánh: leaf cùng tông, nhấc nhẹ khi vỗ
    lift = int(wing * 7)
    ww = int(38 * sq)
    wr = (P(-10, -bh // 2 - 3 - lift)[0], P(-10, -bh // 2 - 3 - lift)[1], ww, 18)
    pygame.draw.ellipse(surf, BLUE_WING, wr)

    if band:  # băng đô thể thao mảnh (tuỳ chọn)
        pygame.draw.line(surf, band, P(20, -bh // 2 + 7), P(34, -bh // 2 + 5), 5)

    # mắt trắng + con ngươi (đầu bên phải)
    pygame.draw.circle(surf, WHITE, P(26, -3), 7)
    pygame.draw.circle(surf, INK, P(28, -3), 3)
    pygame.draw.circle(surf, WHITE, P(29, -4), 1)

    # 2 râu dài cong mượt vắt lên phải
    _smooth(surf, color, [P(28, -9), P(40, -22), P(52, -38), P(60, -52)], 3)
    _smooth(surf, color, [P(26, -7), P(34, -16), P(44, -28), P(50, -42)], 3)
    pygame.draw.circle(surf, color, P(60, -52), 3)
    pygame.draw.circle(surf, color, P(50, -42), 3)

    if rot:
        surf = pygame.transform.rotate(surf, -rot)
    target.blit(surf, surf.get_rect(center=(cx, cy)))


if __name__ == "__main__":
    pygame.init()
    # nền trắng — soi silhouette
    a = pygame.Surface((300, 200))
    a.fill(WHITE)
    draw_cricket(a, 150, 100, scale=1.4, squash=1.0, wing=0.0)
    pygame.image.save(a, "cricket_white.png")

    # nền trời sáng — kiểm tra tương phản + trạng thái vỗ cánh
    b = pygame.Surface((360, 200))
    for y in range(200):
        t = y / 200
        b.fill(tuple(int(BLUE_CYAN[i] + (BLUE_SOFT[i] - BLUE_CYAN[i]) * t) for i in range(3)), (0, y, 360, 1))
    draw_cricket(b, 110, 100, scale=1.3, wing=0.0, rot=10)
    draw_cricket(b, 250, 100, scale=1.3, squash=0.7, wing=1.0, rot=-18, band=PINK_HOT)
    pygame.image.save(b, "cricket_sky.png")
    print("saved cricket_white.png + cricket_sky.png")
