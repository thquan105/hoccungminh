# Sử dụng image python phiên bản mới
FROM python:3.12.2-slim-bullseye

# Cài đặt các biến môi trường giúp Django không tạo bytecode và không có buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt pip và các phụ thuộc
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Cấp quyền thực thi cho entrypoint.sh nếu chưa có
RUN chmod +x /app/entrypoint.sh

# Mở cổng ứng dụng
EXPOSE 8000

# Chạy lệnh khởi động ứng dụng khi container chạy
ENTRYPOINT ["/app/entrypoint.sh"]
