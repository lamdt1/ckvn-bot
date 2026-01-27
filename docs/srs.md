# TÀI LIỆU YÊU CẦU HỆ THỐNG (SRS)

## DỰ ÁN: VIETNAM STOCK TRADING BOT (BACKEND)

### 1. Thông tin chung

* **Tên dự án:** Vietnam Stock Alert Bot
* **Ngôn ngữ:** Python 3.x
* **Nền tảng mục tiêu:** Telegram (Backend Integration)
* **Tần suất cập nhật:** 15 phút/lần (trong giờ giao dịch)

---

### 2. Phạm vi hệ thống

Hệ thống là một công cụ Backend chạy ngầm, tự động truy vấn dữ liệu từ thị trường chứng khoán Việt Nam, thực hiện đối chiếu với danh mục thực tế của người dùng và đưa ra các cảnh báo mua/bán thông minh qua Telegram/Zalo.

---

### 3. Yêu cầu chức năng (Functional Requirements)

| ID | Chức năng | Mô tả chi tiết |
| --- | --- | --- |
| **FR-01** | **Truy vấn dữ liệu** | Sử dụng API/Thư viện `vnstock` để lấy giá Real-time và dữ liệu lịch sử (HOSE, HNX, UPCOM). |
| **FR-02** | **Quản lý Danh mục** | Lưu trữ lịch sử giao dịch thực tế của người dùng (Mã CP, Giá vốn trung bình, Khối lượng). |
| **FR-03** | **Phân tích Kỹ thuật** | Tự động tính toán các chỉ báo: RSI (14 ngày), MA20 từ dữ liệu lịch sử 30 phiên gần nhất. |
| **FR-04** | **Tính toán Lãi/Lỗ** | So sánh giá hiện tại với giá vốn thực tế để tính toán % Lãi/Lỗ tại từng thời điểm. |
| **FR-05** | **Logic Cảnh báo** | Đưa ra khuyến nghị dựa trên sự kết hợp giữa kỹ thuật và vị thế: <br>

<br> - **Mua:** RSI < 30 hoặc giá vượt MA20. <br>

<br> - **Bán/Chốt lời:** Lãi đạt ngưỡng (15%) + RSI > 70. <br>

<br> - **Cắt lỗ:** Lỗ vượt ngưỡng cấu hình (-7%). |
| **FR-06** | **Tích hợp Bot** | Gửi thông báo định dạng Markdown qua Telegram Bot API (hoặc Zalo Webhook). |

---

### 4. Yêu cầu kỹ thuật (Technical Requirements)

#### 4.1. Biến môi trường (Environment Variables)

Nhóm phát triển cần cấu hình file `.env` chứa các tham số:

* `TELEGRAM_BOT_TOKEN`: Token định danh bot.
* `TELEGRAM_CHAT_ID`: ID người nhận thông báo.
* `PROFIT_THRESHOLD`: Ngưỡng lãi kỳ vọng (mặc định 15.0).
* `LOSS_THRESHOLD`: Ngưỡng cắt lỗ (mặc định -7.0).

#### 4.2. Cấu trúc dữ liệu danh mục (Portfolio Schema)

Sử dụng file `portfolio.json` để lưu trữ dữ liệu mua bán:

```json
{
  "Mã_CP": {
    "avg_price": float,
    "quantity": int,
    "last_alert": timestamp
  }
}

```

#### 4.3. Quản lý tài nguyên

* Hệ thống chỉ thực thi hàm `fetch_data` trong khung giờ: **09:00 - 11:30** và **13:00 - 15:00**, từ **Thứ 2 đến Thứ 6**.
* Sử dụng `time.sleep(900)` giữa các chu kỳ để tránh spam API.

---

### 5. Kịch bản vận hành (Workflows)

1. **Bắt đầu chu kỳ:** Bot kiểm tra thời gian thực tế.
2. **Lấy dữ liệu:** Truy vấn giá hiện tại của danh mục theo dõi.
3. **Phân tích:**
* Tính toán PnL (Lãi/Lỗ) dựa trên `avg_price`.
* Tính toán RSI dựa trên dữ liệu lịch sử từ `vnstock`.


4. **Kiểm tra điều kiện:** Nếu vi phạm ngưỡng an toàn hoặc chạm điểm chốt lời kỹ thuật, khởi tạo chuỗi thông báo.
5. **Gửi thông báo:** Đẩy tin nhắn định dạng Markdown về Telegram.

---

### 6. Ghi chú cho nhóm phát triển

* Ưu tiên xử lý ngoại lệ (Exception Handling) khi mất kết nối mạng hoặc API từ phía nguồn cung cấp bị lỗi.
* Tin nhắn Telegram cần sử dụng Emoji để tăng trải nghiệm người dùng (Ví dụ: 🟢 cho Mua, 🔴 cho Bán, ⚠️ cho Cảnh báo).