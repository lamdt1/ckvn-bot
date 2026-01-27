# Sử dụng Python 3.10 slim để nhẹ và an toàn
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Thiết lập biến môi trường để Python không tạo file .pyc và log output ngay lập tức
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cài đặt dependencies hệ thống cần thiết (nếu có)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Lệnh chạy bot
CMD ["python", "main.py"]
