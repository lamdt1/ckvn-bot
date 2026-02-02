# 🍓 Raspberry Pi Setup Guide

## 📋 Overview

Hướng dẫn deploy Pro Trader Bot lên Raspberry Pi 3+ để chạy 24/7.

Bot đã được optimize cho môi trường resource-constrained (RAM hạn chế, SD card storage).

---

## 🎯 Requirements

### **Hardware**
- Raspberry Pi 3B+ hoặc Pi 4 (khuyến nghị 2GB+ RAM)
- SD card 16GB+ (Class 10)
- Power supply 5V/2.5A
- Internet connection (Ethernet hoặc WiFi)

### **Software**
- Raspberry Pi OS (64-bit recommended)
- Python 3.9+
- SQLite3
- Git

---

## 🚀 Installation Steps

### **Step 1: Prepare Raspberry Pi**

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    sqlite3 \
    git \
    htop

# Check Python version
python3 --version  # Should be 3.9+
```

### **Step 2: Clone Repository**

```bash
# Create project directory
mkdir -p ~/projects
cd ~/projects

# Clone repository
git clone https://github.com/yourusername/ckbot.git
cd ckbot
```

### **Step 3: Setup Virtual Environment**

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### **Step 4: Install Dependencies**

```bash
# Install bot dependencies
pip install -r bot/requirements.txt

# Verify installation
python3 -c "import pandas, numpy, vnstock; print('✅ Dependencies OK')"
```

### **Step 5: Configure Bot**

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Minimum configuration:**
```env
# Data Source
BOT_DATA_SOURCE=vnstock
BOT_SYMBOLS=VNM,VCB,HPG,VIC,VHM

# Capital
BOT_TOTAL_CAPITAL=100000000

# Risk Management
BOT_STOP_LOSS_PCT=5.0
BOT_TAKE_PROFIT_PCT=10.0

# Learning (Enable for Pi)
BOT_ENABLE_LEARNING=true
BOT_MIN_TRADES_FOR_FILTER=5
BOT_MIN_WIN_RATE=40.0

# Notifications
BOT_TELEGRAM_ENABLED=true
BOT_TELEGRAM_TOKEN=your_token
BOT_TELEGRAM_CHAT_ID=your_chat_id

# Schedule
BOT_RUN_TIME=15:30
```

### **Step 6: Initialize Database**

```bash
# Create database directory
mkdir -p database

# Initialize database
python3 -c "from database.db_manager import TradingDatabase; db = TradingDatabase(); print('✅ Database initialized')"
```

### **Step 7: Optimize Database**

```bash
# Run optimization script
python3 scripts/optimize_database.py database/trading.db

# This will:
# - Create indexes
# - Clean old data
# - Vacuum database
# - Analyze statistics
```

---

## 🔧 Optimization for Raspberry Pi

### **1. Memory Optimization**

**Enable swap (if not already):**
```bash
# Check current swap
free -h

# Create 2GB swap file (if needed)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Configure Python for low memory:**
```bash
# Add to ~/.bashrc
echo 'export PYTHONOPTIMIZE=1' >> ~/.bashrc
echo 'export MALLOC_TRIM_THRESHOLD_=100000' >> ~/.bashrc

# Reload
source ~/.bashrc
```

### **2. Database Optimization**

**Automatic cleanup (cron job):**
```bash
# Edit crontab
crontab -e

# Add monthly cleanup (1st of month at 2am)
0 2 1 * * cd ~/projects/ckbot && /usr/bin/python3 scripts/optimize_database.py database/trading.db >> logs/db_cleanup.log 2>&1
```

### **3. Resource Monitoring**

**Check resources:**
```bash
# One-time check
python3 utils/resource_monitor.py

# Continuous monitoring (60s interval)
python3 utils/resource_monitor.py --continuous 60
```

**Monitor with htop:**
```bash
htop
```

---

## ⏰ Scheduling

### **Option 1: Cron (Recommended)**

```bash
# Edit crontab
crontab -e

# Add daily run at 15:30 (after market close)
30 15 * * 1-5 cd ~/projects/ckbot && /home/pi/projects/ckbot/venv/bin/python3 bot/main.py --mode once >> logs/bot.log 2>&1
```

### **Option 2: Systemd Service**

**Create service file:**
```bash
sudo nano /etc/systemd/system/trading-bot.service
```

**Content:**
```ini
[Unit]
Description=Pro Trader Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/projects/ckbot
Environment="PATH=/home/pi/projects/ckbot/venv/bin"
ExecStart=/home/pi/projects/ckbot/venv/bin/python3 bot/main.py --mode scheduled --time 15:30
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot

# View logs
sudo journalctl -u trading-bot -f
```

---

## 📊 Performance Tuning

### **Expected Resource Usage**

| Resource | Idle | Running | Peak |
|----------|------|---------|------|
| **CPU** | 5% | 30-50% | 80% |
| **RAM** | 200MB | 300-400MB | 500MB |
| **Disk** | 50MB | 100MB | 200MB |

