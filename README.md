# RETROLENS - Hand AR Portal Camera

Ứng dụng thấu kính tương tác thực tế ảo (AR Hand Portal) thời gian thực sử dụng **MediaPipe** và **OpenCV**. Người dùng tạo khung hiệu ứng camera bằng ngón tay và điều khiển các bộ lọc hoàn toàn bằng cử chỉ tay.

---

## 📋 Thư Viện Cần Thiết

- Python 3.9 trở lên
- `mediapipe>=0.10.0`
- `opencv-python>=4.8.0`
- `numpy>=1.24.0`

---

## ⚡ Cài Đặt & Chạy Nhanh

Mở Terminal / PowerShell và thực hiện 3 bước:

```bash
# 1. Tải dự án về máy
git clone https://github.com/<tai_khoan_cua_ban>/mediapipe_portal.git
cd mediapipe_portal

# 2. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 3. Chạy chương trình
python main.py
```

*(Mô hình nhận diện tay `hand_landmarker.task` sẽ tự động tải về nếu chưa có)*

---

## 🎮 Hướng Dẫn Sử Dụng

### 1. Tạo Khung Hiệu Ứng (Bằng ngón tay)
- **Giơ Ngón Trỏ & Ngón Cái (Gập ngón giữa):** Tạo **1 khung to duy nhất** giữa 2 bàn tay.
- **Giơ cả Ngón Trỏ, Ngón Giữa & Ngón Cái:** Tự động tách thành **2 khung xếp chồng song song** (mỗi khung 1 filter).
- **Chưa giơ đủ ngón (nắm tay, buông tay):** Không kích hoạt khung (Camera bình thường).

### 2. Cử Chỉ Điều Khiển & Phím Tắt
| Thao tác | Chức năng |
|---|---|
| **Chạm Ngón Giữa vào Ngón Cái** | Đổi sang bộ lọc tiếp theo (Chuyển cảnh mượt mà) |
| **Chạm Ngón Trỏ vào Ngón Cái (0.4s)** | Đếm ngược 3 giây để chụp ảnh (có vòng đếm `3..2..1.. 📸`) |
| Phím **`[SPACE]`** (Phím cách) | Bật đếm ngược 3 giây chụp ảnh |
| Phím **`[S]`** | Chụp và lưu ảnh ngay lập tức vào thư mục `screenshots/` |
| Phím **`[C]`** | Hủy đếm ngược chụp ảnh |
| Phím **`[Tab]`** hoặc **`[F]`** | Đổi filter bằng bàn phím |
| Phím **`[Q]`** hoặc **`[ESC]`** | Thoát chương trình |

### 3. Danh Sách Bộ Lọc
1. `THERMAL`: Tầm nhiệt (ColorMap Jet)
2. `SKETCH`: Phác họa chì đen trắng
3. `PIXELATE`: Đồ họa 8-bit retro
4. `NIGHT_VISION`: Kính nhìn ban đêm (xanh lá)
5. `X_RAY`: Âm bản X-Quang
6. `VINTAGE_SEPIA`: Nước ảnh phim cổ điển
7. `MATRIX`: Mưa mã số ma trận

---

## 📁 Cấu Trúc Dự Án

```
mediapipe_edit/
├── main.py                 # File chạy chính của chương trình
├── hand_tracker.py         # Module nhận diện tay & cử chỉ (One Euro Filter)
├── filters.py              # Động cơ 7 bộ lọc xử lý ảnh
├── portal_geometry.py      # Thuật toán dựng khung và ghép bộ lọc
├── hud.py                  # Giao diện đếm ngược 3s và thông báo
├── config.py               # File cấu hình thông số
├── requirements.txt        # Danh sách thư viện cần cài đặt
├── hand_landmarker.task    # Trọng số mô hình MediaPipe
└── README.md               # Hướng dẫn cài đặt và sử dụng
```

---

## 🎥 Video Demo
- **Link Video Demo:** *(Chèn link video YouTube hoặc Google Drive của bạn tại đây)*
