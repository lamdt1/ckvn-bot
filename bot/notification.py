"""
Notification Manager
Send alerts via Telegram and Zalo
"""

import logging
import httpx
from typing import List, Optional
from datetime import datetime

from strategies.signal import Signal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZaloNotifier:
    """
    Zalo notification manager
    
    Sends trading alerts to Zalo for manual review
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Zalo notifier
        
        Args:
            bot_token: Zalo bot token
            chat_id: Zalo chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://bot-api.zaloplatforms.com/bot{bot_token}"
        
        logger.info("✅ Zalo bot initialized")
    
    def _send_message(self, text: str) -> bool:
        """Send message to Zalo"""
        try:
            url = f"{self.base_url}/sendMessage"
            response = httpx.post(
                url,
                json={
                    "chat_id": self.chat_id,
                    "text": text
                },
                timeout=10.0
            )
            
            data = response.json()
            if data.get("ok"):
                return True
            else:
                logger.error(f"Zalo API error: {data.get('description')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Zalo message: {e}")
            return False
    
    def send_signal_alert(self, signal: Signal) -> bool:
        """
        Send signal alert to Zalo
        
        Args:
            signal: Trading signal
            
        Returns:
            True if sent successfully
        """
        try:
            message = self._format_signal_message(signal)
            success = self._send_message(message)
            
            if success:
                logger.info(f"✅ Sent Zalo alert for {signal.symbol}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send Zalo alert: {e}")
            return False
    
    def send_batch_alerts(self, signals: List[Signal]) -> int:
        """
        Send multiple signal alerts
        
        Args:
            signals: List of signals
            
        Returns:
            Number of successfully sent alerts
        """
        if not signals:
            return 0
        
        sent_count = 0
        
        # Send summary first
        summary = self._format_summary_message(signals)
        if self._send_message(summary):
            sent_count += 1
        
        # Send individual signals
        for signal in signals:
            if self.send_signal_alert(signal):
                sent_count += 1
        
        return sent_count
    
    def send_position_alert(self, symbol: str, action: str, price: float,
                           profit_loss_pct: float, reason: str) -> bool:
        """
        Send position close alert
        
        Args:
            symbol: Stock symbol
            action: 'STOP_LOSS' or 'TAKE_PROFIT'
            price: Close price
            profit_loss_pct: Profit/loss percentage
            reason: Close reason
            
        Returns:
            True if sent successfully
        """
        try:
            emoji = "🔴" if action == "STOP_LOSS" else "🟢"
            pnl_emoji = "📉" if profit_loss_pct < 0 else "📈"
            
            message = f"""
{emoji} VỊ THẾ ĐÓNG

