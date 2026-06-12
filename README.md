# NeoArcade

Bộ **game arcade "1 nút"** điều khiển bằng mạch **ThingBot ESP32**, chạy trên **NEO One** —
dành cho **Làng Maker** (ThingEdu). Giao diện theo bộ nhận diện **Dế Foundation (DE STEM)**.

NeoArcade là app launcher chứa nhiều game; mỗi game đóng gói riêng và được cập nhật dần.

## Sản phẩm

| # | Tên | Vận động | Input | Trạng thái |
|---|-----|----------|-------|-----------|
| 1 | **FlappyDe** | phản xạ/timing | nút bấm / nhảy | 🛠️ prototype |
| 2 | **Đua Xe Dế** | lái (vận động tinh) | cần analog | 💡 plan |
| 3 | **Bóng Rổ Dế** | ném/nhắm | cảm biến chạm | 💡 plan |
| 4 | **Đấm Sức Mạnh** | sức mạnh/bùng nổ | cảm biến rung | 💡 plan |
| 5 | **Bắt Dế** | cử chỉ tay/toàn thân | webcam + MediaPipe | 💡 plan |
| … | Nhảy Xa · Thăng Bằng · Nhịp · Nước Rút | phủ hết nhóm vận động | đa cảm biến | 💡 plan |

→ Chi tiết & lộ trình: [`docs/NeoArcade-Games-Roadmap.md`](docs/NeoArcade-Games-Roadmap.md)

Mỗi game = một loại vận động cho trẻ + một bài học **Blue Economy** (Dế Foundation, cùng vũ trụ với [DeBlue](https://deblue.vercel.app)).

## Điều khiển (control profiles)

Game chỉ nghe `flap(player)` — đổi nguồn không sửa logic:
- `keyboard` — bàn phím ngoài: **P1 = SPACE, P2 = ENTER** (demo/dự phòng). ✅
- `thingbot` — nút bấm mạch ThingBot ESP32 qua `neo-hw`. 🔜
- `jumppad` — nút cảm ứng, **học sinh nhảy lên để bay** (vận động thật). 🧪 tương lai

## Chạy prototype (Mac/NEO)

```bash
cd prototype
python3 -m venv .venv && .venv/bin/pip install pygame-ce
.venv/bin/python flappyde.py
```

`SPACE` = P1 vỗ cánh · `ENTER` = P2 (chế độ đấu) · `M` về menu · `ESC` thoát.

## Tài liệu
- [`docs/NeoArcade-Games-Roadmap.md`](docs/NeoArcade-Games-Roadmap.md) — kế hoạch bộ game vận động, map input ThingBot, lồng Blue Economy.
- [`docs/FlappyDe-design.md`](docs/FlappyDe-design.md) — thiết kế chi tiết FlappyDe, brand, kiến trúc.

## Ngăn xếp
Python 3.11+ · pygame-ce (render 60fps) · neo-hw (ThingBot/Simulator) · SQLite (leaderboard).
