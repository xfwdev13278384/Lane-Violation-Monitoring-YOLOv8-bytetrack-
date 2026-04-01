# 🚦 HỆ THỐNG NHẬN DIỆN PHƯƠNG TIỆN ĐI SAI LÀN

## 1. GIỚI THIỆU
Hệ thống sử dụng AI và Deep Learning để phát hiện, ghi nhận và quản lý các vi phạm đi sai làn đường của phương tiện giao thông. Hệ thống gồm các thành phần:
- Nhận diện và tracking phương tiện từ video
- Xác định làn đường, phát hiện vi phạm
- Lưu trữ minh chứng (ảnh, video, CSV, database)
- Giao diện web quản lý, thống kê, xuất biên bản PDF

## 2. CÀI ĐẶT
### Yêu cầu:
- Python 3.8+
- MySQL 8+
- Các thư viện: Flask, OpenCV, mysql-connector-python, v.v.

### Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

### Khởi tạo database:
- Import file `violations.sql` vào MySQL:
```bash
mysql -u <user> -p < traffic_violation_db < violations.sql
```

## 3. CHẠY HỆ THỐNG
### Chạy nhận diện vi phạm từ video:
```bash
python main.py
```

### Chạy web server:
```bash
cd web
python app.py
```

## 4. CHỨC NĂNG CHÍNH
- **Trang chủ**: Tổng quan, vi phạm gần nhất
- **Quản lý vi phạm**: Tra cứu, lọc, xem chi tiết, tải biên bản PDF
- **Thống kê**: Biểu đồ theo ngày, tháng, giờ, loại phương tiện
- **Tải video minh chứng**: Upload video bổ sung cho từng vi phạm

## 5. CẤU TRÚC THƯ MỤC
- `core/`: Xử lý AI, logic vi phạm, ghi DB, xuất video/ảnh
- `web/`: Giao diện Flask, template, static, utils
- `tools/`: Công cụ hỗ trợ vẽ ROI, kiểm tra dữ liệu
- `VIDEOOO/`: Lưu video đầu vào
- `runs/`, `outputs/`: Kết quả nhận diện, log, minh chứng

## 6. HƯỚNG DẪN SỬ DỤNG NHANH
1. Chuẩn bị video giao thông, copy vào thư mục `VIDEOOO/`
2. Chạy nhận diện bằng `main.py` để sinh dữ liệu vi phạm
3. Khởi động web, truy cập để quản lý, thống kê, xuất biên bản
4. Có thể upload video minh chứng thủ công cho từng vi phạm

## 7. LIÊN HỆ & HỖ TRỢ
- Email: daiphuoc1914@gmail.com
- Zalo: 0399640717