Mã: {symbol}
Hành động: {action}
Giá: {price:,.0f} VND
{pnl_emoji} P&L: {profit_loss_pct:+.2f}%
Lý do: {reason}

Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            return self._send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send Zalo position alert: {e}")
            return False
    
    def send_daily_summary(self, stats: dict) -> bool:
        """
        Send daily summary report
        
        Args:
            stats: Dictionary with daily statistics
            
        Returns:
            True if sent successfully
        """
        try:
            message = f"""
📊 BÁO CÁO CUỐI NGÀY

Ngày: {datetime.now().strftime('%Y-%m-%d')}

📈 Tín hiệu tạo ra: {stats.get('signals_generated', 0)}
   • MUA MẠNH: {stats.get('strong_buy', 0)}
   • MUA YẾU: {stats.get('weak_buy', 0)}
   • THEO DÕI: {stats.get('watch', 0)}

💼 Vị thế mở: {stats.get('open_positions', 0)}
💰 Tổng P&L: {stats.get('total_pnl_pct', 0):+.2f}%

✅ Đóng hôm nay: {stats.get('closed_today', 0)}
   • Thắng: {stats.get('wins_today', 0)}
   • Thua: {stats.get('losses_today', 0)}

Tạo bởi Pro Trader Bot
"""
            
            return self._send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send Zalo daily summary: {e}")
            return False
    
    def _format_signal_message(self, signal: Signal) -> str:
        """Format signal as Zalo message"""
        # Emoji based on signal type
        emoji_map = {
            'STRONG_BUY': '🟢🟢',
            'WEAK_BUY': '🟢',
            'WATCH': '👀',
            'NO_ACTION': '⏸️'
        }
        
        emoji = emoji_map.get(signal.signal_type.value, '❓')
        
        # Format message (Zalo doesn't support HTML, use plain text)
        message = f"""
{emoji} {signal.signal_type.value}

Mã: {signal.symbol}
Giá: {signal.price:,.0f} VND
Độ tin cậy: {signal.confidence_score:.1f}%

🛡️ Quản lý rủi ro:
• Cắt lỗ: {signal.stop_loss:,.0f} VND ({signal.get_potential_loss_pct():.2f}%)
• Chốt lời: {signal.take_profit:,.0f} VND (+{signal.get_potential_profit_pct():.2f}%)
• R/R: {signal.risk_reward_ratio:.2f}
• Tỷ lệ vị thế: {signal.position_size_pct:.1f}%

📊 Phân tích:
• Xu hướng: {signal.reasoning.get('trend_reason', 'N/A')}
• Động lượng: {signal.reasoning.get('momentum_reason', 'N/A')}
• Khối lượng: {signal.reasoning.get('volume_reason', 'N/A')}
• Điểm vào: {signal.reasoning.get('entry_reason', 'N/A')}

⚠️ Cần xem xét thủ công trước khi giao dịch
Thời gian: {datetime.fromtimestamp(signal.timestamp).strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return message
    
    def _format_summary_message(self, signals: List[Signal]) -> str:
        """Format summary of multiple signals"""
        # Count by type
        by_type = {}
        for signal in signals:
            signal_type = signal.signal_type.value
            if signal_type not in by_type:
                by_type[signal_type] = []
            by_type[signal_type].append(signal)
        
        # Format message
        message = f"""
📊 TỔNG KẾT TÍN HIỆU

Tổng số: {len(signals)}

"""
        
        for signal_type, sigs in by_type.items():
            emoji = {'STRONG_BUY': '🟢🟢', 'WEAK_BUY': '🟢', 'WATCH': '👀'}.get(signal_type, '❓')
            message += f"{emoji} {signal_type}: {len(sigs)}\n"
            
            # List symbols
            symbols = [s.symbol for s in sorted(sigs, key=lambda x: x.confidence_score, reverse=True)]
            message += f"   {', '.join(symbols[:5])}"
            if len(symbols) > 5:
                message += f" +{len(symbols)-5} khác"
            message += "\n\n"
        
        message += f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message


class TelegramNotifier:
    """
    Telegram notification manager
    
    Sends trading alerts to Telegram for manual review
    """
    
    def __init__(self, token: str, chat_id: str):
        """
        Initialize Telegram notifier
        
        Args:
            token: Telegram bot token
            chat_id: Telegram chat ID
        """
        self.token = token
        self.chat_id = chat_id
        self.bot = None
        
        self._initialize_bot()
    
    def _initialize_bot(self):
        """Initialize Telegram bot"""
        try:
            from telegram import Bot
            self.bot = Bot(token=self.token)
            logger.info("✅ Telegram bot initialized")
        except ImportError:
            logger.error("python-telegram-bot not installed. Install with: pip install python-telegram-bot")
            self.bot = None
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            self.bot = None
    
    def send_signal_alert(self, signal: Signal) -> bool:
        """
        Send signal alert to Telegram
        
        Args:
            signal: Trading signal
            
        Returns:
            True if sent successfully
        """
        if not self.bot:
            logger.warning("Telegram bot not initialized, skipping notification")
            return False
        
        try:
            message = self._format_signal_message(signal)
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"✅ Sent Telegram alert for {signal.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_batch_alerts(self, signals: List[Signal]) -> int:
        """
        Send multiple signal alerts
        
        Args:
            signals: List of signals
            
        Returns:
            Number of successfully sent alerts
        """
        if not signals:
            return 0
        
        sent_count = 0
        
        # Send summary first
        summary = self._format_summary_message(signals)
        if self._send_message(summary):
            sent_count += 1
        
        # Send individual signals
        for signal in signals:
            if self.send_signal_alert(signal):
                sent_count += 1
        
        return sent_count
    
    def send_position_alert(self, symbol: str, action: str, price: float, 
                           profit_loss_pct: float, reason: str) -> bool:
        """
        Send position close alert
        
        Args:
            symbol: Stock symbol
            action: 'STOP_LOSS' or 'TAKE_PROFIT'
            price: Close price
            profit_loss_pct: Profit/loss percentage
            reason: Close reason
            
        Returns:
            True if sent successfully
        """
        if not self.bot:
            return False
        
        try:
            emoji = "🔴" if action == "STOP_LOSS" else "🟢"
            pnl_emoji = "📉" if profit_loss_pct < 0 else "📈"
            
            message = f"""
{emoji} <b>POSITION CLOSED</b>

