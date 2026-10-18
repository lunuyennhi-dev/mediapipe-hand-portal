# RETROLENS - Hand AR Portal Camera

Ứng dụng thấu kính tương tác thực tế ảo tăng cường (AR Hand Portal) thời gian thực sử dụng **MediaPipe Tasks Vision** và **OpenCV**. Người dùng tạo ra các khung hiệu ứng độc đáo bằng chính các đầu ngón tay và điều khiển bộ lọc hoàn toàn thông qua cử chỉ tự nhiên mà không cần chạm vào bàn phím hay chuột.

---

## Yêu Cầu Hệ Thống

- **Hệ điều hành:** Windows 10/11, macOS, hoặc Linux.
- **Python:** Phiên bản từ **3.9** đến **3.12** (khuyên dùng Python 3.10 hoặc 3.11).
- **Thiết bị:** Webcam hoạt động bình thường.

---

## Cài Đặt Thư Viện

Bạn có thể cài đặt nhanh các thư viện cần thiết bằng một trong hai cách dưới đây:

### Cách 1: Cài đặt trực tiếp bằng lệnh pip (Nhanh nhất)
Mở Terminal / PowerShell / Command Prompt và chạy lệnh:
```bash
pip install opencv-python mediapipe numpy
```

### Cách 2: Cài đặt thông qua file requirements.txt
```bash
pip install -r requirements.txt
```

*(Khuyến nghị)* Nếu bạn muốn chạy trên một môi trường ảo riêng biệt (Virtual Environment) để tránh xung đột thư viện:
```bash
# Trên Windows:
python -m venv venv
.\venv\Scripts\activate
pip install opencv-python mediapipe numpy

# Trên macOS / Linux:
python3 -m venv venv
source venv/bin/activate
pip install opencv-python mediapipe numpy
```

---

##  Hướng Dẫn Tải & Chạy Ứng Dụng

### Bước 1: Tải mã nguồn về máy
```bash
git clone https://github.com/<tai_khoan_cua_ban>/mediapipe_portal.git
cd mediapipe_portal
```
*(Hoặc tải file ZIP từ GitHub về máy và giải nén).*

### Bước 2: Chạy kiểm tra hệ thống (Unit Test)
Chạy script kiểm tra để xác nhận camera, các bộ lọc và thư viện hoạt động chuẩn xác:
```bash
python test_pipeline.py
```
Nếu màn hình thông báo `ALL TESTS PASSED! CLEAN OPTIMIZED SYSTEM IS READY.` là hệ thống đã hoàn toàn sẵn sàng.

### Bước 3: Khởi động chương trình chính
```bash
python main.py
```
*(Lưu ý: File trọng số mô hình `hand_landmarker.task` đã có sẵn trong thư mục dự án. Nếu bị thiếu, ứng dụng sẽ tự động tải về từ máy chủ Google Storage).*

---

## Hướng Dẫn Sử Dụng & Thao Tác Cử Chỉ

### 1. Kích hoạt khung hình (Quy tắc giơ ngón tay)
- **Điều kiện kích hoạt:** Bạn cần đưa cả **2 bàn tay** lên trước camera và giơ tối thiểu **Ngón Trỏ** và **Ngón Cái** trên cả 2 tay.
- **Chưa giơ đủ ngón (nắm tay, buông tay):** Khung sẽ **không kích hoạt**, màn hình hiển thị camera thực tế bình thường.
- **Chế độ 1 Khung lớn:** **Gập ngón giữa xuống** $\rightarrow$ Hệ thống tạo 1 khung to duy nhất nối giữa Ngón Trỏ và Ngón Cái của 2 bàn tay.
- **Chế độ 2 Khung xếp chồng:** **Giơ cả ngón giữa lên** $\rightarrow$ Hệ thống tự động phân tách thành 2 khung xếp chồng song song (Khung 1: Trỏ $\rightarrow$ Giữa; Khung 2: Giữa $\rightarrow$ Cái), mỗi khung chạy 1 bộ lọc riêng biệt.

