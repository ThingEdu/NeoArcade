# NeoArcade — Kế hoạch Bộ Game Vận Động cho Trẻ

> Bộ game arcade vận động cho Làng Maker, chạy trên **NEO One**, điều khiển bằng
> **ThingBot ESP32** (và camera), mascot con **Dế**. Mỗi game = **một loại vận động**
> cho trẻ + **một bài học Blue Economy** của Dế Foundation. Cập nhật: 2026-06-12.

## 1. Tầm nhìn

NeoArcade là **cánh tay "vận động"** trong vũ trụ Dế Foundation — bổ sung cho
[DeBlue / Blue World](https://deblue.vercel.app) (cánh tay "tư duy"). Cùng mascot con Dế,
cùng tinh thần **Blue Economy** (học từ thiên nhiên, kinh tế tuần hoàn tự tái sinh).

3 mục tiêu (theo thứ tự ưu tiên):
1. **Hút trẻ ở Làng Maker** — vui, đối kháng, chơi ngay.
2. **Cho trẻ vận động** — phủ hết các nhóm vận động phát triển thể chất.
3. **Gieo khái niệm Blue** — mỗi game nhúng nhẹ 1 nguyên lý bền vững, trẻ "ngấm" qua chơi.

Nguyên tắc thiết kế: game chỉ nghe lệnh trừu tượng (`flap`, `steer`, `hit`, `punch`…),
**đổi nguồn điều khiển không sửa logic** → dễ thêm cảm biến mới, dễ cho trẻ tự lắp (dạy-làm).

## 2. Bản đồ vận động → game → input → Blue

| Nhóm vận động (trẻ) | Game | Input ThingBot/cảm biến | Nguyên lý Blue nhúng |
|---|---|---|---|
| Phản xạ & canh thời gian | **FlappyDe** ✅ | nút bấm / nhảy (đế cảm ứng) | **flow** (dòng năng lượng), **balance** |
| Toàn thân & cử chỉ tay | **Bắt Dế** (camera) | webcam + MediaPipe (cử chỉ tay) | **cluster** (dế tụ đàn), **local**, **balance** |
| Vận động tinh — lái | **Đua Xe Dế** | cần analog (joystick) / nút bấm | **cascade** (rác→năng lượng), **local** |
| Ném & nhắm | **Bóng Rổ Dế** | cảm biến chạm/hồng ngoại ở rổ | **copy-nature** (quỹ đạo parabol), tái dùng bóng |
| Sức mạnh & bùng nổ | **Đấm Sức Mạnh** | cảm biến rung/va đập (piezo/gia tốc) | **flow** (chuyển hoá lực), **copy-nature** |
| Vận động thô — nhảy | **Dế Nhảy Xa** | đế cảm ứng / cảm biến lực (nhảy) | **copy-nature** (chân dế bật xa) |
| Thăng bằng | **Giữ Thăng Bằng** | cảm biến nghiêng (gia tốc kế) | **balance** |
| Nhịp điệu | **Nhịp Dế** | nút bấm theo nhạc | **flow**, **cluster** |
| Vận động thô — chạy | **Nước Rút** (đập nút) | nút bấm (đập nhanh) | **flow** |

> Phủ đủ 9 nhóm vận động cốt lõi cho trẻ 6-14. Bắt đầu vài game, mở rộng dần.

## 3. Danh mục game (chi tiết)

### 3.1 FlappyDe ✅ (đã có prototype)
- **Vận động**: phản xạ, canh thời gian (nhấn/nhả). Biến thể `jumppad`: trẻ **nhảy lên** để bay.
- **Input**: nút bấm ThingBot (P1/P2) · bàn phím (demo) · đế cảm ứng (tương lai).
- **Chơi**: SOLO đua điểm + ĐẤU 2 NGƯỜI đua tới đích. Mascot Dế né "thân sậy".
- **Blue**: dòng chảy năng lượng không ngừng (**flow**); giữ Dế lơ lửng = **balance**.

### 3.2 Bắt Dế (Camera) — tương tác tay qua webcam
- **Vận động**: vung tay, với, toàn thân; phối hợp tay-mắt.
- **Input**: **webcam + MediaPipe** (nhận bàn tay/cử chỉ) — tái dùng Vision Core của
  [[project_neomakervigate_status]] (PyQt6 + MediaPipe đã chạy 29.7fps).
- **Chơi**: đàn Dế nhảy trên màn, trẻ **vẫy/chạm tay** để bắt vào lọ; bắt đúng loài, **thả lại
  khi đủ** để đàn không cạn. Solo đếm giờ / đấu ai bắt nhiều hơn.
- **Blue**: Dế sống thành **cluster** (đàn); chỉ bắt loài **local**; bắt vừa đủ để **balance** hệ.

### 3.3 Đua Xe Dế — lái bằng cần analog ThingBot
- **Vận động**: vận động tinh ngón/cổ tay (lái, ga); phản xạ tránh.
- **Input**: **cần analog/joystick** trên ThingBot (đọc giá trị ADC) để lái + nút ga;
  bản đơn giản chỉ 2 nút trái/phải.
- **Chơi**: Dế lái xe qua **"thành phố Blue"**, nhặt pin/rác đổi năng lượng, tránh kẹt xe.
  Đua 2 làn (như [[project_neorace_status]]) hoặc tính giờ.
- **Blue**: **cascade** (rác đầu vào → năng lượng đầu ra); **local** (trạm sạc gần nhất).

### 3.4 Bóng Rổ Dế — cảm biến chạm tính điểm
- **Vận động**: ném, nhắm, bật tay; phối hợp tay-mắt.
- **Input**: **cảm biến chạm/hồng ngoại** ở vành rổ (mỗi quả lọt = +điểm); có thể thêm
  cảm biến lực để đo cú ném.
- **Chơi**: ném bóng (vật lý thật hoặc trên màn) vào rổ; app đếm điểm, combo. Đấu 2 rổ.
- **Blue**: quỹ đạo parabol **copy-nature**; bóng **tái dùng** (nhặt lại, vòng tuần hoàn).

### 3.5 Đấm Sức Mạnh — bao cát cảm biến rung
- **Vận động**: sức mạnh, bùng nổ toàn thân; giải phóng năng lượng.
- **Input**: **cảm biến rung/va đập (piezo) hoặc gia tốc kế** gắn bao cát → đo lực cú đấm,
  app hiện thanh sức mạnh + xếp hạng.
- **Chơi**: đấm hết sức, app quy lực thành điểm/"sấm sét"; thi ai mạnh nhất. Hiệu ứng rung màn.
- **Blue**: **flow** — chuyển hoá lực cơ bắp thành "năng lượng" trên màn; **copy-nature**
  (chân dế bật khoẻ gấp nhiều lần thân — cảm hứng biomimicry).

### 3.6–3.9 Mở rộng phủ hết vận động
- **Dế Nhảy Xa** — đế cảm ứng/cảm biến lực: trẻ **nhảy thật** để Dế bật xa (vận động thô).
- **Giữ Thăng Bằng** — gia tốc kế: nghiêng tay cầm/đứng giữ Dế thăng bằng (**balance**).
- **Nhịp Dế** — nút bấm theo tiếng dế gáy/nhạc (nhịp điệu, **flow**).
- **Nước Rút** — đập nút đua 100m (vận động thô chạy, năng lượng đám đông cao).

## 4. Bản đồ input ThingBot / cảm biến

| Input | Phần cứng | Game dùng | Trạng thái |
|---|---|---|---|
| Nút bấm digital | nút arcade + GPIO | FlappyDe, Nhịp, Nước Rút | ✅ neo-hw |
| Cần analog | joystick/chiết áp → ADC | Đua Xe Dế | 🔜 |
| Cảm biến chạm/điện dung | touch pad / hồng ngoại | Bóng Rổ, Bắt Dế (đế), Nhảy Xa | 🔜 |
| Rung/va đập | piezo / gia tốc kế (MPU6050) | Đấm Sức Mạnh, Thăng Bằng | 🔜 |
| Camera thị giác | webcam + MediaPipe | Bắt Dế | 🔜 (tái dùng NeoMakerViGate) |

Tất cả đi qua lớp `input/` chuẩn hoá (như FlappyDe) → game không biết nguồn nào, **fallback bàn phím luôn bật**.

## 5. Lồng ghép Blue Economy (vũ trụ Dế Foundation)

Mỗi game gắn **1 "thẻ Blue"** nhỏ (1 câu + biểu tượng) hiện ở màn kết quả/attract, không
làm nặng gameplay. Bối cảnh chung = **"Thành phố Blue"** (xanh, tuần hoàn, sạch) — đồng bộ
với DeBlue. 6 nguyên lý phân bổ qua các game (xem cột "Blue" mục 2). Mục tiêu: trẻ **chơi
vận động** rồi dần quen từ khoá **cascade / cluster / copy-nature / flow / local / balance** —
đúng cách DeBlue đang dạy qua mô phỏng. NeoArcade (vận động) + DeBlue (tư duy) = 2 cửa vào
cùng một thế giới Dế.

## 6. Kế hoạch phát hành (roadmap)

| Phase | Nội dung | Input mới | Mục tiêu |
|---|---|---|---|
| **0** ✅ | FlappyDe prototype (button) | nút bấm | kiểm chứng công thức + brand |
| **1** | Hoàn thiện FlappyDe (tách engine/TDD/`thingbot`) + **Đua Xe Dế** | cần analog | 2 input nền (digital + analog) |
| **2** | **Bóng Rổ Dế** + **Đấm Sức Mạnh** | chạm, rung/gia tốc | game cảm biến vật lý |
| **3** | **Bắt Dế** (camera) | webcam + MediaPipe | thị giác, tái dùng NeoMakerViGate |
| **4** | Nhảy Xa · Thăng Bằng · Nhịp · Nước Rút | đế cảm ứng, nghiêng | phủ hết nhóm vận động |
| **5** | Đóng gói catalog **NeoArcade launcher** + đưa lên [[project_neoplay_status]] | — | phát hành |

**Quy trình mỗi game**: brainstorm → spec → prototype (sim bàn phím) → profile thingbot +
acceptance NEO One → gắn thẻ Blue → đưa vào catalog.

## 7. Hướng dạy-làm (maker)
Mỗi loại cảm biến là một **bộ kit trẻ tự lắp** vào ThingBot: nút arcade, cần analog, đế cảm ứng,
piezo, gia tốc kế, webcam. Trẻ vừa **chơi** vừa **hiểu cảm biến tạo ra điều khiển thế nào** —
khớp mục tiêu Làng Maker và tinh thần copy-nature của Blue Economy.
