# NeoArcade

Bộ **game arcade "1 nút"** điều khiển bằng mạch **ThingBot ESP32**, chạy trên **NEO One** —
dành cho **Làng Maker** (ThingEdu). Giao diện theo bộ nhận diện **Dế Foundation (DE STEM)**.

NeoArcade là app launcher chứa nhiều game; mỗi game đóng gói riêng và được cập nhật dần.

## Sản phẩm

| # | Tên | Vận động | Input | Trạng thái |
|---|-----|----------|-------|-----------|
| 1 | **FlappyDe** | phản xạ/timing | nút bấm / nhảy | ✅ hoàn thiện (engine+test+leaderboard+âm thanh) |
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

## Chạy FlappyDe (bản hoàn thiện)

```bash
make install     # tạo .venv + cài package (editable) + dev deps
make run-sim     # chơi bằng bàn phím
make run         # chơi với ThingBot (tự fallback bàn phím nếu thiếu phần cứng)
make test        # 25 test (engine/storage/input/controller)
```
Hoặc: `.venv/bin/python -m neoarcade.app --profile keyboard`

**2 nút (khớp ThingBot)** — Nút 1 = `SPACE`/`W`, Nút 2 = `ENTER`/`↑`, `ESC` thoát.
Menu: Nút1 = Solo, Nút2 = Đấu · Trong trận: Nút1 = P1, Nút2 = P2 · Kết quả: Nút1 = chơi lại, Nút2 = menu.

## Cấu trúc

```
src/neoarcade/
  config.py            # hằng số + palette (thuần)
  engine/              # LÕI THUẦN: world.py (vật lý/va chạm/điểm), game.py (state machine) — test 100%
  input/profiles.py    # hồ sơ điều khiển: keyboard / thingbot (neo-hw) / jumppad
  storage/db.py        # leaderboard SQLite
  ui/                  # pygame: sprites (con Dế), render, sound (chip-tune tổng hợp)
  app.py               # vòng lặp ghép input·engine·ui·storage
tests/                 # pytest
prototype/             # bản 1-file gốc (tham khảo)
```

## Tài liệu
- [`docs/NeoArcade-Games-Roadmap.md`](docs/NeoArcade-Games-Roadmap.md) — kế hoạch bộ game vận động, map input ThingBot, lồng Blue Economy.
- [`docs/FlappyDe-design.md`](docs/FlappyDe-design.md) — thiết kế chi tiết FlappyDe, brand, kiến trúc.

## Ngăn xếp
Python 3.11+ · pygame-ce (render 60fps) · neo-hw (ThingBot/Simulator) · SQLite (leaderboard).
