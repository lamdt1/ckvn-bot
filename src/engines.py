import pandas as pd
import numpy as np
from typing import Tuple, Optional
from .config import settings

class AnalysisEngine:
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> float:
        """Tính toán chỉ số RSI từ dữ liệu lịch sử."""
        if df.empty or len(df) < period:
            return 50.0  # Giá trị mặc định trung tính
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    @staticmethod
    def calculate_ma(df: pd.DataFrame, period: int = 20) -> float:
        """Tính toán giá trị Moving Average."""
        if df.empty or len(df) < period:
            return 0.0
        return df['close'].rolling(window=period).mean().iloc[-1]

    @staticmethod
    def analyze_signal(
        symbol: str, 
        current_price: float, 
        avg_price: float, 
        history_df: pd.DataFrame
    ) -> Tuple[Optional[str], float, float, float]:
        """
        Phân tích và đưa ra tín hiệu: Mua, Bán, Cắt lỗ hoặc None.
        Trả về: (Tín hiệu, RSI, MA20, PnL)
        """
        rsi = AnalysisEngine.calculate_rsi(history_df, settings.RSI_PERIOD)
        ma20 = AnalysisEngine.calculate_ma(history_df, settings.MA_PERIOD)
        
        # Tính toán Lãi/Lỗ (%)
        pnl = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
        
        signal = None
        
        # 1. Cắt lỗ (Ưu tiên cao nhất)
        if pnl <= settings.LOSS_THRESHOLD:
            signal = "CUT_LOSS"
        
        # 2. Chốt lời: Lãi >= ngưỡng + RSI > 70
        elif pnl >= settings.PROFIT_THRESHOLD and rsi > 70:
            signal = "TAKE_PROFIT"
            
        # 3. Mua: RSI < 30 hoặc Giá vượt MA20
        elif rsi < 30 or current_price > ma20:
            # Lưu ý: Cần thêm logic tránh spam mua nếu đã có vị thế, 
            # nhưng ở đây ta trả về tín hiệu thuần túy theo SRS.
            signal = "BUY"
            
        return signal, rsi, ma20, pnl
