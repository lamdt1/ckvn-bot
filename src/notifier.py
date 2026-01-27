import httpx
from abc import ABC, abstractmethod
from typing import List
from .config import settings

class BaseNotifier(ABC):
    @abstractmethod
    def send_message(self, text: str) -> bool:
        pass

    @abstractmethod
    def format_alert_message(self, symbol: str, signal: str, price: float, pnl: float, rsi: float, ma20: float) -> str:
        pass

class TelegramNotifier(BaseNotifier):
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, text: str) -> bool:
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            response = httpx.post(self.api_url, json=payload, timeout=10.0)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Telegram Error: {e}")
            return False

    def format_alert_message(self, symbol: str, signal: str, price: float, pnl: float, rsi: float, ma20: float) -> str:
        emoji, signal_text = self._get_signal_info(signal)
        return (
            f"{emoji} {signal_text}: #{symbol}\n"
            f"───────────────────\n"
            f"💰 Giá hiện tại: `{price:,.0f}` VNĐ\n"
            f"📈 Lãi/Lỗ: `{pnl:+.2f}%`\n"
            f"📊 RSI(14): `{rsi:.2f}`\n"
            f"📉 MA20: `{ma20:,.0f}`\n"
            f"───────────────────"
        )

    def _get_signal_info(self, signal: str):
        if signal == "BUY": return "🟢", "*KHUYẾN NGHỊ MUA*"
        if signal == "TAKE_PROFIT": return "🔵", "*CHỐT LỜI*"
        if signal == "CUT_LOSS": return "🔴", "*CẮT LỖ KHẨN CẤP*"
        return "⚪", "THEO DÕI"

class ZaloNotifier(BaseNotifier):
    def __init__(self):
        self.token = settings.ZALO_BOT_TOKEN
        self.chat_id = settings.ZALO_CHAT_ID
        # URL format: https://bot-api.zaloplatforms.com/bot<BOT_TOKEN>/<functionName>
        self.api_url = f"https://bot-api.zaloplatforms.com/bot{self.token}/sendMessage"

    def send_message(self, text: str) -> bool:
        if not self.token or not self.chat_id:
            print("Zalo Config Missing!")
            return False
            
        payload = {
            "chat_id": self.chat_id,
            "text": text
        }
        try:
            response = httpx.post(self.api_url, json=payload, timeout=10.0)
            data = response.json()
            if not data.get("ok"):
                print(f"Zalo API Error: {data.get('description')}")
                return False
            return True
        except Exception as e:
            print(f"Zalo Network Error: {e}")
            return False

    def format_alert_message(self, symbol: str, signal: str, price: float, pnl: float, rsi: float, ma20: float) -> str:
        # Zalo có thể không hỗ trợ Markdown như Telegram, dùng text thuần
        emoji, signal_text = self._get_signal_info(signal)
        return (
            f"{emoji} {signal_text}: {symbol}\n"
            f"-------------------\n"
            f"Giá hiện tại: {price:,.0f} VND\n"
            f"Lãi/Lỗ: {pnl:+.2f}%\n"
            f"RSI(14): {rsi:.2f}\n"
            f"MA20: {ma20:,.0f}\n"
            f"-------------------"
        )

    def _get_signal_info(self, signal: str):
        if signal == "BUY": return "🟢", "KHUYẾN NGHỊ MUA"
        if signal == "TAKE_PROFIT": return "🔵", "CHỐT LỜI"
        if signal == "CUT_LOSS": return "🔴", "CẮT LỖ KHẨN CẤP"
        return "⚪", "THEO DÕI"

class MultiNotifier(BaseNotifier):
    def __init__(self, managed_notifiers: List[BaseNotifier]):
        self.notifiers = managed_notifiers

    def send_message(self, text: str) -> bool:
        results = [n.send_message(text) for n in self.notifiers]
        return any(results)

    def format_alert_message(self, symbol: str, signal: str, price: float, pnl: float, rsi: float, ma20: float) -> str:
        # Trả về format của notifier đầu tiên, hoặc một format chung nhất
        return self.notifiers[0].format_alert_message(symbol, signal, price, pnl, rsi, ma20)

def get_notifier() -> BaseNotifier:
    provider = settings.NOTIFICATION_PROVIDER.lower()
    
    if provider == "zalo":
        return ZaloNotifier()
    elif provider == "both":
        return MultiNotifier([TelegramNotifier(), ZaloNotifier()])
    else:
        return TelegramNotifier()
