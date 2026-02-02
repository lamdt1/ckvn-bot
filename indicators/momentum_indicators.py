"""
Momentum Indicators Calculator
Implements RSI and MACD for Pro Trader strategy
"""

import pandas as pd
import numpy as np
from typing import Dict


class MomentumIndicators:
    """Calculate momentum-based indicators"""
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            data: Price series
            period: RSI period (default: 14)
            
        Returns:
            RSI series
        """
        # Calculate price changes
        delta = data.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss using EMA
        avg_gain = gain.ewm(span=period, adjust=False, min_periods=period).mean()
        avg_loss = loss.ewm(span=period, adjust=False, min_periods=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def classify_rsi(rsi_value: float, 
                     oversold_threshold: float = 30, 
                     overbought_threshold: float = 70) -> str:
        """
        Classify RSI signal
        
        Args:
            rsi_value: RSI value
            oversold_threshold: Oversold threshold (default: 30)
            overbought_threshold: Overbought threshold (default: 70)
            
        Returns:
            'OVERSOLD', 'NEUTRAL', or 'OVERBOUGHT'
        """
        if pd.isna(rsi_value):
            return 'NEUTRAL'
        
        if rsi_value < oversold_threshold:
            return 'OVERSOLD'
        elif rsi_value > overbought_threshold:
            return 'OVERBOUGHT'
        else:
            return 'NEUTRAL'
    
    @staticmethod
    def calculate_macd(data: pd.Series, 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: Price series
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line period (default: 9)
            
        Returns:
            Dictionary with MACD line, signal line, and histogram
        """
        # Calculate EMAs
        ema_fast = data.ewm(span=fast_period, adjust=False, min_periods=fast_period).mean()
        ema_slow = data.ewm(span=slow_period, adjust=False, min_periods=slow_period).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = macd_line.ewm(span=signal_period, adjust=False, min_periods=signal_period).mean()
        
        # Histogram
        histogram = macd_line - signal_line
        
        return {
            'macd_line': macd_line,
            'macd_signal': signal_line,
            'macd_histogram': histogram
        }
    
    @staticmethod
    def classify_macd(macd_histogram: float, macd_line: float, signal_line: float) -> str:
        """
        Classify MACD trend
        
        Args:
            macd_histogram: MACD histogram value
            macd_line: MACD line value
            signal_line: Signal line value
            
        Returns:
            'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        if pd.isna(macd_histogram):
            return 'NEUTRAL'
        
        # Bullish: Histogram positive and MACD above signal
        if macd_histogram > 0 and macd_line > signal_line:
            return 'BULLISH'
        # Bearish: Histogram negative and MACD below signal
        elif macd_histogram < 0 and macd_line < signal_line:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    @classmethod
    def calculate_all(cls, df: pd.DataFrame, 
                     rsi_period: int = 14,
                     macd_fast: int = 12,
                     macd_slow: int = 26,
                     macd_signal: int = 9) -> Dict[str, any]:
        """
        Calculate all momentum indicators
        
        Args:
            df: DataFrame with OHLC data (must have 'close' column)
            rsi_period: RSI period (default: 14)
            macd_fast: MACD fast period (default: 12)
            macd_slow: MACD slow period (default: 26)
            macd_signal: MACD signal period (default: 9)
            
        Returns:
            Dictionary with all momentum indicators
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame must have 'close' column")
        
        # Calculate RSI
        df['RSI_14'] = cls.calculate_rsi(df['close'], rsi_period)
        
        # Calculate MACD
        macd_data = cls.calculate_macd(df['close'], macd_fast, macd_slow, macd_signal)
        df['MACD'] = macd_data['macd_line']
        df['MACD_signal'] = macd_data['macd_signal']
        df['MACD_hist'] = macd_data['macd_histogram']
        
        # Get latest values
        latest = df.iloc[-1]
        rsi_value = latest['RSI_14']
        macd_line = latest['MACD']
        macd_signal_line = latest['MACD_signal']
        macd_histogram = latest['MACD_hist']
        
        # Classify signals
        rsi_signal = cls.classify_rsi(rsi_value)
        macd_trend = cls.classify_macd(macd_histogram, macd_line, macd_signal_line)
        
        return {
            'rsi_14': round(rsi_value, 2) if not pd.isna(rsi_value) else None,
            'rsi_signal': rsi_signal,
            'macd_line': round(macd_line, 2) if not pd.isna(macd_line) else None,
            'macd_signal': round(macd_signal_line, 2) if not pd.isna(macd_signal_line) else None,
            'macd_histogram': round(macd_histogram, 2) if not pd.isna(macd_histogram) else None,
            'macd_trend': macd_trend
        }


if __name__ == "__main__":
    # Test with sample data
    import random
    from datetime import datetime, timedelta
    
    # Generate sample price data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    base_price = 85000
    
    data = []
    for i in range(100):
        change = random.uniform(-0.03, 0.03)
        close = base_price * (1 + change)
        data.append({
            'timestamp': int(dates[i].timestamp()),
            'close': close,
            'volume': random.randint(1000000, 5000000)
        })
        base_price = close
    
    df = pd.DataFrame(data)
    
    # Calculate indicators
    indicators = MomentumIndicators.calculate_all(df)
    
    print("Momentum Indicators Test:")
    print(f"  RSI 14: {indicators['rsi_14']}")
    print(f"  RSI Signal: {indicators['rsi_signal']}")
    print(f"  MACD Line: {indicators['macd_line']}")
    print(f"  MACD Signal: {indicators['macd_signal']}")
    print(f"  MACD Histogram: {indicators['macd_histogram']}")
    print(f"  MACD Trend: {indicators['macd_trend']}")