<b>Symbol:</b> {symbol}
<b>Action:</b> {action}
<b>Price:</b> {price:,.0f} VND
{pnl_emoji} <b>P&L:</b> {profit_loss_pct:+.2f}%
<b>Reason:</b> {reason}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
            
            return self._send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send position alert: {e}")
            return False
    
    def send_daily_summary(self, stats: dict) -> bool:
        """
        Send daily summary report
        
        Args:
            stats: Dictionary with daily statistics
            
        Returns:
            True if sent successfully
        """
        if not self.bot:
            return False
        
        try:
            message = f"""
📊 <b>DAILY SUMMARY</b>

<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}

📈 <b>Signals Generated:</b> {stats.get('signals_generated', 0)}
   • STRONG_BUY: {stats.get('strong_buy', 0)}
   • WEAK_BUY: {stats.get('weak_buy', 0)}
   • WATCH: {stats.get('watch', 0)}

💼 <b>Open Positions:</b> {stats.get('open_positions', 0)}
💰 <b>Total P&L:</b> {stats.get('total_pnl_pct', 0):+.2f}%

✅ <b>Closed Today:</b> {stats.get('closed_today', 0)}
   • Wins: {stats.get('wins_today', 0)}
   • Losses: {stats.get('losses_today', 0)}

<i>Generated by Pro Trader Bot</i>
"""
            
            return self._send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {e}")
            return False
    
    def _send_message(self, message: str) -> bool:
        """Send message to Telegram"""
        try:
            # Use direct HTTP request instead of async bot wrapper
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            response = httpx.post(
                url,
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Telegram API error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def _format_signal_message(self, signal: Signal) -> str:
        """Format signal as Telegram message"""
        # Emoji based on signal type
        emoji_map = {
            'STRONG_BUY': '🟢🟢',
            'WEAK_BUY': '🟢',
            'WATCH': '👀',
            'NO_ACTION': '⏸️'
        }
        
        emoji = emoji_map.get(signal.signal_type.value, '❓')
        
        # Format message
        message = f"""
{emoji} <b>{signal.signal_type.value}</b>

<b>Symbol:</b> {signal.symbol}
<b>Price:</b> {signal.price:,.0f} VND
<b>Confidence:</b> {signal.confidence_score:.1f}%

🛡️ <b>Risk Management:</b>
• Stop-Loss: {signal.stop_loss:,.0f} VND ({signal.get_potential_loss_pct():.2f}%)
• Take-Profit: {signal.take_profit:,.0f} VND (+{signal.get_potential_profit_pct():.2f}%)
• R/R Ratio: {signal.risk_reward_ratio:.2f}
• Position Size: {signal.position_size_pct:.1f}%

📊 <b>Analysis:</b>
• Trend: {signal.reasoning.get('trend_reason', 'N/A')}
• Momentum: {signal.reasoning.get('momentum_reason', 'N/A')}
• Volume: {signal.reasoning.get('volume_reason', 'N/A')}
• Entry: {signal.reasoning.get('entry_reason', 'N/A')}

<i>⚠️ Manual review required before trading</i>
<i>Time: {datetime.fromtimestamp(signal.timestamp).strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return message
    
    def _format_summary_message(self, signals: List[Signal]) -> str:
        """Format summary of multiple signals"""
        # Count by type
        by_type = {}
        for signal in signals:
            signal_type = signal.signal_type.value
            if signal_type not in by_type:
                by_type[signal_type] = []
            by_type[signal_type].append(signal)
        
        # Format message
        message = f"""
📊 <b>SIGNAL SUMMARY</b>

<b>Total Signals:</b> {len(signals)}

"""
        
        for signal_type, sigs in by_type.items():
            emoji = {'STRONG_BUY': '🟢🟢', 'WEAK_BUY': '🟢', 'WATCH': '👀'}.get(signal_type, '❓')
            message += f"{emoji} <b>{signal_type}:</b> {len(sigs)}\n"
            
            # List symbols
            symbols = [s.symbol for s in sorted(sigs, key=lambda x: x.confidence_score, reverse=True)]
            message += f"   {', '.join(symbols[:5])}"
            if len(symbols) > 5:
                message += f" +{len(symbols)-5} more"
            message += "\n\n"
        
        message += f"<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return message


class NotificationManager:
    """
    Main notification manager
    
    Supports multiple channels (Telegram, Zalo, Email, etc.)
    """
    
    def __init__(self,
                 telegram_token: Optional[str] = None,
                 telegram_chat_id: Optional[str] = None,
                 zalo_token: Optional[str] = None,
                 zalo_chat_id: Optional[str] = None,
                 email_config: Optional[dict] = None):
        """
        Initialize notification manager
        
        Args:
            telegram_token: Telegram bot token
            telegram_chat_id: Telegram chat ID
            zalo_token: Zalo bot token
            zalo_chat_id: Zalo chat ID
            email_config: Email configuration (optional)
        """
        self.telegram = None
        self.zalo = None
        self.email = None
        
        # Initialize Telegram
        if telegram_token and telegram_chat_id:
            self.telegram = TelegramNotifier(telegram_token, telegram_chat_id)
        else:
            logger.info("⏸️ Telegram not configured")
        
        # Initialize Zalo
        if zalo_token and zalo_chat_id:
            self.zalo = ZaloNotifier(zalo_token, zalo_chat_id)
        else:
            logger.info("⏸️ Zalo not configured")
        
        # Initialize Email (TODO)
        if email_config:
            logger.warning("Email notifications not yet implemented")
    
    def send_signal_alert(self, signal: Signal) -> bool:
        """Send signal alert via all enabled channels"""
        success = False
        
        if self.telegram:
            success = self.telegram.send_signal_alert(signal) or success
        
        if self.zalo:
            success = self.zalo.send_signal_alert(signal) or success
        
        return success
    
    def send_batch_alerts(self, signals: List[Signal]) -> bool:
        """Send batch alerts via all enabled channels"""
        success = False
        
        if self.telegram:
            count = self.telegram.send_batch_alerts(signals)
            success = count > 0 or success
        
        if self.zalo:
            count = self.zalo.send_batch_alerts(signals)
            success = count > 0 or success
        
        return success
    
    def send_position_alert(self, symbol: str, action: str, price: float,
                           profit_loss_pct: float, reason: str) -> bool:
        """Send position alert via all enabled channels"""
        success = False
        
        if self.telegram:
            success = self.telegram.send_position_alert(
                symbol, action, price, profit_loss_pct, reason
            ) or success
        
        if self.zalo:
            success = self.zalo.send_position_alert(
                symbol, action, price, profit_loss_pct, reason
            ) or success
        
        return success
    
    def send_daily_summary(self, stats: dict) -> bool:
        """Send daily summary via all enabled channels"""
        success = False
        
        if self.telegram:
            success = self.telegram.send_daily_summary(stats) or success
        
        if self.zalo:
            success = self.zalo.send_daily_summary(stats) or success
        
        return success

    def send_message(self, message: str) -> bool:
        """Send raw message via all enabled channels"""
        success = False
        
        if self.telegram:
            # Access internal method _send_message
            success = self.telegram._send_message(message) or success
        
        if self.zalo:
            # Access internal method _send_message
            success = self.zalo._send_message(message) or success
        
        return success


if __name__ == "__main__":
    # Test notification
    print("="*70)
    print("NOTIFICATION MANAGER TEST")
    print("="*70)
    
    print("\n⚠️ To test Telegram notifications:")
    print("1. Create bot with @BotFather")
    print("2. Get bot token")
    print("3. Get your chat ID from @userinfobot")
    print("4. Set environment variables:")
    print("   export BOT_TELEGRAM_TOKEN='your_token'")
    print("   export BOT_TELEGRAM_CHAT_ID='your_chat_id'")
    print("\n5. Run: python3 bot/notification.py")
