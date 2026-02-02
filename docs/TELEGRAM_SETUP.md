# 📱 Telegram Bot Setup Guide

## 🎯 Overview

Hướng dẫn chi tiết để setup Telegram bot nhận alerts từ Pro Trader Bot.

---

## 📋 Prerequisites

- Tài khoản Telegram
- Smartphone hoặc Telegram Desktop
- 5-10 phút setup time

---

## 🚀 Step-by-Step Setup

### **Step 1: Create Telegram Bot**

1. **Mở Telegram** và search `@BotFather`

2. **Start conversation** với BotFather

3. **Send command:** `/newbot`

4. **Follow prompts:**
   ```
   BotFather: Alright, a new bot. How are we going to call it?
   You: Pro Trader Alert Bot
   
   BotFather: Good. Now let's choose a username for your bot.
   You: pro_trader_alert_bot
   ```
   
   **Note:** Username phải unique và end với `_bot`

5. **Copy Bot Token:**
   ```
   BotFather: Done! Congratulations on your new bot.
   
   Use this token to access the HTTP API:
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   
   Keep your token secure!
   ```
   
   ⚠️ **IMPORTANT:** Lưu token này, bạn sẽ cần nó!

---

### **Step 2: Get Your Chat ID**

1. **Search `@userinfobot`** trong Telegram

2. **Start conversation**

3. Bot sẽ reply với thông tin của bạn:
   ```
   Id: 123456789
   First name: Your Name
   Username: @your_username
   ```

4. **Copy Chat ID** (số `Id`)

---

### **Step 3: Test Bot Connection**

1. **Search bot của bạn** trong Telegram (username bạn đã tạo)

2. **Start conversation** với bot

3. **Send message:** `/start`

4. Bot sẽ **không reply** (chưa có code) - đây là bình thường!

---

### **Step 4: Configure .env File**

1. **Navigate to project directory:**
   ```bash
   cd /Volumes/Data/projects/ckbot
   ```

2. **Edit .env file:**
   ```bash
   nano .env
   ```

3. **Add Telegram configuration:**
   ```env
   # Telegram Notifications
   BOT_TELEGRAM_ENABLED=true
   BOT_TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   BOT_TELEGRAM_CHAT_ID=123456789
   ```
   
   **Replace:**
   - `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` → Your bot token
   - `123456789` → Your chat ID

4. **Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

---

### **Step 5: Install Dependencies**

```bash
# Install python-telegram-bot
pip install python-telegram-bot

# Or install all bot dependencies
pip install -r bot/requirements.txt
```

---

### **Step 6: Test Notifications**

1. **Create test script:**
   ```bash
   nano test_telegram.py
   ```

2. **Add test code:**
   ```python
   import os
   from bot.notification import NotificationManager
   from strategies.signal import Signal, SignalType
   from datetime import datetime
   
   # Load from .env
   from dotenv import load_dotenv
   load_dotenv()
   
   # Initialize notification manager
   notifier = NotificationManager(
       telegram_token=os.getenv('BOT_TELEGRAM_TOKEN'),
       telegram_chat_id=os.getenv('BOT_TELEGRAM_CHAT_ID')
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
           'trend_reason': 'Strong uptrend confirmed',
           'momentum_reason': 'MACD bullish, RSI neutral',
           'volume_reason': 'High volume confirms buying',
           'entry_reason': 'Near lower Bollinger Band'
       },
       conditions_met=['trend_favorable', 'momentum_strong'],
       stop_loss=81700,
       take_profit=94600,
       position_size_pct=5.0,
       risk_reward_ratio=2.0
   )
   
   # Send test alert
   print("Sending test alert...")
   success = notifier.send_signal_alert(test_signal)
   
   if success:
       print("✅ Test alert sent successfully!")
       print("Check your Telegram app")
   else:
       print("❌ Failed to send alert")
       print("Check your token and chat ID")
   ```

3. **Run test:**
   ```bash
   python3 test_telegram.py
   ```

4. **Check Telegram app** - bạn sẽ nhận được message như này:

   ```
   🟢🟢 STRONG_BUY
   
   Symbol: VNM
   Price: 86,000 VND
   Confidence: 85.5%
   
   🛡️ Risk Management:
   • Stop-Loss: 81,700 VND (-5.00%)
   • Take-Profit: 94,600 VND (+10.00%)
   • R/R Ratio: 2.00
   • Position Size: 5.0%
   
   📊 Analysis:
   • Trend: Strong uptrend confirmed
   • Momentum: MACD bullish, RSI neutral
   • Volume: High volume confirms buying
   • Entry: Near lower Bollinger Band
   
   ⚠️ Manual review required before trading
   Time: 2026-02-03 01:45:00
   ```

