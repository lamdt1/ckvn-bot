# ✅ Production Deployment Checklist

## 📋 Pre-Deployment Verification

### **Hardware Requirements**
- [ ] Raspberry Pi 3B+ or Pi 4 (2GB+ RAM recommended)
- [ ] 16GB+ SD card (Class 10)
- [ ] Stable power supply (5V/2.5A)
- [ ] Internet connection (Ethernet preferred)
- [ ] Case with cooling (optional but recommended)

### **Software Requirements**
- [ ] Raspberry Pi OS (64-bit recommended)
- [ ] Python 3.9+ installed
- [ ] Git installed
- [ ] SQLite3 installed
- [ ] 2GB+ swap configured

---

## 🚀 Installation Steps

### **Step 1: System Preparation**
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3-pip python3-venv sqlite3 git htop

# Verify Python version
python3 --version  # Should be 3.9+
```
- [ ] System updated
- [ ] Dependencies installed
- [ ] Python 3.9+ verified

### **Step 2: Repository Setup**
```bash
# Clone repository
cd ~/
git clone https://github.com/yourusername/ckbot.git
cd ckbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r bot/requirements.txt
```
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed

### **Step 3: Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required settings:**
- [ ] `BOT_DATA_SOURCE=vnstock`
- [ ] `BOT_SYMBOLS` configured (start with 3-5 symbols)
- [ ] `BOT_TOTAL_CAPITAL` set
- [ ] `BOT_TELEGRAM_TOKEN` configured
- [ ] `BOT_TELEGRAM_CHAT_ID` configured
- [ ] `BOT_ZALO_TOKEN` configured (optional)
- [ ] `BOT_ZALO_CHAT_ID` configured (optional)
- [ ] `BOT_RUN_TIME` set (e.g., 15:30)

### **Step 4: Database Initialization**
```bash
# Create database directory
mkdir -p database logs

# Initialize database
python3 -c "from database.db_manager import TradingDatabase; db = TradingDatabase(); print('✅ Database initialized')"

# Optimize database
python3 scripts/optimize_database.py database/trading.db
```
- [ ] Database directory created
- [ ] Database initialized
- [ ] Database optimized

### **Step 5: Test Run**
```bash
# Activate virtual environment
source venv/bin/activate

# Test run (once mode)
python3 bot/main.py --mode once

# Check logs
tail -f logs/bot.log
```
- [ ] Test run successful
- [ ] Signals generated
- [ ] Notifications received
- [ ] No errors in logs

---

## 📱 Notification Setup

### **Telegram**
- [ ] Bot created via @BotFather
- [ ] Token obtained
- [ ] Chat ID obtained (via test message)
- [ ] Test notification successful

**Verify:**
```bash
python3 -c "from bot.notification import TelegramNotifier; t = TelegramNotifier('TOKEN', 'CHAT_ID'); t.send_test_message()"
```

### **Zalo (Optional)**
- [ ] Zalo bot created
- [ ] Token obtained
- [ ] Chat ID obtained
- [ ] Test notification successful

**Verify:**
```bash
python3 -c "from bot.notification import ZaloNotifier; z = ZaloNotifier('TOKEN', 'CHAT_ID'); z.send_test_message()"
```

---

## ⏰ Scheduling Setup

### **Option 1: Cron (Recommended)**
```bash
# Edit crontab
crontab -e

# Add daily run at 15:30 (after market close)
30 15 * * 1-5 cd /home/pi/ckbot && /home/pi/ckbot/venv/bin/python3 bot/main.py --mode once >> logs/bot.log 2>&1

