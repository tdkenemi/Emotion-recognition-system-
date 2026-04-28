# 🎭 Hệ Thống Nhận Diện Cảm Xúc Khuôn Mặt (FER) Tích Hợp MLOps Tự Học

Một ứng dụng Web AI hoàn chỉnh cho phép nhận diện 7 cảm xúc cơ bản của con người (Tức giận, Ghê tởm, Sợ hãi, Vui vẻ, Buồn bã, Bất ngờ, Bình thường) thông qua hình ảnh. Điểm đặc biệt của dự án là việc tích hợp chu trình **MLOps (Human-in-the-loop)**, cho phép hệ thống thu thập phản hồi sai sót từ người dùng để tự động học chuyển giao (Fine-tuning) và ngày càng thông minh hơn.

## 🚀 Công nghệ sử dụng
* **Core AI:** Mạng Nơ-ron Tích chập (Custom CNN) xây dựng bằng `TensorFlow/Keras`.
* **Computer Vision:** Tiền xử lý và định vị khuôn mặt bằng thuật toán Haar Cascade của `OpenCV`.
* **Web Framework:** Giao diện tương tác trực quan được xây dựng bằng `Streamlit`.
* **Deployment (Cloud):** Triển khai Web App từ máy ảo **Google Colab** ra Internet thông qua đường hầm bảo mật **Ngrok**.

## ✨ Tính năng nổi bật
1. **Nhận diện cảm xúc (Inference):** Phân tích ảnh tải lên, cắt khuôn mặt tự động và xuất ra biểu đồ phân bổ xác suất %.
2. **Cơ chế Feedback (MLOps):** Ghi nhận các ca dự đoán sai, lưu ảnh lỗi vào thư mục `feedback_images/` và log lịch sử vào file `lich_su_AI.csv`.
3. **Tự động Retrain (Fine-tuning):** Kịch bản huấn luyện lại với Learning Rate siêu nhỏ giúp AI tự sửa lỗi từ dữ liệu Feedback mà không quên kiến thức cũ.

---

## 🛠️ Hướng dẫn Khởi chạy Dự án (Chạy Demo Nhanh trên Colab)

Dự án này được tối ưu để **không cần phải train lại từ đầu**. Bạn chỉ cần làm theo các bước sau để khởi chạy Web App ngay lập tức:

### Bước 1: Chuẩn bị môi trường trên Google Colab
1. Tải file mã nguồn `.ipynb` từ kho lưu trữ này và mở bằng [Google Colab](https://colab.research.google.com/).
2. **Upload mô hình có sẵn:** Tải file `emotion_model.h5` (hoặc `emotion_model_v2.h5`) và file `haarcascade_frontalface_default.xml` từ máy tính lên thư mục gốc của Colab.
3. **BỎ QUA** các Cell huấn luyện ở bước 3 và 4 chỉ chạy cell tải dữ liệu Kaggle và bước 2. 

### Bước 2: Load mô hình và Tạo giao diện Web
1. Chạy Cell chứa lệnh `load_model('emotion_model.h5')` để đưa não bộ AI vào trạng thái sẵn sàng.
2. Chạy Cell chứa lệnh `%%writefile app.py`. Colab sẽ tự động tạo ra một file giao diện Web Streamlit hoàn chỉnh cho bạn.

### Bước 3: Khởi chạy Máy chủ Web qua Ngrok
1. Kéo xuống Cell "KHỞI CHẠY MÁY CHỦ WEB".
2. Thay đoạn `DÁN TOKEN NGROK VÀO ĐÂY` bằng mã AuthToken lấy từ tài khoản [Ngrok](https://dashboard.ngrok.com/) của bạn.
3. Chạy Cell đó. Hệ thống sẽ tự động cài Streamlit, mở cổng mạng và in ra cho bạn một đường link Public (VD: `https://xxxx.ngrok-free.app`). 
4. Bấm vào link để trải nghiệm ứng dụng Web!

---

## 🔄 Hướng dẫn Vận hành MLOps (Cơ chế Tự Học)
Khi bạn test ứng dụng trên Web và AI đoán sai (VD: thực tế là Vui vẻ nhưng AI đoán là Bình thường), hãy sử dụng phần **Góp ý** trên web.

1. **Thu thập dữ liệu:** Hệ thống web sẽ tự động lưu ảnh lỗi về thư mục `feedback_images/` và cập nhật file `lich_su_AI.csv` ngay trên Colab của bạn.
2. **Retrain (Học lại):** Quay lại file Colab, cuộn xuống Cell có tiêu đề **"Retrain"**. Chạy Cell này. AI sẽ tự động đọc file CSV, học lại chính những tấm ảnh nó vừa đoán sai (Fine-tuning) và xuất ra một phiên bản mới thông minh hơn (thường lưu dưới tên `emotion_model_v2.h5`).
3. **Cập nhật Web:** chạy lại Cell `%%writefile app.py` ở dưới cell retrai, chạy lại Cell đó và cell khởi động lại Server Web để AI nhận diện đúng 100%!

## ✍️ Tác giả
* **Triệu Duy Khang** - Sinh viên Kỹ thuật phần mềm (ĐH Nguyễn Tất Thành)
