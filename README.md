# Vietnam Stock Alert Bot 🟢🔵🔴

Bot tự động theo dõi danh mục chứng khoán Việt Nam, tính toán chỉ báo kỹ thuật và gửi cảnh báo thông minh qua Telegram.

## ✨ Tính năng chính
* 📊 **Theo dõi Real-time:** Lấy giá khớp lệnh trực tiếp từ thị trường (vnstock).
* 🧠 **Phân tích kỹ thuật:** Tự động tính toán RSI(14) và MA(20).
* 🚀 **Cảnh báo đa kênh:** Hỗ trợ gửi thông báo qua **Telegram** và **Zalo Bot API**.
* ⏰ **Tự động hóa:** Hoạt động chính xác trong giờ giao dịch (09:00 - 15:00, Thứ 2 đến Thứ 6).
* 🐳 **Docker Ready:** Hỗ trợ chạy container giúp đảm bảo bot luôn online 24/7.

## 🛠 Cài đặt & Sử dụng

### 1. Chuẩn bị
- **Telegram:** Tạo Bot qua [@BotFather](https://t.me/botfather) và lấy Chat ID qua [@userinfobot](https://t.me/userinfobot).
- **Zalo:** Tạo Bot qua Zalo Bot Platform (Xem hướng dẫn chi tiết tại `docs/zalo-bot-doc.md`).

### 2. Cấu hình
1. Tạo file `.env` từ file `.env.example` và thiết lập kênh thông báo:
   ```env
   # Chọn kênh: telegram, zalo, hoặc cả hai (both)
   NOTIFICATION_PROVIDER=telegram

   # Cấu hình Telegram
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_CHAT_ID=...

   # Cấu hình Zalo
   ZALO_BOT_TOKEN=...
   ZALO_CHAT_ID=...
   ```
2. Cập nhật danh mục thực tế của bạn trong file `portfolio.json`:
   ```json
   {
     "FPT": { "avg_price": 95000, "quantity": 100 },
     "VNM": { "avg_price": 68000, "quantity": 200 }
   }
   ```

### 3. Khởi động Bot

#### Cách 1: Chạy trực tiếp (Local Python)
```bash
pip install -r requirements.txt
python main.py
```

#### Cách 2: Chạy qua Docker (Khuyên dùng)
```bash
docker-compose up -d --build
```

## 📊 Logic Cảnh báo
- **Mua (Buy):** RSI < 30 hoặc Giá vượt MA20.
- **Chốt lời (Take Profit):** Lãi >= 15% và RSI > 70.
- **Cắt lỗ (Cut Loss):** Lỗ quá -7%.

## 📝 Lưu ý
- Bot truy vấn dữ liệu mỗi 15 phút một lần để tránh spam API.
- Dữ liệu `portfolio.json` được mount qua Docker Volume, bạn có thể sửa file này và restart container để cập nhật danh mục.

---
*Chúc bạn đầu tư thành công!* 🚀