# Add monthly database cleanup (1st of month at 2am)
0 2 1 * * cd /home/pi/ckbot && /home/pi/ckbot/venv/bin/python3 scripts/optimize_database.py database/trading.db >> logs/db_cleanup.log 2>&1
```
- [ ] Crontab configured
- [ ] Daily run scheduled
- [ ] Monthly cleanup scheduled
- [ ] Cron tested (wait for scheduled time or use `* * * * *` for testing)

### **Option 2: Systemd Service**
```bash
# Create service file
sudo nano /etc/systemd/system/trading-bot.service
```

**Service content:**
```ini
[Unit]
Description=Pro Trader Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ckbot
Environment="PATH=/home/pi/ckbot/venv/bin"
ExecStart=/home/pi/ckbot/venv/bin/python3 bot/main.py --mode scheduled --time 15:30
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot
```
- [ ] Service file created
- [ ] Service enabled
- [ ] Service started
- [ ] Status verified

---

## 🔧 Optimization

### **Memory Optimization**
```bash
# Check current swap
free -h

# Create 2GB swap (if needed)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Configure Python
echo 'export PYTHONOPTIMIZE=1' >> ~/.bashrc
echo 'export MALLOC_TRIM_THRESHOLD_=100000' >> ~/.bashrc
source ~/.bashrc
```
- [ ] Swap configured (2GB+)
- [ ] Python optimized
- [ ] Environment variables set

### **Database Optimization**
```bash
# Run optimization
python3 scripts/optimize_database.py database/trading.db
```
- [ ] Indexes created
- [ ] Old data cleaned
- [ ] Database vacuumed
- [ ] Statistics analyzed

---

## 🔍 Monitoring Setup

### **Resource Monitoring**
```bash
# One-time check
python3 utils/resource_monitor.py

# Continuous monitoring (optional)
python3 utils/resource_monitor.py --continuous 60
```
- [ ] Resource monitor tested
- [ ] CPU < 80%
- [ ] Memory < 80%
- [ ] Disk < 90%

### **Log Monitoring**
```bash
# Create log rotation
sudo nano /etc/logrotate.d/trading-bot
```

**Content:**
```
/home/pi/ckbot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```
- [ ] Log rotation configured
- [ ] Logs directory created
- [ ] Log files writable

---

## 🔒 Security

### **File Permissions**
```bash
# Secure .env file
chmod 600 .env

# Verify .gitignore
cat .gitignore | grep .env
```
- [ ] .env file secured (600)
- [ ] .env in .gitignore
- [ ] No sensitive data in git

### **Firewall (Optional)**
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Check status
sudo ufw status
```
- [ ] Firewall enabled (optional)
- [ ] SSH allowed
- [ ] Status verified

---

## 📊 Performance Validation

### **System Resources**
- [ ] CPU usage < 50% during run
- [ ] Memory usage < 500MB
- [ ] Database size < 100MB
- [ ] Temperature < 70°C

### **Bot Performance**
- [ ] Symbols processed: 5+ per minute
- [ ] Signals generated successfully
- [ ] Notifications sent successfully
- [ ] Database updated correctly

---

## 🧪 Testing

### **Functional Tests**
- [ ] Data fetching works
- [ ] Indicators calculated correctly
- [ ] Signals generated
- [ ] Performance filter working
- [ ] Notifications sent
- [ ] Database updated

### **Error Handling**
- [ ] Network timeout handled
- [ ] API error handled
- [ ] Database lock handled
- [ ] Retry logic working

### **Integration Tests**
- [ ] End-to-end workflow successful
- [ ] Telegram notifications received
- [ ] Zalo notifications received (if enabled)
- [ ] Database queries fast (< 100ms)

---

## 📚 Documentation Review

- [ ] `README.md` read
- [ ] `IMPLEMENTATION_PLAN.md` reviewed
- [ ] `docs/RASPBERRY_PI_SETUP.md` followed
- [ ] `docs/TELEGRAM_SETUP.md` completed
- [ ] `docs/ZALO_SETUP.md` completed (if using Zalo)
- [ ] `SYSTEM_REVIEW.md` reviewed

---

## 🔄 Backup Strategy

### **Database Backup**
```bash
# Create backup script
nano scripts/backup_database.sh
```

**Content:**
```bash
#!/bin/bash
BACKUP_DIR="/home/pi/ckbot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /home/pi/ckbot/database/trading.db $BACKUP_DIR/trading_$DATE.db
# Keep only last 7 backups
ls -t $BACKUP_DIR/trading_*.db | tail -n +8 | xargs rm -f
echo "Backup completed: trading_$DATE.db"
```

