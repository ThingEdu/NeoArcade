# Cài đặt NeoArcade trên NEO One

Hướng dẫn cài & chạy **NeoArcade** trên thiết bị **NEO One** (ARM64 / Armbian).
Đã kiểm chứng thực tế: NEO One, Armbian bookworm, aarch64, Python 3.11.2 — **54/54 test pass**.

> NeoArcade rất nhẹ: chỉ phụ thuộc `pygame-ce` (có sẵn wheel ARM64), nên cài rất nhanh.
> Game thị giác camera (Bắt Dế…) đã tách sang [NeoAiSport](https://github.com/ThingEdu/NeoAiSport) —
> xem hướng dẫn cài riêng ở repo đó.

---

## 1. Yêu cầu

| Mục | Giá trị |
|-----|---------|
| Thiết bị | NEO One (SoC Allwinner, ARM64 / `aarch64`) |
| Hệ điều hành | Armbian bookworm (Debian 12) |
| Python | 3.11+ (`python3 --version`) |
| Đã có sẵn trên Armbian | `git`, `pip3`, `venv`, `libsdl2-2.0-0`, `libgl1` |
| Màn hình | màn hình gắn trực tiếp máy NEO (X11, display `:0`) |
| Điều khiển | bàn phím (mặc định) hoặc mạch **ThingBot ESP32** qua `neo-hw` (tùy chọn) |

Nếu thiếu thư viện hệ thống cho SDL/pygame (hiếm), cài:

```bash
sudo apt update
sudo apt install -y python3-venv libsdl2-2.0-0 libsdl2-mixer-2.0-0 libgl1
```

---

## 2. Truy cập NEO One qua SSH (từ máy dev)

```bash
ssh neo@<IP-NEO-One>        # ví dụ: ssh neo@192.168.1.92
```

Cài SSH key một lần để khỏi nhập mật khẩu mỗi lần:

```bash
ssh-keygen -t ed25519        # nếu chưa có key
ssh-copy-id neo@<IP-NEO-One>
```

---

## 3. Lấy mã nguồn

**Cách A — clone từ GitHub** (cần quyền truy cập, repo private):

```bash
mkdir -p ~/Ai-Code && cd ~/Ai-Code
git clone https://github.com/ThingEdu/NeoArcade.git
cd NeoArcade
```

**Cách B — đẩy bản local từ máy dev bằng rsync** (không cần GitHub auth trên NEO):

```bash
# chạy trên MÁY DEV
rsync -az --delete \
  --exclude '.venv/' --exclude '.pytest_cache/' --exclude '__pycache__/' \
  ~/Ai-Code/NeoArcade/ neo@<IP-NEO-One>:~/Ai-Code/NeoArcade/
```

---

## 4. Cài đặt

```bash
cd ~/Ai-Code/NeoArcade
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"      # hoặc: make install
```

`pygame-ce` có sẵn wheel `aarch64` cp311 trên PyPI nên không cần biên dịch.

**Tùy chọn — phần cứng ThingBot:**

```bash
.venv/bin/pip install -e ".[hardware]"   # cài thêm neo-hw cho profile thingbot
```

---

## 5. Kiểm tra cài đặt (không cần màn hình)

```bash
cd ~/Ai-Code/NeoArcade
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q
# Kỳ vọng: 54 passed
```

---

## 6. Chạy game

Game hiển thị trên **màn hình gắn trực tiếp máy NEO** (display `:0`).
Nếu chạy lệnh qua SSH, đặt `DISPLAY=:0`:

```bash
cd ~/Ai-Code/NeoArcade
DISPLAY=:0 .venv/bin/python -m neoarcade.hub        # màn tổng — chọn game
```

Hoặc dùng Makefile (chạy ngay trên máy NEO, có sẵn `$DISPLAY`):

```bash
make hub          # màn tổng (launcher)
make run-sim      # FlappyDe bằng bàn phím
make run          # FlappyDe với ThingBot (tự fallback bàn phím nếu thiếu phần cứng)
make run-dexe     # Đua Xe Dế
make run-bongro   # Bóng Rổ Dế
make run-damboc   # Đấm Bốc
```

**Điều khiển (mô hình 2 nút khớp ThingBot):** Nút 1 = `SPACE`/`W`, Nút 2 = `ENTER`/`↑`, `ESC` thoát.

---

## 7. Launcher tiện lợi (tùy chọn)

Tạo lệnh ngắn `neoarcade` để mở màn tổng:

```bash
mkdir -p ~/bin
cat > ~/bin/neoarcade <<'SH'
#!/bin/bash
cd ~/Ai-Code/NeoArcade
export DISPLAY="${DISPLAY:-:0}"
exec .venv/bin/python -m neoarcade.hub "$@"
SH
chmod +x ~/bin/neoarcade
grep -q 'HOME/bin' ~/.bashrc || echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Từ giờ chỉ cần gõ: `neoarcade`

---

## 8. Xử lý sự cố

| Triệu chứng | Xử lý |
|-------------|-------|
| `No available video device` / không mở được cửa sổ qua SSH | Đặt `DISPLAY=:0`; đảm bảo có phiên đồ họa (X) đang chạy trên màn hình máy NEO (`ls /tmp/.X11-unix/` thấy `X0`). |
| Không có âm thanh | Bình thường nếu chưa cấu hình audio; thêm `SDL_AUDIODRIVER=dummy` để tắt. |
| `pygame` lỗi import SDL | `sudo apt install -y libsdl2-2.0-0 libgl1`. |
| ThingBot không nhận | Chạy bằng bàn phím trước (`make run-sim`); cài `neo-hw` qua `.[hardware]` để dùng phần cứng. |

---

_Tài liệu liên quan: [`README.md`](../README.md) · [`docs/FlappyDe-design.md`](FlappyDe-design.md) · [`docs/NeoArcade-Games-Roadmap.md`](NeoArcade-Games-Roadmap.md)_