---

## ✅ Verification Checklist

- [ ] Bot created with @BotFather
- [ ] Bot token copied
- [ ] Chat ID obtained from @userinfobot
- [ ] .env file configured
- [ ] python-telegram-bot installed
- [ ] Test alert received successfully

---

## 🎨 Customizing Alerts

### Emoji Meanings

| Emoji | Signal Type |
|-------|-------------|
| 🟢🟢 | STRONG_BUY |
| 🟢 | WEAK_BUY |
| 👀 | WATCH |
| ⏸️ | NO_ACTION |
| 🔴 | STOP_LOSS |
| 🟢 | TAKE_PROFIT |

### Alert Types

**1. Signal Alerts** (New trading opportunities)
- Symbol, price, confidence
- Risk management details
- Analysis breakdown
- Manual review reminder

**2. Position Alerts** (Stop-loss / Take-profit triggered)
- Symbol, action (STOP_LOSS/TAKE_PROFIT)
- Close price, P&L %
- Reason

**3. Daily Summary** (End of day report)
- Signals generated today
- Open positions
- Total P&L
- Closed positions stats

---

## 🔧 Troubleshooting

### Issue: "Bot not found"

**Solution:**
- Check bot username is correct
- Make sure you started conversation with bot
- Search again in Telegram

### Issue: "Unauthorized"

**Solution:**
- Check token is correct (no extra spaces)
- Token should look like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- Regenerate token if needed: `/token` to @BotFather

### Issue: "Chat not found"

**Solution:**
- Check chat ID is correct
- Make sure you sent `/start` to bot first
- Chat ID should be numbers only (no letters)

### Issue: "python-telegram-bot not installed"

**Solution:**
```bash
pip install python-telegram-bot
```

### Issue: "No alerts received"

**Solution:**
1. Check .env file has correct values
2. Check `BOT_TELEGRAM_ENABLED=true`
3. Run test script to verify connection
4. Check bot logs for errors

---

## 🔒 Security Best Practices

### 1. Keep Token Secret

⚠️ **NEVER commit .env file to Git!**

```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

### 2. Regenerate Token if Leaked

If token is accidentally exposed:
1. Go to @BotFather
2. Send `/token`
3. Select your bot
4. Click "Regenerate Token"
5. Update .env file

### 3. Restrict Bot Access

Only you should have access to your bot:
- Don't share bot username publicly
- Don't add bot to groups (unless needed)
- Monitor bot activity

---

## 📱 Advanced Features

### Multiple Chat IDs (Group Alerts)

To send alerts to multiple people:

```env
# .env
BOT_TELEGRAM_CHAT_ID=123456789,987654321,555555555
```

Update notification.py to support multiple IDs.

### Custom Alert Templates

Edit `bot/notification.py` to customize message format:

```python
def _format_signal_message(self, signal: Signal) -> str:
    # Customize message here
    message = f"""
    🚀 NEW SIGNAL!
    
    {signal.symbol} @ {signal.price:,.0f}
    Confidence: {signal.confidence_score}%
    
    Your custom format here...
    """
    return message
```

### Silent Notifications

For non-urgent alerts:

```python
self.bot.send_message(
    chat_id=self.chat_id,
    text=message,
    parse_mode='HTML',
    disable_notification=True  # Silent notification
)
```

---

## 🎯 Next Steps

After successful setup:

1. ✅ **Test with real bot run:**
   ```bash
   python3 bot/main.py --mode once
   ```

2. ✅ **Monitor alerts** during market hours

3. ✅ **Review and act** on signals manually

4. ✅ **Track performance** of acted signals

5. ✅ **Optimize** based on results

---

## 📚 Additional Resources

- [Telegram Bot API Docs](https://core.telegram.org/bots/api)
- [python-telegram-bot Docs](https://python-telegram-bot.readthedocs.io/)
- [BotFather Commands](https://core.telegram.org/bots#6-botfather)

---

**Setup Complete!** 🎉

Bạn đã sẵn sàng nhận alerts từ Pro Trader Bot qua Telegram!

**Remember:** Always review signals manually before trading! 🛡️
