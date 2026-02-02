"""
Bot Configuration
Centralized configuration for the trading bot
"""

import os
from typing import List, Optional
from pathlib import Path


class BotConfig:
    """
    Centralized configuration for trading bot
    
    Environment variables can override defaults:
    - BOT_DATA_SOURCE: 'vnstock' or 'ssi'
    - BOT_SYMBOLS: Comma-separated list of symbols
    - BOT_CAPITAL: Total capital
    - BOT_TELEGRAM_TOKEN: Telegram bot token
    - BOT_TELEGRAM_CHAT_ID: Telegram chat ID
    """
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATABASE_PATH = PROJECT_ROOT / "database" / "trading.db"
    
    # Data source
    DATA_SOURCE = os.getenv('BOT_DATA_SOURCE', 'vnstock')  # 'vnstock' or 'ssi'
    
    # Symbols to track
    VN30_SYMBOLS = [
        'VNM', 'VCB', 'HPG', 'VIC', 'VHM', 'MSN', 'MWG', 'FPT',
        'VPB', 'GAS', 'TCB', 'BID', 'CTG', 'VRE', 'PLX', 'SAB',
        'MBB', 'VJC', 'POW', 'SSI', 'HDB', 'TPB', 'PDR', 'GVR',
        'VNM', 'NVL', 'STB', 'BCM', 'KDH', 'HNG'
    ]
    
    SYMBOLS = os.getenv('BOT_SYMBOLS', ','.join(VN30_SYMBOLS[:10])).split(',')  # Default: Top 10
    
    # Timeframes
    TIMEFRAMES = ['1D']  # Can add '4H' for intraday
    
    # Trading parameters
    TOTAL_CAPITAL = float(os.getenv('BOT_CAPITAL', 100_000_000))  # 100M VND
    MAX_OPEN_POSITIONS = int(os.getenv('BOT_MAX_POSITIONS', 5))
    MIN_CONFIDENCE_SCORE = float(os.getenv('BOT_MIN_CONFIDENCE', 60.0))
    
    # Schedule
    RUN_TIME = os.getenv('BOT_RUN_TIME', '15:30')  # After market close
    RUN_INTERVAL_MINUTES = int(os.getenv('BOT_INTERVAL', 60))  # For real-time mode
    
    # Notification
    TELEGRAM_ENABLED = os.getenv('BOT_TELEGRAM_ENABLED', 'false').lower() == 'true'
    TELEGRAM_TOKEN = os.getenv('BOT_TELEGRAM_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('BOT_TELEGRAM_CHAT_ID', '')
    
    ZALO_ENABLED = os.getenv('BOT_ZALO_ENABLED', 'false').lower() == 'true'
    ZALO_TOKEN = os.getenv('BOT_ZALO_TOKEN', '')
    ZALO_CHAT_ID = os.getenv('BOT_ZALO_CHAT_ID', '')
    
    EMAIL_ENABLED = os.getenv('BOT_EMAIL_ENABLED', 'false').lower() == 'true'
    EMAIL_FROM = os.getenv('BOT_EMAIL_FROM', '')
    EMAIL_TO = os.getenv('BOT_EMAIL_TO', '')
    EMAIL_PASSWORD = os.getenv('BOT_EMAIL_PASSWORD', '')
    
    # Auto-trading (DANGEROUS - use with caution)
    AUTO_TRADING_ENABLED = os.getenv('BOT_AUTO_TRADING', 'false').lower() == 'true'
    BROKER_API_KEY = os.getenv('BOT_BROKER_API_KEY', '')
    
    # Logging
    LOG_LEVEL = os.getenv('BOT_LOG_LEVEL', 'INFO')
    LOG_FILE = PROJECT_ROOT / "logs" / "bot.log"
    
    # Strategy configuration
    STRATEGY_NAME = 'Pro Trader - Trend Following'
    
    # Risk management defaults
    STOP_LOSS_PCT = float(os.getenv('BOT_STOP_LOSS_PCT', 5.0))
    TAKE_PROFIT_PCT = float(os.getenv('BOT_TAKE_PROFIT_PCT', 10.0))
    MIN_RISK_REWARD = float(os.getenv('BOT_MIN_RR', 1.5))
    
    # Performance learning (Week 3)
    ENABLE_LEARNING = os.getenv('BOT_ENABLE_LEARNING', 'true').lower() == 'true'
    MIN_TRADES_FOR_FILTER = int(os.getenv('BOT_MIN_TRADES_FOR_FILTER', 5))
    MIN_WIN_RATE = float(os.getenv('BOT_MIN_WIN_RATE', 40.0))
    COOLDOWN_DAYS = int(os.getenv('BOT_COOLDOWN_DAYS', 7))
    
    # Portfolio tracking (Option 3)
    ENABLE_PORTFOLIO_TRACKING = os.getenv('BOT_ENABLE_PORTFOLIO_TRACKING', 'true').lower() == 'true'
    PORTFOLIO_PATH = os.getenv('BOT_PORTFOLIO_PATH', 'portfolio.json')
    PORTFOLIO_ALERT_THRESHOLD = float(os.getenv('BOT_PORTFOLIO_ALERT_THRESHOLD', 5.0))
    PORTFOLIO_UPDATE_INTERVAL = int(os.getenv('BOT_PORTFOLIO_UPDATE_INTERVAL', 60))  # minutes
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        errors = []
        
        # Check database path
        if not cls.DATABASE_PATH.parent.exists():
            errors.append(f"Database directory not found: {cls.DATABASE_PATH.parent}")
        
        # Check symbols
        if not cls.SYMBOLS:
            errors.append("No symbols configured")
        
        # Check Telegram config if enabled
        if cls.TELEGRAM_ENABLED:
            if not cls.TELEGRAM_TOKEN:
                errors.append("Telegram enabled but no token provided")
            if not cls.TELEGRAM_CHAT_ID:
                errors.append("Telegram enabled but no chat ID provided")
        
        # Check Zalo config if enabled
        if cls.ZALO_ENABLED:
            if not cls.ZALO_TOKEN:
                errors.append("Zalo enabled but no token provided")
            if not cls.ZALO_CHAT_ID:
                errors.append("Zalo enabled but no chat ID provided")
        
        # Check email config if enabled
        if cls.EMAIL_ENABLED:
            if not cls.EMAIL_FROM or not cls.EMAIL_TO:
                errors.append("Email enabled but credentials missing")
        
        # Check auto-trading config if enabled
        if cls.AUTO_TRADING_ENABLED:
            if not cls.BROKER_API_KEY:
                errors.append("Auto-trading enabled but no broker API key")
        
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("\n" + "="*70)
        print("BOT CONFIGURATION")
        print("="*70)
        
        print(f"\n📊 DATA:")
        print(f"  Source: {cls.DATA_SOURCE}")
        print(f"  Symbols: {', '.join(cls.SYMBOLS[:5])}{'...' if len(cls.SYMBOLS) > 5 else ''}")
        print(f"  Timeframes: {', '.join(cls.TIMEFRAMES)}")
        
        print(f"\n💰 TRADING:")
        print(f"  Total Capital: {cls.TOTAL_CAPITAL:,.0f} VND")
        print(f"  Max Open Positions: {cls.MAX_OPEN_POSITIONS}")
        print(f"  Min Confidence: {cls.MIN_CONFIDENCE_SCORE}%")
        
        print(f"\n🛡️ RISK MANAGEMENT:")
        print(f"  Stop-Loss: {cls.STOP_LOSS_PCT}%")
        print(f"  Take-Profit: {cls.TAKE_PROFIT_PCT}%")
        print(f"  Min R/R: {cls.MIN_RISK_REWARD}")
        
        print(f"\n🧠 PERFORMANCE LEARNING:")
        print(f"  Enabled: {'✅ Yes' if cls.ENABLE_LEARNING else '❌ No'}")
        if cls.ENABLE_LEARNING:
            print(f"  Min Trades for Filter: {cls.MIN_TRADES_FOR_FILTER}")
            print(f"  Min Win Rate: {cls.MIN_WIN_RATE}%")
            print(f"  Cooldown Days: {cls.COOLDOWN_DAYS}")
        
        print(f"\n📊 PORTFOLIO TRACKING:")
        print(f"  Enabled: {'✅ Yes' if cls.ENABLE_PORTFOLIO_TRACKING else '❌ No'}")
        if cls.ENABLE_PORTFOLIO_TRACKING:
            print(f"  Portfolio File: {cls.PORTFOLIO_PATH}")
            print(f"  Alert Threshold: {cls.PORTFOLIO_ALERT_THRESHOLD}%")
            print(f"  Update Interval: {cls.PORTFOLIO_UPDATE_INTERVAL} minutes")
        
        print(f"\n⏰ SCHEDULE:")
        print(f"  Run Time: {cls.RUN_TIME}")
        print(f"  Interval: {cls.RUN_INTERVAL_MINUTES} minutes")
        
        print(f"\n🔔 NOTIFICATIONS:")
        print(f"  Telegram: {'✅ Enabled' if cls.TELEGRAM_ENABLED else '❌ Disabled'}")
        print(f"  Zalo: {'✅ Enabled' if cls.ZALO_ENABLED else '❌ Disabled'}")
        print(f"  Email: {'✅ Enabled' if cls.EMAIL_ENABLED else '❌ Disabled'}")
        
        print(f"\n🤖 AUTO-TRADING:")
        print(f"  Status: {'⚠️ ENABLED (DANGEROUS)' if cls.AUTO_TRADING_ENABLED else '✅ Disabled (Safe)'}")
        
        print(f"\n📁 PATHS:")
        print(f"  Database: {cls.DATABASE_PATH}")
        print(f"  Logs: {cls.LOG_FILE}")
        
        print("\n" + "="*70)
    
    @classmethod
    def create_env_template(cls, filepath: str = '.env.example'):
        """Create .env template file"""
        template = """# Trading Bot Configuration

# Data Source
BOT_DATA_SOURCE=vnstock  # 'vnstock' or 'ssi'

# Symbols (comma-separated)
BOT_SYMBOLS=VNM,VCB,HPG,VIC,VHM,MSN,MWG,FPT,VPB,GAS

# Trading Parameters
BOT_CAPITAL=100000000  # 100M VND
BOT_MAX_POSITIONS=5
BOT_MIN_CONFIDENCE=60.0

# Schedule
BOT_RUN_TIME=15:30  # After market close
BOT_INTERVAL=60  # Minutes (for real-time mode)

# Risk Management
BOT_STOP_LOSS_PCT=5.0
BOT_TAKE_PROFIT_PCT=10.0
BOT_MIN_RR=1.5

# Performance Learning (Week 3)
BOT_ENABLE_LEARNING=true
BOT_MIN_TRADES_FOR_FILTER=5
BOT_MIN_WIN_RATE=40.0
BOT_COOLDOWN_DAYS=7

# Portfolio Tracking (Option 3)
BOT_ENABLE_PORTFOLIO_TRACKING=true
BOT_PORTFOLIO_PATH=portfolio.json
BOT_PORTFOLIO_ALERT_THRESHOLD=5.0
BOT_PORTFOLIO_UPDATE_INTERVAL=60

# Telegram Notification
BOT_TELEGRAM_ENABLED=false
BOT_TELEGRAM_TOKEN=your_telegram_bot_token_here
BOT_TELEGRAM_CHAT_ID=your_chat_id_here

# Zalo Notification
BOT_ZALO_ENABLED=false
BOT_ZALO_TOKEN=your_zalo_bot_token_here
BOT_ZALO_CHAT_ID=your_zalo_chat_id_here

# Email Notification
BOT_EMAIL_ENABLED=false
BOT_EMAIL_FROM=your_email@gmail.com
BOT_EMAIL_TO=recipient@gmail.com
BOT_EMAIL_PASSWORD=your_app_password

# Auto-Trading (DANGEROUS - use with caution)
BOT_AUTO_TRADING=false
BOT_BROKER_API_KEY=your_broker_api_key

# Logging
BOT_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
"""
        
        with open(filepath, 'w') as f:
            f.write(template)
        
        print(f"✅ Created .env template: {filepath}")
        print("   Edit this file and rename to .env")


if __name__ == "__main__":
    # Test configuration
    BotConfig.print_config()
    
    # Validate
    if BotConfig.validate():
        print("\n✅ Configuration is valid!")
    else:
        print("\n❌ Configuration has errors!")
    
    # Create .env template
    print("\n" + "="*70)
    BotConfig.create_env_template()