```bash
# Make executable
chmod +x scripts/backup_database.sh

# Add to crontab (daily at 1am)
0 1 * * * /home/pi/ckbot/scripts/backup_database.sh >> /home/pi/ckbot/logs/backup.log 2>&1
```
- [ ] Backup script created
- [ ] Backup directory created
- [ ] Backup scheduled
- [ ] Backup tested

### **Configuration Backup**
```bash
# Backup .env (manually, securely)
cp .env .env.backup
chmod 600 .env.backup
```
- [ ] .env backed up
- [ ] Backup secured

---

## 🎯 Production Readiness

### **Code Quality**
- [ ] No syntax errors
- [ ] No runtime errors
- [ ] Logging configured
- [ ] Error handling implemented

### **Performance**
- [ ] Database optimized
- [ ] Memory managed
- [ ] Batch processing enabled
- [ ] Resource monitoring active

### **Reliability**
- [ ] Retry logic tested
- [ ] Circuit breaker tested
- [ ] Graceful shutdown tested
- [ ] Error recovery tested

### **Monitoring**
- [ ] Resource monitoring working
- [ ] Health checks passing
- [ ] Performance tracking enabled
- [ ] Alert system working

---

## 📈 Post-Deployment

### **Week 1: Monitoring**
- [ ] Check logs daily
- [ ] Monitor resources
- [ ] Verify notifications
- [ ] Review signals

### **Week 2-4: Validation**
- [ ] Compare with backtest
- [ ] Analyze performance
- [ ] Tune parameters
- [ ] Document issues

### **Month 2-3: Optimization**
- [ ] Optimize parameters
- [ ] Add more symbols (gradually)
- [ ] Review win rate
- [ ] Adjust thresholds

---

## ✅ Final Checklist

### **Critical Items**
- [ ] ✅ All dependencies installed
- [ ] ✅ Configuration complete
- [ ] ✅ Database initialized & optimized
- [ ] ✅ Notifications working (Telegram + Zalo)
- [ ] ✅ Scheduling configured (cron or systemd)
- [ ] ✅ Test run successful
- [ ] ✅ Logs directory created
- [ ] ✅ Backup strategy implemented
- [ ] ✅ Resource monitoring active
- [ ] ✅ Documentation reviewed

### **Optional Items**
- [ ] Zalo notifications configured
- [ ] Systemd service setup
- [ ] Firewall enabled
- [ ] Log rotation configured
- [ ] Continuous monitoring setup

---

## 🚀 Deployment Sign-off

**Deployment Date:** _______________

**Deployed By:** _______________

**Configuration:**
- Raspberry Pi Model: _______________
- RAM: _______________
- Symbols: _______________
- Capital: _______________
- Notifications: Telegram [ ] Zalo [ ]
- Scheduling: Cron [ ] Systemd [ ]

**Initial Test Results:**
- Test run: Success [ ] Failed [ ]
- Notifications: Success [ ] Failed [ ]
- Database: Success [ ] Failed [ ]
- Resources: Normal [ ] High [ ]

**Sign-off:**
- [ ] All critical items completed
- [ ] System tested and verified
- [ ] Documentation reviewed
- [ ] Ready for production

**Signature:** _______________

---

## 📞 Support

**Issues?**
1. Check logs: `tail -f logs/bot.log`
2. Check resources: `python3 utils/resource_monitor.py`
3. Review documentation: `docs/RASPBERRY_PI_SETUP.md`
4. Check troubleshooting: `SYSTEM_REVIEW.md`

**Emergency Stop:**
```bash
# Stop cron job
crontab -e  # Comment out the line

# Or stop systemd service
sudo systemctl stop trading-bot
```

---

**Deployment Checklist Complete!** ✅

**Status:** Ready for Production  
**Next Step:** Monitor for 1 week, then enable live trading (small capital)

**Good luck with your trading bot!** 🚀📈
