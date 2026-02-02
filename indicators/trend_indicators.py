"""
Trend Indicators Calculator
Implements MA, EMA, and trend detection for Pro Trader strategy
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class TrendIndicators:
    """Calculate trend-based indicators"""
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average
        
        Args:
            data: Price series
            period: MA period
            
        Returns:
            SMA series
        """
        return data.rolling(window=period, min_periods=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            data: Price series
            period: EMA period
            
        Returns:
            EMA series
        """
        return data.ewm(span=period, adjust=False, min_periods=period).mean()
    
    @staticmethod
    def detect_trend_direction(price: float, ma_200: float, ema_20: float) -> str:
        """
        Detect trend direction based on price position relative to MAs
        
        Args:
            price: Current price
            ma_200: MA 200 value
            ema_20: EMA 20 value
            
        Returns:
            'UP', 'DOWN', or 'SIDEWAYS'
        """
        if pd.isna(ma_200) or pd.isna(ema_20):
            return 'SIDEWAYS'
        
        # Strong uptrend: Price above both MAs
        if price > ma_200 and price > ema_20:
            return 'UP'
        # Strong downtrend: Price below both MAs
        elif price < ma_200 and price < ema_20:
            return 'DOWN'
        # Mixed signals
        else:
            return 'SIDEWAYS'
    
    @staticmethod
    def calculate_trend_strength(price: float, ma_200: float) -> float:
        """
        Calculate trend strength (0-100)
        
        Args:
            price: Current price
            ma_200: MA 200 value
            
        Returns:
            Trend strength score (0-100)
        """
        if pd.isna(ma_200) or ma_200 == 0:
            return 50.0
        
        # Calculate percentage distance from MA 200
        distance_pct = abs((price - ma_200) / ma_200) * 100
        
        # Convert to 0-100 scale (cap at 20% distance = 100 strength)
        strength = min(distance_pct * 5, 100)
        
        return round(strength, 2)
    
    @staticmethod
    def calculate_support_resistance(df: pd.DataFrame, lookback: int = 20) -> Dict[str, float]:
        """
        Calculate dynamic support and resistance levels
        
        Args:
            df: DataFrame with OHLC data
            lookback: Number of periods to look back
            
        Returns:
            Dictionary with support and resistance levels
        """
        if len(df) < lookback:
            return {
                'support_level': None,
                'resistance_level': None,
                'distance_to_support_pct': None,
                'distance_to_resistance_pct': None
            }
        
        recent_data = df.tail(lookback)
        
        # Support: Recent low
        support = recent_data['low'].min()
        
        # Resistance: Recent high
        resistance = recent_data['high'].max()
        
        current_price = df['close'].iloc[-1]
        
        # Calculate distances
        distance_to_support = ((current_price - support) / support * 100) if support > 0 else 0
        distance_to_resistance = ((resistance - current_price) / current_price * 100) if current_price > 0 else 0
        
        return {
            'support_level': round(support, 2),
            'resistance_level': round(resistance, 2),
            'distance_to_support_pct': round(distance_to_support, 2),
            'distance_to_resistance_pct': round(distance_to_resistance, 2)
        }
    
    @classmethod
    def calculate_all(cls, df: pd.DataFrame, 
                     ma_period: int = 200, 
                     ema_period: int = 20) -> Dict[str, any]:
        """
        Calculate all trend indicators
        
        Args:
            df: DataFrame with OHLC data (must have 'close' column)
            ma_period: MA period (default: 200)
            ema_period: EMA period (default: 20)
            
        Returns:
            Dictionary with all trend indicators
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame must have 'close' column")
        
        # Calculate MAs
        df['MA_200'] = cls.calculate_sma(df['close'], ma_period)
        df['EMA_20'] = cls.calculate_ema(df['close'], ema_period)
        
        # Get latest values
        latest = df.iloc[-1]
        current_price = latest['close']
        ma_200 = latest['MA_200']
        ema_20 = latest['EMA_20']
        
        # Detect trend
        trend_direction = cls.detect_trend_direction(current_price, ma_200, ema_20)
        trend_strength = cls.calculate_trend_strength(current_price, ma_200)
        
        # Support/Resistance
        support_resistance = cls.calculate_support_resistance(df)
        
        return {
            'ma_200': round(ma_200, 2) if not pd.isna(ma_200) else None,
            'ema_20': round(ema_20, 2) if not pd.isna(ema_20) else None,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            **support_resistance
        }


if __name__ == "__main__":
    # Test with sample data
    import random
    from datetime import datetime, timedelta
    
    # Generate sample OHLC data
    dates = pd.date_range(end=datetime.now(), periods=250, freq='D')
    base_price = 85000
    
    data = []
    for i in range(250):
        change = random.uniform(-0.02, 0.02)
        close = base_price * (1 + change)
        data.append({
            'timestamp': int(dates[i].timestamp()),
            'open': base_price,
            'high': max(base_price, close) * 1.01,
            'low': min(base_price, close) * 0.99,
            'close': close,
            'volume': random.randint(1000000, 5000000)
        })
        base_price = close
    
    df = pd.DataFrame(data)
    
    # Calculate indicators
    indicators = TrendIndicators.calculate_all(df)
    
    print("Trend Indicators Test:")
    print(f"  MA 200: {indicators['ma_200']:,.0f}")
    print(f"  EMA 20: {indicators['ema_20']:,.0f}")
    print(f"  Trend Direction: {indicators['trend_direction']}")
    print(f"  Trend Strength: {indicators['trend_strength']}")
    print(f"  Support: {indicators['support_level']:,.0f}")
    print(f"  Resistance: {indicators['resistance_level']:,.0f}")
    print(f"  Distance to Support: {indicators['distance_to_support_pct']}%")
    print(f"  Distance to Resistance: {indicators['distance_to_resistance_pct']}%")