### 2. Cử chỉ điều khiển thông minh
| Cử chỉ bàn tay | Hành động kích hoạt | Chi tiết xử lý |
|---|---|---|
| **Chạm Ngón Giữa vào Ngón Cái** | **Đổi bộ lọc tiếp theo** | Chuyển cảnh mờ dần (Cross-fade) mượt mà trong 0.25 giây |
| **Chạm Ngón Trỏ vào Ngón Cái (0.4s)** | **Đếm ngược 3s chụp ảnh** | Giữ chạm 0.4s để xác nhận chống bấm nhầm $\rightarrow$ Màn hình hiện vòng đếm ngược `3.. 2.. 1..` rồi tự động chụp ảnh |

### 3. Phím tắt bàn phím tiện ích
| Phím | Chức năng |
|---|---|
| **`[SPACE]`** (Phím cách) | Bật đếm ngược 3 giây để chụp ảnh |
| **`[S]`** | Chụp ảnh ngay lập tức (không cần chờ đếm ngược) |
| **`[C]`** | Hủy đếm ngược chụp ảnh |
| **`[Tab]`** hoặc **`[F]`** | Chuyển sang bộ lọc tiếp theo |
| **`[Q]`** hoặc **`[ESC]`** | Thoát ứng dụng |

*Tất cả ảnh chụp sẽ được tự động lưu vào thư mục `screenshots/` với định dạng tên `snapshot_YYYYMMDD_HHMMSS.png` cùng hiệu ứng chớp sáng màn trập chân thực.*

---

## Danh Sách 7 Bộ Lọc Nghệ Thuật (Không gây rối mắt)

1. **`THERMAL`**: Giả lập camera tầm nhiệt với bảng màu gradient rực rỡ (`COLORMAP_JET`).
2. **`SKETCH`**: Tranh vẽ phác họa nét chì nghệ thuật đen trắng với thuật toán làm mờ Gaussian và hòa trộn Color Dodge.
3. **`PIXELATE`**: Hiệu ứng đồ họa điểm ảnh 8-bit cổ điển phong cách game thùng arcade.
4. **`NIGHT_VISION`**: Kính nhìn đêm quân sự với ánh lân tinh xanh lá, đường quét quét CRT và nhiễu cảm biến hạt mịn.
5. **`X_RAY`**: Hiệu ứng âm bản phim X-quang tăng cường tương phản cạnh biên với toán tử Laplacian.
6. **`VINTAGE_SEPIA`**: Nước màu ảnh phim cổ điển ấm áp kèm hiệu ứng tối viền (vignette).
7. **`MATRIX`**: Mưa mã số ma trận kỹ thuật số với đường quét ánh sáng xanh lá chuyển động liên tục.

---

## Cấu Trúc Thư Mục Dự Án

```
mediapipe_edit/
│
├── main.py                 # File chạy chính của ứng dụng
├── hand_tracker.py         # Nhận diện tay, bộ lọc mượt One Euro Filter 2D, phát hiện chạm ngón
├── portal_geometry.py      # Thuật toán neo góc cố định, tạo 1/2 khung và hòa trộn cross-fade
├── filters.py              # Động cơ xử lý ảnh số gồm 7 bộ lọc tối ưu hóa bằng NumPy & OpenCV
├── hud.py                  # Giao diện hiển thị: vòng đếm ngược 3s, vòng xác nhận chạm, toast thông báo
├── config.py               # Quản lý toàn bộ thông số cấu hình của ứng dụng
├── test_pipeline.py        # Kịch bản kiểm thử tự động toàn diện (Unit Tests)
├── requirements.txt        # Danh sách thư viện phụ thuộc
├── hand_landmarker.task    # Trọng số mô hình nhận diện tay MediaPipe
├── .gitignore              # Danh sách các file bỏ qua không push lên Git
├── README.md               # Tài liệu hướng dẫn cài đặt và sử dụng
└── BAO_CAO_ASSIGNMENT.md   # Báo cáo đồ án chi tiết theo yêu cầu đề bài
```

---

