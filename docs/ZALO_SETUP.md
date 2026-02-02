# 📱 Zalo Bot Setup Guide

## 🎯 Overview

Hướng dẫn chi tiết để setup Zalo bot nhận alerts từ Pro Trader Bot.

Zalo là nền tảng nhắn tin phổ biến nhất tại Việt Nam, rất phù hợp cho trading alerts!

---

## 📋 Prerequisites

- Tài khoản Zalo
- Smartphone hoặc Zalo PC
- 10-15 phút setup time

---

## 🚀 Step-by-Step Setup

### **Step 1: Tạo Zalo Bot**

1. **Mở Zalo** trên điện thoại hoặc PC

2. **Tìm kiếm:** `Zalo Bot Manager`

3. **Chọn:** "Tạo bot" trong menu chat

4. **Nhập thông tin Bot:**
   - Tên Bot: `Bot Pro Trader` (phải bắt đầu bằng "Bot")
   - Mô tả: `Trading signal alerts`
   
5. **Nhấn "Tạo Bot"**

6. **Nhận Bot Token:**
   - Hệ thống sẽ gửi Bot Token qua tin nhắn Zalo
   - Token có dạng: `123456789:ABCxyz...`
   
   ⚠️ **LƯU Ý:** Lưu token này cẩn thận!

---

### **Step 2: Lấy Chat ID**

**Cách 1: Sử dụng script test**

1. **Tạo file test:**
   ```bash
   cd /Volumes/Data/projects/ckbot
   nano test_zalo_id.py
   ```

2. **Paste code:**
   ```python
   import httpx
   import time
   
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Thay bằng token của bạn
   url = f"https://bot-api.zaloplatforms.com/bot{BOT_TOKEN}/getUpdates"
   
   print("🚀 Đang chờ tin nhắn từ Zalo... (Hãy nhắn tin cho Bot của bạn)")
   
   while True:
       try:
           response = httpx.post(url, json={"timeout": 30}, timeout=40.0)
           data = response.json()
   
           if data.get("ok"):
               if data.get("result"):
                   result = data["result"]
                   message = result.get("message", {})
                   chat_id = message.get("chat", {}).get("id")
                   
                   if chat_id:
                       print(f"\n✅ Tìm thấy! ZALO_CHAT_ID của bạn: {chat_id}")
                       break
               else:
                   print(".", end="", flush=True)
           else:
               if "Request timeout" in str(data.get("description")):
                   print(".", end="", flush=True)
               else:
                   print(f"\n❌ Lỗi API: {data.get('description')}")
                   if data.get("error_code") == 401:
                       break
                   
       except httpx.ReadTimeout:
           print(".", end="", flush=True)
       except Exception as e:
           print(f"\n❌ Lỗi: {e}")
           time.sleep(5)
   
       time.sleep(1)
   ```

3. **Chạy script:**
   ```bash
   python3 test_zalo_id.py
   ```

4. **Nhắn tin cho Bot:**
   - Mở Zalo, tìm bot của bạn
   - Gửi tin nhắn bất kỳ (ví dụ: "Hello")
   - Script sẽ hiển thị Chat ID

5. **Copy Chat ID** (dạng: `abc123xyz`)

**Cách 2: Manual (nếu script không hoạt động)**

1. Sử dụng Postman hoặc curl để gọi API `getUpdates`
2. Nhắn tin cho bot
3. Tìm `chat.id` trong response

---

### **Step 3: Configure .env File**

1. **Navigate to project:**
   ```bash
   cd /Volumes/Data/projects/ckbot
   ```

2. **Edit .env:**
   ```bash
   nano .env
   ```

3. **Add Zalo configuration:**
   ```env
   # Zalo Notifications
   BOT_ZALO_ENABLED=true
   BOT_ZALO_TOKEN=123456789:ABCxyz...
   BOT_ZALO_CHAT_ID=abc123xyz
   ```
   
   **Replace:**
   - `123456789:ABCxyz...` → Your bot token
   - `abc123xyz` → Your chat ID

4. **Save:** `Ctrl+X`, `Y`, `Enter`

---

### **Step 4: Install Dependencies**

```bash
# Install httpx for Zalo API
pip install httpx

# Or install all dependencies
pip install -r bot/requirements.txt
```

