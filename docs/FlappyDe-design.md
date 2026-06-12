# FlappyDe — Tài liệu thiết kế

> Game đầu tiên của bộ **NeoArcade** (ThingEdu). Cập nhật: 2026-06-12.

## 1. Tổng quan

**FlappyDe** là game arcade "1 nút" chạy trên **NEO One**, điều khiển bằng nút bấm
**ThingBot ESP32** (hoặc bàn phím ngoài). Người chơi điều khiển con **Dế** — mascot
của **Dế Foundation (DE STEM)** — vỗ cánh bay, né khe giữa các "thân sậy".

Mục tiêu (ưu tiên theo thứ tự):
1. **Hút khách tại Làng Maker** — dễ hiểu trong 2 giây, đối kháng tạo đám đông.
2. **Mở rộng dạy-làm** — sau này học sinh tự lắp nút/đế cảm ứng, tự vận động.
3. **Sản phẩm catalog** — đóng gói phát hành trong app **NeoArcade**.

FlappyDe là **sản phẩm #1**; NeoArcade sẽ còn nhiều game khác được cập nhật dần.

## 2. Bộ nhận diện — Dế Foundation (DE STEM)

Lấy từ repo `de-stem-foundation` (`docs/design-guidelines.md`).

| Vai trò | Token | Hex |
|---|---|---|
| Màu chính (Lam Đại Dương) | `blue-electric` | `#2347FB` |
| Cyan / soft | `blue-cyan` / `blue-soft` | `#94F6FF` / `#D8EFFF` |
| Nhấn năng lượng | `pink-hot` / `orange-hot` | `#D71D90` / `#E74D1E` |
| Thiên nhiên (Xanh Diệp Lục) | `green-cricket` / `green-lime` | `#0C7069` / `#D5F244` |
| Mực / nền | `ink` / `white` | `#121212` / `#F7F7F7` |

- **Mascot**: con **Dế** phẳng một-màu xanh điện — thân lá, đầu tròn quay phải +
  1 mắt trắng, 2 râu dài cong, chân nhảy. Bám sát logo `logo-blue.svg`.
- **Bối cảnh**: trời sáng (cyan→soft) + mặt trời cam (Bình Minh); cột = **thân sậy**
  xanh diệp lục viền lime (chất môi trường); cỏ lime; mây blob trắng.
- **Typography**: font bo tròn (Arial Rounded / Avenir Next Rounded / Nunito…).
- Bản chính thức sẽ **thả thẳng SVG/PNG xuất từ Figma brand kit** vào `assets/`.

## 3. Cơ chế chơi

- **1 nút / người**: nhấn = Dế vỗ cánh bay lên; không nhấn = trọng lực kéo rơi.
- Sậy mọc trên/dưới chừa 1 khe; qua mỗi cột +1 điểm.
- Va chạm trần/đất/sậy → tuỳ chế độ (chết hoặc choáng).
- Vòng đời màn hình: `MENU → ĐẾM 3-2-1 → CHƠI → KẾT QUẢ → (MENU)`.

### 3.1 Chế độ SOLO (đua bảng điểm)
- 1 người, chơi tới khi chết. Tốc độ tăng + khe hẹp dần theo điểm.
- Phá kỷ lục → lưu leaderboard (tên 3 ký tự arcade). Lượt nhanh, xếp hàng chơi.

### 3.2 Chế độ ĐẤU 2 NGƯỜI (đua tới đích)
- Màn **chia đôi**, mỗi người 1 con Dế, **cùng dãy sậy** (công bằng, seed chung).
- Đua tới **vạch đích cố định** (mặc định 18 cột). Ai về trước **THẮNG ngay**.
- Đụng sậy **không chết** mà **choáng ~1.2s + lùi nhẹ** (mất thời gian) rồi chơi tiếp
  → cuộc đua luôn căng tới phút chót. Có thanh tiến độ + màn ăn mừng người thắng.

## 4. Hồ sơ điều khiển (control profiles)

Game chỉ nghe một lệnh trừu tượng `flap(player_id)`. Nguồn nào tạo ra lệnh đó cũng được —
chuyển đổi qua `CONTROL_PROFILE`, **không sửa logic game**:

