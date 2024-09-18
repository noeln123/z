# Rapid Rescue

Rapid Rescue là một ứng dụng web cho phép người dùng nhanh chóng yêu cầu dịch vụ xe cứu thương, theo dõi vị trí xe cứu thương theo thời gian thực và cung cấp thông tin y tế cần thiết cho Kỹ thuật viên y tế khẩn cấp (EMT).

## Các Tính Năng Chính

- Đăng ký và đăng nhập tài khoản
- Quản lý hồ sơ cá nhân và hồ sơ y tế
- Yêu cầu dịch vụ xe cứu thương
- Theo dõi xe cứu thương theo thời gian thực
- Phản hồi về dịch vụ
- Quản trị viên quản lý xe cứu thương và tài xế
- EMT truy cập thông tin bệnh nhân và cập nhật trạng thái

## Cài Đặt

1. Clone repository:

    ```bash
    git clone https://github.com/yourusername/z.git
    cd rapid_rescue
    ```

2. Tạo và kích hoạt môi trường ảo:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Cài đặt các gói yêu cầu:

    ```bash
    pip install -r requirements.txt
    ```

4. Cấu hình MySQL trong `config.py`.

5. Khởi tạo và áp dụng migration:

    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

6. Chạy ứng dụng:

    ```bash
    python app.py
    ```

## License

MIT License
