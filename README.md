# NeoArcade

Bộ **game arcade "1 nút"** điều khiển bằng mạch **ThingBot ESP32**, chạy trên **NEO One** —
dành cho **Làng Maker** (ThingEdu). Giao diện theo bộ nhận diện **Dế Foundation (DE STEM)**.

NeoArcade là app launcher chứa nhiều game; mỗi game đóng gói riêng và được cập nhật dần.

## Sản phẩm

| # | Tên | Vận động | Input | Trạng thái |
|---|-----|----------|-------|-----------|
| 1 | **FlappyDe** | phản xạ/timing | nút bấm / nhảy | ✅ hoàn thiện · 🤫 có bí mật ẩn (tự khám phá) |
| 2 | **Đua Xe Dế** | lái (vận động tinh) | cần analog / nút | 🛠️ prototype (engine+test) |
| 3 | **Bóng Rổ Dế** | ném/nhắm | nút canh lực (cảm biến chạm sau) | 🛠️ prototype (engine+test) |
| 4 | **Đấm Bốc** | sức mạnh/bùng nổ | đập nút (cảm biến rung sau) | 🛠️ prototype (engine+test) |
| … | Nhảy Xa · Thăng Bằng · Nhịp · Nước Rút | phủ hết nhóm vận động | đa cảm biến | 💡 plan |

> **Game camera (Bắt Dế, …) đã tách sang nền tảng riêng [NeoAiSport](https://github.com/ThingEdu/NeoAiSport)** —
> game thị giác AI (tay/cử chỉ/mặt/tư thế) có stack riêng (opencv + mediapipe) để NeoArcade nhẹ, hợp NEO cấu hình thấp.

→ Chi tiết & lộ trình: [`docs/NeoArcade-Games-Roadmap.md`](docs/NeoArcade-Games-Roadmap.md)

Mỗi game = một loại vận động cho trẻ + một bài học **Blue Economy** (Dế Foundation, cùng vũ trụ với [DeBlue](https://deblue.vercel.app)).

## Điều khiển (control profiles)

Game chỉ nghe `flap(player)` — đổi nguồn không sửa logic:
- `keyboard` — bàn phím ngoài: **P1 = SPACE, P2 = ENTER** (demo/dự phòng). ✅
- `thingbot` — nút bấm mạch ThingBot ESP32 qua `neo-hw`. 🔜
- `jumppad` — nút cảm ứng, **học sinh nhảy lên để bay** (vận động thật). 🧪 tương lai

## Chạy FlappyDe (bản hoàn thiện)

```bash
make install     # tạo .venv + cài package (editable) + dev deps
make hub         # màn tổng — chọn game
make run-sim     # FlappyDe bằng bàn phím
make run-dexe    # Đua Xe Dế bằng bàn phím (lái A/D, ←/→)
make run         # FlappyDe với ThingBot (tự fallback bàn phím nếu thiếu phần cứng)
make run-bongro  # Bóng Rổ Dế (canh lực)
make run-damboc  # Đấm Bốc (đập nút)
make test        # 53 test (engine/storage/input/controller × 4 game)
```
Hoặc: `python -m neoarcade.hub` · `… .app` · `… .dexe.app`

**2 nút (khớp ThingBot)** — Nút 1 = `SPACE`/`W`, Nút 2 = `ENTER`/`↑`, `ESC` thoát.
Menu: Nút1 = Solo, Nút2 = Đấu · Trong trận: Nút1 = P1, Nút2 = P2 · Kết quả: Nút1 = chơi lại, Nút2 = menu.

## Cấu trúc

```
src/neoarcade/
  config.py            # hằng số + palette (thuần)
  engine/              # FlappyDe LÕI THUẦN: world.py + game.py — test 100%
  dexe/                # Đua Xe Dế: world.py + game.py (thuần) + render.py + app.py
  input/profiles.py    # điều khiển: keyboard / thingbot (neo-hw) / jumppad + steer (lái)
  storage/db.py        # leaderboard SQLite (dùng chung)
  ui/                  # pygame: sprites (con Dế), widgets (style dùng chung), render, sound
  app.py               # FlappyDe — vòng lặp
tests/                 # pytest (41 test)
prototype/             # bản 1-file gốc (tham khảo)
```

## Tài liệu
- [`docs/NEO-ONE-INSTALL.md`](docs/NEO-ONE-INSTALL.md) — **cài đặt & chạy trên NEO One** (ARM64/Armbian).
- [`docs/NeoArcade-Games-Roadmap.md`](docs/NeoArcade-Games-Roadmap.md) — kế hoạch bộ game vận động, map input ThingBot, lồng Blue Economy.
- [`docs/FlappyDe-design.md`](docs/FlappyDe-design.md) — thiết kế chi tiết FlappyDe, brand, kiến trúc.

## Ngăn xếp
Python 3.11+ · pygame-ce (render 60fps) · neo-hw (ThingBot/Simulator) · SQLite (leaderboard).