| Profile | Mô tả | P1 | P2 | Trạng thái |
|---|---|---|---|---|
| `keyboard` | Bàn phím ngoài (demo/triển lãm, dự phòng khi ThingBot hỏng) | `SPACE` | `ENTER` | ✅ prototype |
| `thingbot` | Nút bấm trên mạch **ThingBot ESP32** qua `neo-hw` (bản chính thức) | nút mạch 1 | nút mạch 2 | 🔜 |
| `jumppad` | **Nút cảm ứng — học sinh NHẢY LÊN để vỗ cánh** (vận động thật) | đế cảm ứng 1 | đế cảm ứng 2 | 🧪 tương lai |

- `thingbot`: tái dùng `SimulatorBackend`/`TelemetrixBackend` của neo-hw; `find_thingbot_ports()`
  gán cổng đầu = P1, cổng sau = P2; debounce ~15ms tại lớp input; **fallback bàn phím luôn bật**.
- `jumppad`: ý tưởng giáo dục — mỗi cú nhảy của học sinh = 1 cú vỗ cánh (nút cảm ứng/điện dung
  hoặc cảm biến lực). Biến game thành bài vận động; khớp định hướng "dạy-làm".

## 5. Kiến trúc

```
ThingBot P1/P2 (nút) ──Telemetrix/USB──┐
Bàn phím ngoài ────────────────────────┤→ input/ (profiles → ButtonEvent → flap(player))
Đế cảm ứng (jumppad, tương lai) ───────┘
                                         ↓
                       engine/  (LÕI THUẦN, test 100%: physics Dế, sinh sậy,
                                  va chạm, điểm, state machine, luật solo/đấu)
                          ↓ vẽ                    ↓ điểm
                       ui/ (pygame-ce, 60fps,     storage/ (SQLite leaderboard)
                           juice, âm thanh)
                          ↑
                       app.py (vòng lặp, ghép input·engine·ui·storage)
```

- **Ngôn ngữ**: Python 3.11+. **Render**: `pygame-ce` (game action 60fps; khác QML của NeoRace).
- **engine/** thuần Python, không dính render/hardware → **TDD được**.
- **input/** chuẩn hoá mọi nguồn về `flap(player)`; chứa các control profile.
- **storage/** SQLite tại chỗ (offline ở hội chợ): bảng `scores(mode, player_name, score,
  distance, won, duration_ms, created_at)`. Chỉ lưu tên 3 ký tự — không thu thập dữ liệu trẻ.

## 6. Cảm giác chơi (juice)
Rung màn khi va chạm; hạt cyan khi vỗ cánh, lime khi qua cột, cam/hồng khi chết;
squash-stretch + nghiêng theo vận tốc; âm thanh chip-tune; attract loop hút khách khi rảnh.

## 7. Kiểm thử
- **TDD `engine/`**: physics, sinh sậy, va chạm, điểm, state, luật solo (chết) & đấu (về đích, choáng).
- **`input/`**: debounce, đổi profile, mất/cắm lại ThingBot, fallback bàn phím.
- **`storage/`**: ghi/đọc điểm, lọc TOP hôm nay, export CSV.
- Chạy `make run-sim` (bàn phím) để demo/QA không cần phần cứng. Acceptance: 1 vòng solo +
  1 vòng đấu về đích trên simulator; kịch bản rút tay cầm giữa chừng → phục hồi.

## 8. NeoArcade — bộ sản phẩm
NeoArcade là **app launcher + bộ game** arcade ThingBot trên NEO. FlappyDe là game #1.
Khung `engine/input/storage/attract` tái dùng để thêm game mới (gợi ý kế tiếp: Sút Luân Lưu,
Nước Rút đập nút…). Mỗi game đóng gói vào catalog NeoArcade / NeoPlay.

## 9. Lộ trình
1. ✅ Prototype: con Dế brand, SOLO + ĐẤU 2 NGƯỜI, profile bàn phím.
2. ✅ **Hoàn thiện**: tách `engine/input/ui/storage` (`src/neoarcade/`), **25 test** (engine/storage/input/controller),
   leaderboard SQLite (TOP hôm nay ở menu), âm thanh chip-tune tổng hợp, mô hình **2 nút** khớp ThingBot.
3. 🔜 Profile `thingbot` (neo-hw) chạy phần cứng thật + acceptance trên NEO One + 2 ThingBot.
4. 🔜 Asset chính thức từ Figma brand kit (logo, mascot, shape).
5. 🧪 Profile `jumppad` (nút cảm ứng — nhảy để bay) cho hướng vận động/dạy-làm.
6. 🔜 Đưa FlappyDe vào catalog NeoArcade + thêm game #2.
```
