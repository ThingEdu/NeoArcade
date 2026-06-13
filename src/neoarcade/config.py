"""Hằng số game + bảng màu Dế Foundation. THUẦN — không import pygame."""

# ---- Khung hình ----
W, H = 900, 600
FPS = 60

# ---- Vật lý / luật chơi ----
GRAVITY = 1500.0
FLAP_V = -420.0
BIRD_R = 16
PIPE_W = 84
PIPE_SPACING = 270
GROUND_H = 80
BASE_SPEED = 220.0
SPEED_PER_POINT = 6.0

# ---- Bắt Dế (camera + bàn tay) ----
CATCH_FLOCK = 8           # số Dế giữ trên màn (đàn = cluster)
CATCH_R = 48              # bán kính bắt (tay chạm Dế)
FLEE_R = 125              # Dế bỏ chạy khi tay tới gần
CRICKET_SPEED = 140.0     # tốc độ lang thang
CRICKET_FLEE = 330.0      # tốc độ bỏ chạy
CATCH_TIME = 45.0         # giây mỗi lượt

# ---- Đua Xe Dế (top-down lane runner) ----
CAR_W, CAR_H = 50, 78
ROAD_W = 330              # bề rộng MẶT ĐƯỜNG cố định (căn giữa, KHÔNG theo bề rộng màn)
STEER_SPEED = 360.0       # px/s khi cần lái = ±1
RACE_SPEED = 300.0        # tốc độ tiến (px/s)
RACE_SPEED_PER = 0.06     # solo: nhanh dần theo quãng đường
RACE_TARGET = 7200        # quãng đường về đích khi đấu (px)
RACE_STUN = 1.0           # xoay vòng khi đụng (đấu)
RACE_INVULN_EXTRA = 0.6
OBSTACLE_W, OBSTACLE_H = 78, 50   # to gần kín làn → không đậu khe né được
ENERGY_R = 15
SPAWN_GAP = 200           # khoảng cách dọc giữa các hàng vật thể (px)

# ---- Bóng Rổ Dế (ném canh lực — nút bấm) ----
BR_TIME = 45.0            # giây mỗi lượt
BR_LAUNCH_X = 110         # vị trí ném (trái dưới)
BR_RANGE = 660            # tầm xa khi lực = 1.0
BR_HOOP_MIN, BR_HOOP_MAX = 430, 760   # rổ ở khoảng cách ngẫu nhiên
BR_POWER_TOL = 0.05       # sai số lực để VÀO rổ
BR_OSC = 1.3              # số chu kỳ dao động thanh lực / giây
BR_SHOT_ANIM = 0.7        # thời gian bóng bay

# ---- Đấm Bốc (đập nút thử lực / đẩy đối thủ) ----
BX_TIME = 6.0             # solo: cửa sổ thử lực (giây)
BX_GAIN = 7.0            # lực cộng mỗi cú đấm
BX_DECAY = 26.0          # lực tụt / giây (phải đấm nhanh)
BX_DUEL_TIME = 40.0
BX_PUSH_STEP = 4.0       # đấu: đẩy vạch mỗi cú đấm
BX_PUSH_DECAY = 11.0     # đấu: vạch trôi về giữa / giây
BX_WIN = 100.0          # đấu: đẩy tới ±100 = thắng

DUEL_TARGET = 18          # số cột để về đích (đấu 2 người)
DUEL_GAP = 195            # khe cố định khi đấu (công bằng)
SOLO_GAP0 = 205           # khe ban đầu solo (hẹp dần)
SOLO_GAP_MIN = 140
STUN_TIME = 1.2          # choáng khi va chạm (đấu)
INVULN_EXTRA = 0.5       # bất tử thêm sau khi tỉnh
HIT_PUSHBACK = 70        # lùi cột khi va chạm (đấu)
COUNTDOWN = 3.0

# ---- Bảng màu Dế Foundation (DE STEM) ----
BLUE_ELECTRIC = (35, 71, 251)    # #2347FB
BLUE_WING = (104, 134, 252)
BLUE_CYAN = (148, 246, 255)      # #94F6FF
BLUE_SOFT = (216, 239, 255)      # #D8EFFF
PINK_HOT = (215, 29, 144)        # #D71D90
ORANGE_HOT = (231, 77, 30)       # #E74D1E
ORANGE_WARM = (240, 112, 32)     # #F07020
GREEN_CRICKET = (12, 112, 105)   # #0C7069
GREEN_DEEP = (9, 84, 78)
GREEN_LIME = (213, 242, 68)      # #D5F244
GREEN_SOFT = (241, 255, 211)     # #F1FFD3
INK = (18, 18, 18)
WHITE = (247, 247, 247)
