# 🎭 EmotionAI — Nhận Diện Cảm Xúc Khuôn Mặt bằng Trí Tuệ Nhân Tạo

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Ứng dụng web nhận diện 7 loại cảm xúc khuôn mặt real-time sử dụng Deep Learning CNN**

[🚀 Demo Live](#) · [📖 API Docs](#api-reference) · [🐛 Báo lỗi](https://github.com/tdkenemi/App_CamXuc/issues)

![EmotionAI Screenshot](./docs/screenshot.png)

</div>

---

## 📋 Mục Lục

- [Giới thiệu](#-giới-thiệu)
- [Tính năng nổi bật](#-tính-năng-nổi-bật)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Cài đặt và Chạy Local](#-cài-đặt-và-chạy-local)
- [Cấu hình môi trường](#-cấu-hình-môi-trường)
- [API Reference](#-api-reference)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [Thông số Mô hình AI](#-thông-số-mô-hình-ai)
- [Deploy lên Render](#-deploy-lên-render)
- [Tác giả](#-tác-giả)

---

## 🌟 Giới thiệu

**EmotionAI** là đồ án tốt nghiệp được phát triển bởi sinh viên **Triệu Duy Khang**, Khoa Công nghệ Thông tin, Đại học Nguyễn Tất Thành (NTT University).

Dự án ứng dụng **mạng nơ-ron tích chập (CNN)** được huấn luyện trên bộ dữ liệu **FER2013** (~35,000 ảnh khuôn mặt) để nhận diện chính xác **7 loại cảm xúc cơ bản** của con người:

| Cảm xúc | Emoji | Mô tả |
|---------|-------|--------|
| Tức giận | 😠 | Angry |
| Ghê tởm | 🤢 | Disgust |
| Sợ hãi | 😨 | Fear |
| Vui vẻ | 😊 | Happy |
| Bình thường | 😐 | Neutral |
| Buồn bã | 😢 | Sad |
| Bất ngờ | 😮 | Surprise |

---

## ✨ Tính năng nổi bật

### 🤖 AI & Computer Vision
- **Phát hiện khuôn mặt tự động** bằng Haar Cascade (OpenCV)
- **Phân tích cảm xúc** với CNN model 7 classes
- **Hiển thị bounding box** trực tiếp trên ảnh gốc
- **Phân bổ xác suất** cho từng cảm xúc (biểu đồ thanh)
- **Batch analysis**: Phân tích nhiều ảnh cùng lúc (tối đa 10)
- **Camera real-time**: Chụp ảnh trực tiếp từ webcam

### 🔐 Bảo mật
- **JWT Authentication** (JSON Web Tokens)
- **Password hashing** với bcrypt
- **Rate limiting**: Chống spam phân tích (30 req/phút)
- **Login brute-force protection** (5 lần/5 phút)
- **Security headers**: X-Frame-Options, X-XSS-Protection, X-Content-Type-Options
- **Input validation** cả client-side và server-side

### 📊 Dashboard Admin
- **KPI Cards** với số liệu real-time + animation counter
- **Doughnut Chart**: Tỉ lệ cảm xúc toàn hệ thống
- **Line Chart**: Xu hướng phân tích 7 ngày gần nhất
- **Bar Chart**: So sánh số lượng mỗi cảm xúc
- **Bảng lịch sử** có filter theo cảm xúc, tìm kiếm, phân trang
- **Quản lý Feedback**: Xem đánh giá độ chính xác AI
- **Quản lý Users**: Danh sách tài khoản hệ thống
- **Xuất CSV** với encoding UTF-8 chuẩn tiếng Việt
- **Auto-refresh** mỗi 30 giây

### 🎨 UI/UX
- **Dark Glassmorphism** design system
- **Responsive** hoàn toàn (mobile / tablet / desktop)
- **GSAP animations** mượt mà
- **Trang 404** đẹp với animation
- **Toast notifications** cho mọi thao tác
- **Keyboard shortcuts** (Esc, Enter)
- **Offline detection** tự động

---

## 🏗 Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (HTML/CSS/JS)              │
│  index.html ──── app.js ──── style.css               │
│  admin.html ──── admin.js                            │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP REST API
┌──────────────────────▼──────────────────────────────┐
│              FastAPI Backend (Python 3.11)            │
│                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  auth.py    │  │  main.py     │  │ ai_service  │  │
│  │  JWT/bcrypt │  │  REST APIs   │  │  CNN Model  │  │
│  └─────────────┘  └──────┬───────┘  └──────┬──────┘  │
│                          │                  │          │
│  ┌─────────────┐         │         ┌───────▼──────┐   │
│  │  models.py  │         │         │ emotion_     │   │
│  │  Pydantic   │◄────────┘         │ model.h5     │   │
│  └─────────────┘                   └──────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              MongoDB Atlas (Cloud)                    │
│  history_collection  │  feedback_collection          │
│  users_collection                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Cài đặt và Chạy Local

### Yêu cầu hệ thống
- Python 3.11+
- pip hoặc pip3
- MongoDB Atlas account (miễn phí)

### Bước 1: Clone repository
```bash
git clone https://github.com/tdkenemi/App_CamXuc.git
cd App_CamXuc
```

### Bước 2: Tạo môi trường ảo
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ **Lưu ý cho Windows**: Cần cài riêng `bcrypt==3.2.2` để tránh xung đột:
> ```bash
> pip install bcrypt==3.2.2
> ```

### Bước 4: Cấu hình môi trường
```bash
# Copy file mẫu
cp .env.example .env

# Mở .env và điền thông tin của bạn
# (xem phần Cấu hình môi trường bên dưới)
```

### Bước 5: Thêm model AI
Do file `emotion_model.h5` (~7MB) không được lưu trên GitHub, bạn cần tải riêng:
- Đặt file `emotion_model.h5` vào thư mục gốc của dự án.

### Bước 6: Khởi chạy server
```bash
python cli.py start
```

Mở trình duyệt tại: **http://localhost:8000**

---

## ⚙️ Cấu hình môi trường

Tạo file `.env` từ `.env.example` và điền các giá trị:

```env
# === MongoDB Connection ===
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/

# === CORS - Domains được phép gọi API ===
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# === JWT Security ===
# Tạo secret key mạnh: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your_strong_secret_key_here_minimum_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# === Admin mặc định (tạo tự động khi server khởi động lần đầu) ===
ADMIN_USER=admin
ADMIN_PASSWORD=your_strong_admin_password_min_8_chars

# === Environment ===
ENVIRONMENT=development
PORT=8000
```

> 🔐 **Bảo mật**: File `.env` đã được thêm vào `.gitignore` và **KHÔNG BAO GIỜ** được push lên GitHub.

---

## 📖 API Reference

### 🔓 Public Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/` | Trang chủ |
| `GET` | `/api/health` | Kiểm tra trạng thái server |
| `GET` | `/api/emotions` | Danh sách 7 cảm xúc |
| `POST` | `/api/register` | Đăng ký tài khoản |
| `POST` | `/api/login` | Đăng nhập nhận JWT token |
| `POST` | `/api/predict` | Phân tích 1 ảnh |
| `POST` | `/api/predict/batch` | Phân tích nhiều ảnh (≤10) |
| `POST` | `/api/feedback` | Gửi feedback kết quả |

### 🔒 User Endpoints (Cần đăng nhập)

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/me` | Thông tin tài khoản |
| `GET` | `/api/history/me` | Lịch sử phân tích cá nhân |

### 👑 Admin Endpoints (Chỉ Admin)

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| `GET` | `/api/history` | Lịch sử toàn hệ thống (có filter, page) |
| `DELETE` | `/api/history/{id}` | Xóa 1 bản ghi |
| `GET` | `/api/stats` | Thống kê tổng hợp |
| `GET` | `/api/stats/trend` | Xu hướng 7 ngày |
| `GET` | `/api/users` | Danh sách người dùng |

📝 **Swagger UI**: http://localhost:8000/api/docs

---

## 📁 Cấu trúc thư mục

```
App_CamXuc/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, routes, middleware
│   ├── auth.py          # JWT, bcrypt, rate limiting
│   ├── db.py            # MongoDB connection
│   ├── ai_service.py    # CNN model, image processing
│   └── models.py        # Pydantic validation models
│
├── templates/
│   ├── index.html       # Trang chủ (7 sections)
│   ├── admin.html       # Dashboard Admin (4 tabs, 3 charts)
│   └── 404.html         # Custom 404 page
│
├── static/
│   ├── css/
│   │   └── style.css    # Design system (1600+ lines)
│   ├── js/
│   │   ├── app.js       # Frontend logic trang chủ
│   │   └── admin.js     # Frontend logic dashboard
│   └── img/
│       └── favicon.svg  # Icon trình duyệt
│
├── tests/               # Unit tests
├── scripts/             # Scripts tiện ích
│
├── cli.py               # CLI tool: python cli.py start
├── emotion_model.h5     # Model AI (không trên GitHub)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker container
├── render.yaml          # Deploy config (Render.com)
├── .env                 # Biến môi trường (không trên GitHub)
├── .env.example         # Mẫu .env
├── .gitignore           # File loại trừ Git
└── README.md            # Tài liệu này
```

---

## 🧠 Thông số Mô hình AI

| Thông số | Giá trị |
|----------|---------|
| **Dataset** | FER2013 (Kaggle) |
| **Số ảnh huấn luyện** | ~28,709 ảnh |
| **Số ảnh kiểm thử** | ~3,589 ảnh |
| **Input size** | 48 × 48 pixels (grayscale) |
| **Kiến trúc** | CNN + BatchNorm + Dropout |
| **Số classes** | 7 cảm xúc |
| **Test Accuracy** | ~70% |
| **Human Accuracy** | ~65.5% (trên FER2013) |
| **Framework** | TensorFlow/Keras |

> 📊 FER2013 là bộ dữ liệu chuẩn quốc tế được sử dụng trong hầu hết nghiên cứu nhận diện cảm xúc. Độ chính xác ~70% được xem là **state-of-the-art** cho single-model CNN trên bộ dữ liệu này và vượt qua ngưỡng nhận diện của con người (~65.5%).

---

## 🐳 Deploy lên Render

### Sử dụng render.yaml (Khuyến nghị)

File `render.yaml` đã được cấu hình sẵn. Chỉ cần:

1. Push code lên GitHub
2. Vào [render.com](https://render.com) → New → Blueprint
3. Connect GitHub repository
4. Thêm Environment Variables (MongoDB URI, Secret Key, Admin Password)
5. Deploy!

### Hoặc Deploy thủ công (Docker)

```bash
# Build image
docker build -t emotionai .

# Run container
docker run -d -p 8000:8000 \
  -e MONGODB_URI="your_mongodb_uri" \
  -e SECRET_KEY="your_secret_key" \
  -e ADMIN_PASSWORD="your_admin_password" \
  emotionai
```

---

## 🧪 Chạy Tests

```bash
# Cài pytest
pip install pytest pytest-asyncio httpx

# Chạy tests
pytest tests/ -v
```

---

## 📝 Contributing

Xem [CONTRIBUTING.md](./CONTRIBUTING.md) để biết hướng dẫn đóng góp.

---

## 📄 License

Dự án được phát hành dưới [MIT License](./LICENSE).

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

**🎭 EmotionAI v3.1** · Made with ❤️ by Triệu Duy Khang · ĐH Nguyễn Tất Thành

</div>
