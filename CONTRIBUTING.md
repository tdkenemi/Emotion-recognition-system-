# Hướng dẫn Đóng góp cho EmotionAI

Cảm ơn bạn đã quan tâm đến dự án! Dưới đây là hướng dẫn để đóng góp code, báo lỗi hoặc đề xuất tính năng.

## 🐛 Báo Lỗi

1. Kiểm tra xem lỗi đã được [báo cáo chưa](https://github.com/tdkenemi/App_CamXuc/issues)
2. Nếu chưa, tạo Issue mới với:
   - Mô tả lỗi rõ ràng
   - Các bước tái hiện lỗi
   - Kết quả mong đợi vs kết quả thực tế
   - Screenshot (nếu có)
   - Môi trường: OS, Python version, trình duyệt

## 💡 Đề xuất Tính năng

Tạo Issue với nhãn `enhancement` và mô tả:
- Tính năng bạn muốn thêm
- Lý do tại sao nó hữu ích
- Mô tả cách bạn muốn nó hoạt động

## 🔧 Đóng góp Code

### Quy trình

1. **Fork** repository
2. **Clone** fork của bạn:
   ```bash
   git clone https://github.com/<your-username>/App_CamXuc.git
   ```
3. Tạo **branch mới**:
   ```bash
   git checkout -b feature/ten-tinh-nang
   # hoặc
   git checkout -b fix/ten-bug
   ```
4. **Viết code** và đảm bảo:
   - Code sạch, có comment rõ ràng
   - Không có hardcode credentials
   - Không commit file `.env` hoặc model `.h5`
5. **Commit** theo quy ước:
   ```bash
   git commit -m "feat: thêm tính năng X"
   git commit -m "fix: sửa lỗi Y"
   git commit -m "docs: cập nhật README"
   ```
6. **Push** lên fork:
   ```bash
   git push origin feature/ten-tinh-nang
   ```
7. Tạo **Pull Request** vào branch `main`

### Code Style

- Python: Theo PEP 8, sử dụng type hints
- JavaScript: ES6+, dùng `const`/`let` thay `var`
- HTML: Semantic, có `aria-label` cho accessibility
- CSS: BEM-like naming, sử dụng CSS variables

## 📝 Quy ước Commit

| Prefix | Ý nghĩa |
|--------|---------|
| `feat:` | Tính năng mới |
| `fix:` | Sửa lỗi |
| `docs:` | Cập nhật tài liệu |
| `style:` | Thay đổi CSS/UI |
| `refactor:` | Tái cấu trúc code |
| `test:` | Thêm/sửa tests |
| `chore:` | Công việc bảo trì |

## 📄 License

Bằng cách đóng góp, bạn đồng ý rằng code của bạn sẽ được phát hành dưới [MIT License](./LICENSE).

---

**Triệu Duy Khang** · ĐH Nguyễn Tất Thành · GitHub: [@tdkenemi](https://github.com/tdkenemi)
