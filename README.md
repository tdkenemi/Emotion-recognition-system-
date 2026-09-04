# 🎭 EmotionAI — Hệ Thống Nhận Diện Cảm Xúc Khuôn Mặt AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![DeepFace](https://img.shields.io/badge/DeepFace-AI-FF0000?style=for-the-badge&logo=ai)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Ứng dụng web nhận diện 7 loại cảm xúc khuôn mặt chuyên nghiệp sử dụng lõi DeepFace đa mô hình và kiến trúc bảo mật cao FastAPI**

[🚀 Demo Live](#) · [🐛 Báo lỗi](https://github.com/tdkenemi/Emotion-recognition-system-/issues)

</div>

---

## 📸 Giao diện Ứng dụng

> **Hướng dẫn:** Chụp ảnh màn hình web của bạn và lưu vào thư mục `docs/`. Sau đó thay tên file tương ứng vào các đường dẫn bên dưới.

<div align="center">
  <img src="https://github.com/user-attachments/assets/77997d8d-0828-4fdd-8f22-f4fca5d46e75" alt="Giao diện Trang chủ" width="800"/>
  <p><i>Trang chủ - Upload và Phân tích ảnh với DeepFace</i></p>
  
  <br>

  <img src="https://github.com/user-attachments/assets/816abb06-a14c-4048-843e-090832d8ca98" alt="Giao diện Admin Dashboard" width="800"/>
  <p><i>Admin Dashboard - Biểu đồ thống kê thời gian thực</i></p>
</div>

---

## 📋 Mục Lục

- [🌟 Giới thiệu](#-giới-thiệu)
- [✨ Tính năng nổi bật](#-tính-năng-nổi-bật)
- [🛡️ Kiến trúc Bảo Mật (MỚI)](#️-kiến-trúc-bảo-mật-mới)
- [🚀 Hướng dẫn Cài đặt & Chạy Local](#-hướng-dẫn-cài-đặt--chạy-local)
- [⚙️ Cấu hình Môi trường](#️-cấu-hình-môi-trường)
- [👨‍💻 Tác giả](#-tác-giả)

---

## 🌟 Giới thiệu

**EmotionAI** là đồ án tốt nghiệp được phát triển bởi sinh viên **Triệu Duy Khang**, Khoa Công nghệ Thông tin, Đại học Nguyễn Tất Thành (NTT University).

Dự án ứng dụng thư viện nhận diện khuôn mặt và cảm xúc chuyên sâu **DeepFace** (kết hợp các mô hình tiên tiến nhất hiện nay như VGG-Face, Facenet, OpenCV) để nhận diện chính xác **7 loại cảm xúc cơ bản** của con người ngay trong thời gian thực.

| Cảm xúc | Emoji | Cảm xúc | Emoji |
|---------|-------|---------|-------|
| Tức giận | 😠 | Bình thường | 😐 |
| Ghê tởm | 🤢 | Buồn bã | 😢 |
| Sợ hãi | 😨 | Bất ngờ | 😮 |
| Vui vẻ | 😊 | | |

---

## ✨ Tính năng nổi bật

### 🤖 Lõi Trí Tuệ Nhân Tạo (DeepFace Integration)
- **Tự động dò tìm và nhận diện khuôn mặt** với độ chính xác cao ngay cả khi mặt bị nghiêng.
- Tích hợp lõi AI từ **DeepFace**, mạnh mẽ và chính xác hơn gấp nhiều lần so với các mô hình CNN (FER2013) tự train thủ công.
- **Phân bổ xác suất** cho từng cảm xúc và highlight bounding box trực tiếp trên ảnh.
- **Batch analysis**: Phân tích nhiều ảnh cùng lúc (tối đa 10 ảnh) thông qua xử lý đa luồng an toàn.
- **Camera real-time**: Chụp ảnh trực tiếp từ webcam trình duyệt.

### 📊 Dashboard Admin Độc Quyền
- Giao diện Admin quản trị mạnh mẽ dành riêng cho chủ hệ thống (phân quyền Role-based).
- **KPI Cards** tự động đếm tổng số lượng request, độ chính xác AI, số lượng người dùng.
- **Hệ thống Biểu Đồ Trực Quan (Chart.js)**: Doughnut Chart, Line Chart (xu hướng 7 ngày), Bar Chart.
- Quản lý **Lịch sử phân tích**, **Góp ý người dùng**, và theo dõi toàn bộ Database thời gian thực nhờ MongoDB Indexes.

### 🎨 UI/UX Siêu Mượt
- Giao diện **Dark Glassmorphism** vô cùng hiện đại, bắt mắt.
- **Responsive 100%** trên điện thoại, máy tính bảng và màn hình lớn.
- Hàng chục hiệu ứng chuyển động **GSAP animations** chuyên nghiệp.

---

## 🛡️ Kiến trúc Bảo Mật (MỚI - Cập nhật v3.1.1)

Dự án vừa trải qua đợt Audit Bảo Mật toàn diện và áp dụng các tiêu chuẩn an toàn cấp độ Production:

- **Auth Cookie Httponly**: Chuyển đổi toàn bộ quy trình Google OAuth2 sang sử dụng JWT lưu trong HTTP-Only Cookie kết hợp cờ `SameSite=Lax`, ngăn chặn hoàn toàn tấn công XSS lấy cắp token.
- **Chống Stored XSS**: Giao diện Admin được bọc hàm `escapeHtml` cho mọi dữ liệu render từ Database.
- **Cơ chế Rate Limiting Toàn Diện**:
  - Đăng nhập: Tối đa 5 lần sai / 5 phút.
  - Đăng ký: Tối đa 3 tài khoản / 1 giờ / IP.
  - Quên mật khẩu: Tối đa 3 email / 15 phút / IP.
- **Content-Security-Policy (CSP)**: Tích hợp Middleware gắn header CSP chặn thực thi script lạ, kèm theo các header chống Clickjacking (`X-Frame-Options`), MIME-sniffing.
- **Server-side Auth Route**: Các route nhạy cảm như `/admin` được chặn ngay tại Server, không chỉ ẩn UI ở Frontend.
- **Database Optimization**: Unique Indexes cho `username` và `email` để chống Race Condition.

---

## 🚀 Hướng dẫn Cài đặt & Chạy Local

### Bước 1: Clone repository
```bash
git clone https://github.com/tdkenemi/App_CamXuc.git
cd App_CamXuc
```

### Bước 2: Tạo môi trường ảo (Khuyến nghị)
```bash
python -m venv .venv
# Kích hoạt trên Windows:
.venv\Scripts\activate
# Kích hoạt trên Mac/Linux:
source .venv/bin/activate
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Cấu hình biến môi trường
```bash
cp .env.example .env
```
Mở file `.env` và thiết lập các thông số cơ sở dữ liệu MongoDB, cấu hình JWT Secret và Google Client ID (xem phần `Cấu hình môi trường` bên dưới).

### Bước 5: Khởi chạy server
Dự án có CLI riêng biệt giúp việc chạy siêu dễ dàng:
```bash
python cli.py start
```

Mở trình duyệt tại: **http://localhost:8000**
*(Lưu ý: Lần chạy đầu tiên, thư viện DeepFace sẽ tự động tải các file trọng số (weights) cần thiết về máy).*

---

## ⚙️ Cấu hình Môi trường

Bắt buộc cấu hình file `.env` chuẩn xác để các dịch vụ hoạt động trơn tru:

```env
# === MongoDB Connection ===
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/

# === JWT Security ===
SECRET_KEY=your_strong_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# === Admin Mặc định ===
ADMIN_USER=admin
ADMIN_PASSWORD=your_strong_admin_password_min_12_chars

# === Email Configuration (Quên mật khẩu) ===
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# === Google OAuth2 ===
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

> 🔐 **Lưu ý Bảo mật**: Đừng bao giờ up file `.env` lên Github để tránh bị lộ thông tin nhạy cảm. Hãy dùng lệnh `git log --all --full-history -- "**.env"` để chắc chắn bạn chưa bao giờ lỡ tay commit file này.

---

## 👨‍💻 Tác giả

<div align="center">

**Triệu Duy Khang**  
Sinh viên Khoa Công nghệ Thông tin  
Đại học Nguyễn Tất Thành (NTT University)

[![GitHub](https://img.shields.io/badge/GitHub-tdkenemi-181717?style=flat-square&logo=github)](https://github.com/tdkenemi)

</div>

---

<div align="center">

**🎭 EmotionAI v3.1.1** · Tích hợp DeepFace & Chuẩn Bảo Mật Cấp Cao · Made with ❤️ by Triệu Duy Khang

</div>
