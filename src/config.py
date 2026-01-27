from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Notification Selection
    # Options: "telegram", "zalo", "both"
    NOTIFICATION_PROVIDER: str = "telegram"

    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # Zalo Configuration (from zalo-bot-doc.md)
    ZALO_BOT_TOKEN: Optional[str] = None
    ZALO_CHAT_ID: Optional[str] = None
    
    # Trading Strategy Thresholds
    PROFIT_THRESHOLD: float = 15.0  # Percentage
    LOSS_THRESHOLD: float = -7.0    # Percentage
    
    # Technical Indicators Parameters
    RSI_PERIOD: int = 14
    MA_PERIOD: int = 20
    
    # Operational Constants
    CHECK_INTERVAL_SECONDS: int = 900  # 15 minutes
    PORT: int = 6886  # Port for health check or status page
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Singleton instance
settings = Settings()
