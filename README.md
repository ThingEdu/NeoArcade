# NeoArcade

Bộ **game arcade "1 nút"** điều khiển bằng mạch **ThingBot ESP32**, chạy trên **NEO One** —
dành cho **Làng Maker** (ThingEdu). Giao diện theo bộ nhận diện **Dế Foundation (DE STEM)**.

NeoArcade là app launcher chứa nhiều game; mỗi game đóng gói riêng và được cập nhật dần.

## Sản phẩm

| # | Tên | Mô tả | Trạng thái |
|---|-----|-------|-----------|
| 1 | **FlappyDe** | Con Dế vỗ cánh né sậy. SOLO (đua điểm) + ĐẤU 2 NGƯỜI (đua tới đích). | 🛠️ prototype |
| 2 | _(dự kiến)_ Sút Luân Lưu / Nước Rút… | thêm sau | 💡 ý tưởng |

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
- [`docs/FlappyDe-design.md`](docs/FlappyDe-design.md) — thiết kế chi tiết, brand, kiến trúc, lộ trình.

## Ngăn xếp
Python 3.11+ · pygame-ce (render 60fps) · neo-hw (ThingBot/Simulator) · SQLite (leaderboard).