---

### **Step 5: Test Notifications**

1. **Create test script:**
   ```bash
   nano test_zalo_notification.py
   ```

2. **Add code:**
   ```python
   import os
   from bot.notification import ZaloNotifier
   from strategies.signal import Signal, SignalType
   from datetime import datetime
   
   # Load from .env
   from dotenv import load_dotenv
   load_dotenv()
   
   # Initialize Zalo notifier
   notifier = ZaloNotifier(
       bot_token=os.getenv('BOT_ZALO_TOKEN'),
       chat_id=os.getenv('BOT_ZALO_CHAT_ID')
   )
   
   # Create test signal
   test_signal = Signal(
       symbol='VNM',
       timeframe='1D',
       timestamp=int(datetime.now().timestamp()),
       signal_type=SignalType.STRONG_BUY,
       price=86000,
       confidence_score=85.5,
       strategy_name='Pro Trader - Test',
       reasoning={
           'trend_reason': 'Xu hướng tăng mạnh',
           'momentum_reason': 'MACD tăng, RSI trung tính',
           'volume_reason': 'Khối lượng cao xác nhận mua',
           'entry_reason': 'Gần dải Bollinger dưới'
       },
       conditions_met=['trend_favorable', 'momentum_strong'],
       stop_loss=81700,
       take_profit=94600,
       position_size_pct=5.0,
       risk_reward_ratio=2.0
   )
   
   # Send test alert
   print("Đang gửi test alert...")
   success = notifier.send_signal_alert(test_signal)
   
   if success:
       print("✅ Gửi alert thành công!")
       print("Kiểm tra Zalo app của bạn")
   else:
       print("❌ Gửi alert thất bại")
       print("Kiểm tra token và chat ID")
   ```

3. **Run test:**
   ```bash
   python3 test_zalo_notification.py
   ```

4. **Check Zalo app** - bạn sẽ nhận được message:

   ```
   🟢🟢 STRONG_BUY
   
   Mã: VNM
   Giá: 86,000 VND
   Độ tin cậy: 85.5%
   
   🛡️ Quản lý rủi ro:
   • Cắt lỗ: 81,700 VND (-5.00%)
   • Chốt lời: 94,600 VND (+10.00%)
   • R/R: 2.00
   • Tỷ lệ vị thế: 5.0%
   
   📊 Phân tích:
   • Xu hướng: Xu hướng tăng mạnh
   • Động lượng: MACD tăng, RSI trung tính
   • Khối lượng: Khối lượng cao xác nhận mua
   • Điểm vào: Gần dải Bollinger dưới
   
   ⚠️ Cần xem xét thủ công trước khi giao dịch
   Thời gian: 2026-02-03 01:50:00
   ```

---

## ✅ Verification Checklist

- [ ] Bot created via Zalo Bot Manager
- [ ] Bot token received
- [ ] Chat ID obtained
- [ ] .env file configured
- [ ] httpx installed
- [ ] Test alert received successfully

---

## 🎨 Message Format

### **1. Signal Alert**

```
🟢🟢 STRONG_BUY

Mã: VNM
Giá: 86,000 VND
Độ tin cậy: 85.5%

🛡️ Quản lý rủi ro:
• Cắt lỗ: 81,700 VND (-5.00%)
• Chốt lời: 94,600 VND (+10.00%)
• R/R: 2.00
• Tỷ lệ vị thế: 5.0%

📊 Phân tích:
• Xu hướng: Xu hướng tăng mạnh
• Động lượng: MACD tăng, RSI trung tính
• Khối lượng: Khối lượng cao xác nhận mua
• Điểm vào: Gần dải Bollinger dưới

⚠️ Cần xem xét thủ công trước khi giao dịch
```

### **2. Position Alert**

```
🔴 VỊ THẾ ĐÓNG

Mã: VCB
Hành động: STOP_LOSS
Giá: 87,400 VND
📉 P&L: -5.00%
Lý do: STOP_LOSS_TRIGGERED
```

### **3. Daily Summary**