### **Optimization Tips**

**1. Batch Processing:**
```python
# Process symbols in batches of 5
BOT_BATCH_SIZE=5
```

**2. Data Retention:**
```env
# Keep only 6 months of price data
# Cleanup script handles this
```

**3. Disable Unused Features:**
```env
# Disable email if not needed
BOT_EMAIL_ENABLED=false

# Use only one notification channel
BOT_TELEGRAM_ENABLED=true
BOT_ZALO_ENABLED=false
```

---

## 🔍 Monitoring & Maintenance

### **Daily Checks**

```bash
# Check bot logs
tail -f logs/bot.log

# Check system resources
python3 utils/resource_monitor.py

# Check database size
du -h database/trading.db
```

### **Weekly Maintenance**

```bash
# Update code
cd ~/projects/ckbot
git pull

# Restart service (if using systemd)
sudo systemctl restart trading-bot

# Check for updates
pip list --outdated
```

### **Monthly Maintenance**

```bash
# Optimize database
python3 scripts/optimize_database.py database/trading.db

# Clean logs
find logs/ -name "*.log" -mtime +30 -delete

# Update system
sudo apt-get update && sudo apt-get upgrade -y
```

---

## 🐛 Troubleshooting

### Issue: "Out of memory"

**Solution:**
```bash
# Increase swap
sudo swapoff /swapfile
sudo fallocate -l 4G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Reduce batch size
# Edit .env: BOT_BATCH_SIZE=3
```

### Issue: "Database locked"

**Solution:**
```bash
# Check for zombie processes
ps aux | grep python

# Kill if needed
kill -9 <PID>

# Restart bot
sudo systemctl restart trading-bot
```

### Issue: "Network timeout"

**Solution:**
```bash
# Check internet
ping -c 4 google.com

# Check DNS
cat /etc/resolv.conf

# Restart networking
sudo systemctl restart networking
```

### Issue: "High CPU usage"

**Solution:**
```bash
# Check what's using CPU
htop

# Reduce symbol count
# Edit .env: BOT_SYMBOLS=VNM,VCB,HPG

# Increase run interval
# Edit .env: BOT_RUN_INTERVAL_MINUTES=60
```

---

## 📈 Performance Benchmarks

### **Raspberry Pi 3B+ (1GB RAM)**

```
Symbol Processing: ~5 symbols/minute
Memory Usage: 350MB peak
Database Size: ~80MB (6 months data)
CPU Usage: 40-60% during run
```

### **Raspberry Pi 4 (2GB RAM)**

```
Symbol Processing: ~10 symbols/minute
Memory Usage: 400MB peak
Database Size: ~100MB (6 months data)
CPU Usage: 30-40% during run
```

---

## 🔒 Security Best Practices

### **1. Secure .env File**

```bash
# Set proper permissions
chmod 600 .env

# Never commit to git
echo ".env" >> .gitignore
```

### **2. Firewall**

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Check status
sudo ufw status
```

### **3. Auto Updates**

```bash
# Enable unattended upgrades
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📚 Useful Commands

### **Bot Management**

```bash
# Run once
python3 bot/main.py --mode once

# Run scheduled
python3 bot/main.py --mode scheduled --time 15:30

# Run continuous
python3 bot/main.py --mode continuous --interval 60
```

### **Database Management**

```bash
# Optimize
python3 scripts/optimize_database.py database/trading.db

# Query
sqlite3 database/trading.db "SELECT * FROM signal_performance;"

# Backup
cp database/trading.db database/trading_backup_$(date +%Y%m%d).db
```

### **System Monitoring**

```bash
# Resources
python3 utils/resource_monitor.py

# Logs
tail -f logs/bot.log

# System info
vcgencmd measure_temp  # Temperature
free -h                 # Memory
df -h                   # Disk
```

---

## 🎯 Production Checklist

- [ ] Raspberry Pi setup complete
- [ ] Dependencies installed
- [ ] .env configured
- [ ] Database initialized & optimized
- [ ] Telegram/Zalo bot configured
- [ ] Cron job or systemd service setup
- [ ] Swap enabled (2GB+)
- [ ] Resource monitoring tested
- [ ] Logs directory created
- [ ] Backup strategy defined
- [ ] Network connectivity verified
- [ ] Test run successful

---

## 🚀 Next Steps

After successful deployment:

1. **Monitor for 1 week** - Check logs daily
2. **Tune parameters** - Adjust based on performance
3. **Enable auto-trading** (optional) - After validation
4. **Scale up** - Add more symbols gradually

---

**Deployment Complete!** 🎉

Bot giờ chạy 24/7 trên Raspberry Pi với:
- ✅ Optimized database
- ✅ Memory management
- ✅ Error recovery
- ✅ Resource monitoring
- ✅ Automatic scheduling

**Happy Trading!** 📈
