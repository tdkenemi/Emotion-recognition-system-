# 🎭 Hệ Thống Nhận Diện Cảm Xúc Khuôn Mặt (FER) Tích Hợp MLOps Tự Học

Một ứng dụng Web AI hoàn chỉnh cho phép nhận diện 7 cảm xúc cơ bản của con người (Tức giận, Ghê tởm, Sợ hãi, Vui vẻ, Buồn bã, Bất ngờ, Bình thường) thông qua hình ảnh. Điểm đặc biệt của dự án là việc tích hợp chu trình **MLOps (Human-in-the-loop)**, cho phép hệ thống thu thập phản hồi sai sót từ người dùng để tự động học chuyển giao (Fine-tuning) và ngày càng thông minh hơn.

## 🚀 Công nghệ sử dụng
* **Core AI:** Mạng Nơ-ron Tích chập (Custom CNN) xây dựng bằng `TensorFlow/Keras` (v2.15.x).
* **Computer Vision:** Tiền xử lý và định vị khuôn mặt bằng thuật toán Haar Cascade của `OpenCV` (v4.8.x).
* **Web Framework:** Giao diện tương tác trực quan được xây dựng bằng `Streamlit` (v1.32.x).
* **Data Processing:** `Pandas` & `Numpy` để xử lý ma trận và quản lý lịch sử phản hồi (CSV).
* **Deployment:** Hỗ trợ public mạng nội bộ ra Internet thông qua đường hầm bảo mật `Ngrok`.

## ✨ Tính năng nổi bật
1. **Nhận diện cảm xúc (Inference):** Phân tích ảnh tải lên, cắt khuôn mặt tự động và xuất ra biểu đồ phân bổ xác suất %.
2. **Cơ chế Feedback (MLOps):** Ghi nhận các ca dự đoán sai, lưu ảnh lỗi vào thư mục cục bộ (`feedback_images/`) và log lịch sử vào file `lich_su_AI.csv`.
3. **Tự động Retrain (Fine-tuning):** Kịch bản huấn luyện lại với Learning Rate cực nhỏ (1e-5) giúp mô hình cập nhật kiến thức mới mà không bị "quên thảm khốc" (Catastrophic Forgetting).

## 🛠️ Hướng dẫn cài đặt và chạy dự án (Local)

**Bước 1: Clone kho lưu trữ này về máy**
```bash
git clone [https://github.com/TENDANGNHAP/TEN-REPO-CUA-BAN.git](https://github.com/TENDANGNHAP/TEN-REPO-CUA-BAN.git)
cd TEN-REPO-CUA-BAN
```
Bước 2: Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```