```
📊 BÁO CÁO CUỐI NGÀY

Ngày: 2026-02-03

📈 Tín hiệu tạo ra: 8
   • MUA MẠNH: 2
   • MUA YẾU: 3
   • THEO DÕI: 3

💼 Vị thế mở: 3
💰 Tổng P&L: +8.50%

✅ Đóng hôm nay: 2
   • Thắng: 1
   • Thua: 1
```

---

## 🔧 Troubleshooting

### Issue: "Token không hợp lệ"

**Solution:**
- Kiểm tra token có đúng format không
- Token phải có dạng: `123456789:ABCxyz...`
- Không có khoảng trắng thừa
- Nếu cần, tạo lại bot và lấy token mới

### Issue: "Chat not found"

**Solution:**
- Đảm bảo đã nhắn tin cho bot trước
- Chat ID phải chính xác
- Chạy lại script test để lấy chat ID

### Issue: "httpx not installed"

**Solution:**
```bash
pip install httpx
```

### Issue: "Không nhận được alert"

**Solution:**
1. Kiểm tra .env file có đúng không
2. Kiểm tra `BOT_ZALO_ENABLED=true`
3. Chạy test script để verify
4. Xem bot logs để tìm lỗi

---

## 🔒 Security Best Practices

### 1. Bảo mật Token

⚠️ **KHÔNG commit .env file lên Git!**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

### 2. Reset Token nếu bị lộ

Nếu token bị lộ:
1. Mở Zalo Bot Creator
2. Chọn bot của bạn
3. Vào "Thiết lập"
4. Chọn "Reset Token"
5. Cập nhật .env file

### 3. Hạn chế truy cập

- Chỉ bạn nên có quyền truy cập bot
- Không chia sẻ token công khai
- Theo dõi hoạt động của bot

---

## 📱 So sánh Telegram vs Zalo

| Feature | Telegram | Zalo |
|---------|----------|------|
| **Phổ biến tại VN** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Setup dễ dàng** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **HTML formatting** | ✅ | ❌ |
| **Emoji support** | ✅ | ✅ |
| **API stability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Free tier** | Unlimited | 100 bots |

**Khuyến nghị:** Dùng CẢ HAI để backup!

---

## 🎯 Dual Channel Setup

Để nhận alerts qua cả Telegram VÀ Zalo:

```env
# .env file

# Telegram
BOT_TELEGRAM_ENABLED=true
BOT_TELEGRAM_TOKEN=your_telegram_token
BOT_TELEGRAM_CHAT_ID=your_telegram_chat_id

# Zalo
BOT_ZALO_ENABLED=true
BOT_ZALO_TOKEN=your_zalo_token
BOT_ZALO_CHAT_ID=your_zalo_chat_id
```

Bot sẽ tự động gửi alerts qua CẢ HAI kênh! 🎉

---

## 📚 Zalo Bot API Reference

- **Base URL:** `https://bot-api.zaloplatforms.com/bot{TOKEN}/`
- **Methods:**
  - `getMe` - Kiểm tra bot info
  - `getUpdates` - Nhận tin nhắn (polling)
  - `sendMessage` - Gửi tin nhắn
  - `sendPhoto` - Gửi ảnh
  - `setWebhook` - Setup webhook

**Full docs:** `/Volumes/Data/projects/ckbot/docs/zalo-bot-doc.md`

---

## 🚀 Next Steps

After successful setup:

1. ✅ **Test với bot run:**
   ```bash
   python3 bot/main.py --mode once
   ```

2. ✅ **Monitor alerts** trong giờ giao dịch

3. ✅ **Review signals** manually

4. ✅ **Track performance**

5. ✅ **Optimize** dựa trên kết quả

---

## 💡 Pro Tips

1. **Dual Channel:** Dùng cả Telegram + Zalo để không bỏ lỡ alerts
2. **Test Daily:** Chạy test script hàng ngày để đảm bảo bot hoạt động
3. **Backup Token:** Lưu token ở nơi an toàn (password manager)
4. **Monitor Logs:** Kiểm tra logs thường xuyên
5. **Update Regular:** Cập nhật dependencies định kỳ

---

**Setup Complete!** 🎉

Bạn đã sẵn sàng nhận trading alerts qua Zalo!

**Lưu ý:** Luôn review signals manually trước khi trade! 🛡️
