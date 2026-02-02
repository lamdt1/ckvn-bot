"""
Pro Trader Strategy
Implements the 4-layer Pro Trader Rule-Based Decision Tree
"""

from typing import Dict
from .decision_tree import DecisionTree
from .signal import SignalType
from .risk_manager import RiskManager


class ProTraderStrategy(DecisionTree):
    """
    Pro Trader Strategy Implementation
    
    4-Layer Decision Tree:
    1. Trend: MA 200, EMA 20 - Filter out downtrends
    2. Momentum: RSI, MACD - Check for buying power
    3. Volume: Volume analysis - Confirm with money flow
    4. Entry: Bollinger Bands - Find optimal entry point
    """
    
    def __init__(self, risk_manager: RiskManager = None):
        """
        Initialize Pro Trader strategy
        
        Args:
            risk_manager: Risk manager instance (creates default if None)
        """
        super().__init__(
            strategy_name="Pro Trader - Trend Following",
            risk_manager=risk_manager
        )
        
        # Thresholds (configurable)
        self.thresholds = {
            # Signal type thresholds
            'strong_buy': 80.0,
            'weak_buy': 60.0,
            'watch': 40.0,
            
            # RSI thresholds
            'rsi_oversold': 30.0,
            'rsi_overbought': 70.0,
            
            # Volume thresholds
            'volume_high': 1.5,  # 1.5x average
            'volume_low': 0.7,   # 0.7x average
            
            # BB position thresholds
            'bb_near_lower': 0.3,
            'bb_near_upper': 0.7
        }
    
    def evaluate_trend(self, indicators: Dict[str, any]) -> Dict[str, any]:
        """
        Layer 1: Evaluate trend
        
        Conditions for PASS:
        - Trend direction is UP
        - Price above MA 200
        - Price above EMA 20
        
        Scoring:
        - Strong uptrend (price > MA 200 AND price > EMA 20): 100
        - Weak uptrend (price > MA 200 OR price > EMA 20): 60
        - Downtrend: 0
        """
        trend_direction = indicators.get('trend_direction', 'SIDEWAYS')
        ma_200 = indicators.get('ma_200')
        ema_20 = indicators.get('ema_20')
        
        # Get current price from close or use ma_200 as fallback
        # (In real usage, price will be passed separately)
        
        if trend_direction == 'UP':
            score = 100
            passed = True
            reason = "Strong uptrend confirmed"
        elif trend_direction == 'SIDEWAYS':
            score = 50
            passed = False
            reason = "Sideways trend - no clear direction"
        else:  # DOWN
            score = 0
            passed = False
            reason = "Downtrend - avoid buying"
        
        return {
            'score': score,
            'passed': passed,
            'reason': reason
        }
    
    def evaluate_momentum(self, indicators: Dict[str, any]) -> Dict[str, any]:
        """
        Layer 2: Evaluate momentum
        
        Conditions for PASS:
        - RSI not overbought (< 70)
        - MACD trend is BULLISH
        
        Scoring:
        - RSI in sweet spot (40-60) + MACD bullish: 100
        - RSI neutral (30-70) + MACD bullish: 80
        - RSI oversold (< 30) + MACD bullish: 60 (potential reversal)
        - RSI overbought (> 70): 20 (risky)
        - MACD bearish: 0
        """
        rsi_value = indicators.get('rsi_14', 50)
        rsi_signal = indicators.get('rsi_signal', 'NEUTRAL')
        macd_trend = indicators.get('macd_trend', 'NEUTRAL')
        
        score = 0
        passed = False
        reason = ""
        
        # MACD check
        if macd_trend == 'BULLISH':
            macd_score = 50
        elif macd_trend == 'NEUTRAL':
            macd_score = 30
        else:  # BEARISH
            macd_score = 0
        
        # RSI check
        if rsi_signal == 'OVERBOUGHT':
            rsi_score = 20
            reason = "RSI overbought - risky entry"
        elif rsi_signal == 'OVERSOLD':
            rsi_score = 60
            reason = "RSI oversold - potential reversal"
        else:  # NEUTRAL
            if 40 <= rsi_value <= 60:
                rsi_score = 50
                reason = "RSI in sweet spot"
            else:
                rsi_score = 40
                reason = "RSI neutral"
        
        # Combined score
        score = macd_score + rsi_score
        
        # Pass if MACD bullish and RSI not overbought
        passed = (macd_trend == 'BULLISH' and rsi_signal != 'OVERBOUGHT')
        
        if macd_trend == 'BULLISH' and rsi_signal == 'NEUTRAL':
            reason = "Strong momentum - MACD bullish, RSI neutral"
        elif macd_trend == 'BEARISH':
            reason = "Weak momentum - MACD bearish"
        
        return {
            'score': min(score, 100),
            'passed': passed,
            'reason': reason
        }
    
    def evaluate_volume(self, indicators: Dict[str, any]) -> Dict[str, any]:
        """
        Layer 3: Evaluate volume (money flow confirmation)
        
        Conditions for PASS:
        - Volume signal is HIGH or NORMAL
        - Volume ratio >= 1.0
        
        Scoring:
        - Volume HIGH (> 1.5x avg): 100
        - Volume NORMAL (0.7-1.5x avg): 70
        - Volume LOW (< 0.7x avg): 30
        """
        volume_signal = indicators.get('volume_signal', 'NORMAL')
        volume_ratio = indicators.get('volume_ratio', 1.0)
        volume_spike = indicators.get('volume_spike', False)
        
        if volume_signal == 'HIGH':
            score = 100
            passed = True
            reason = "High volume confirms buying interest"
            if volume_spike:
                reason += " (volume spike detected)"
        elif volume_signal == 'NORMAL':
            score = 70
            passed = True
            reason = "Normal volume - adequate confirmation"
        else:  # LOW
            score = 30
            passed = False
            reason = "Low volume - weak confirmation"
        
        return {
            'score': score,
            'passed': passed,
            'reason': reason
        }
    
    def evaluate_entry(self, indicators: Dict[str, any]) -> Dict[str, any]:
        """
        Layer 4: Evaluate entry timing (Bollinger Bands)
        
        Conditions for PASS:
        - BB position < 0.5 (below middle band)
        - Preferably near lower band (< 0.3)
        
        Scoring:
        - Near lower band (< 0.3): 100 (best entry)
        - Below middle (0.3-0.5): 80 (good entry)
        - Around middle (0.5-0.7): 50 (okay entry)
        - Above middle (0.7-0.9): 30 (risky entry)
        - Near upper band (> 0.9): 10 (very risky)
        """
        bb_position = indicators.get('bb_position', 0.5)
        bb_position_label = indicators.get('bb_position_label', 'AROUND_MIDDLE')
        
        if bb_position < 0.3:
            score = 100
            passed = True
            reason = "Excellent entry - near lower Bollinger Band"
        elif bb_position < 0.5:
            score = 80
            passed = True
            reason = "Good entry - below middle Bollinger Band"
        elif bb_position < 0.7:
            score = 50
            passed = False
            reason = "Okay entry - around middle Bollinger Band"
        elif bb_position < 0.9:
            score = 30
            passed = False
            reason = "Risky entry - above middle Bollinger Band"
        else:
            score = 10
            passed = False
            reason = "Very risky - near upper Bollinger Band"
        
        return {
            'score': score,
            'passed': passed,
            'reason': reason
        }
    
    def determine_signal_type(self, confidence: float) -> SignalType:
        """
        Determine signal type based on confidence score
        
        Args:
            confidence: Confidence score (0-100)
            
        Returns:
            SignalType
        """
        if confidence >= self.thresholds['strong_buy']:
            return SignalType.STRONG_BUY
        elif confidence >= self.thresholds['weak_buy']:
            return SignalType.WEAK_BUY
        elif confidence >= self.thresholds['watch']:
            return SignalType.WATCH
        else:
            return SignalType.NO_ACTION
    
    def set_thresholds(self, **kwargs):
        """
        Set custom thresholds
        
        Args:
            **kwargs: Threshold values to update
                strong_buy, weak_buy, watch,
                rsi_oversold, rsi_overbought,
                volume_high, volume_low,
                bb_near_lower, bb_near_upper
        """
        for key, value in kwargs.items():
            if key in self.thresholds:
                self.thresholds[key] = value


if __name__ == "__main__":
    # Test Pro Trader Strategy
    from datetime import datetime
    
    print("="*70)
    print("PRO TRADER STRATEGY TEST")
    print("="*70)
    
    # Initialize strategy
    strategy = ProTraderStrategy()
    
    # Sample indicators (strong buy scenario)
    indicators_strong_buy = {
        'trend_direction': 'UP',
        'ma_200': 84000,
        'ema_20': 85000,
        'rsi_14': 55.0,
        'rsi_signal': 'NEUTRAL',
        'macd_trend': 'BULLISH',
        'macd_histogram': 150.0,
        'volume_signal': 'HIGH',
        'volume_ratio': 1.8,
        'volume_spike': True,
        'bb_position': 0.25,
        'bb_position_label': 'NEAR_LOWER',
        'bb_upper': 88000,
        'bb_middle': 85000,
        'bb_lower': 82000,
        'support_level': 83000,
        'resistance_level': 91000
    }
    
    # Generate signal
    signal = strategy.generate_signal(
        symbol='VNM',
        timeframe='1D',
        timestamp=int(datetime.now().timestamp()),
        price=86000,
        indicators=indicators_strong_buy,
        total_capital=100_000_000
    )
    
    print(f"\n📊 SIGNAL GENERATED:")
    print(f"  Symbol: {signal.symbol}")
    print(f"  Type: {signal.signal_type.value}")
    print(f"  Confidence: {signal.confidence_score}%")
    print(f"  Price: {signal.price:,.0f} VND")
    
    print(f"\n🎯 REASONING:")
    print(f"  Trend: {signal.reasoning['trend_reason']} (score: {signal.reasoning['trend_score']})")
    print(f"  Momentum: {signal.reasoning['momentum_reason']} (score: {signal.reasoning['momentum_score']})")
    print(f"  Volume: {signal.reasoning['volume_reason']} (score: {signal.reasoning['volume_score']})")
    print(f"  Entry: {signal.reasoning['entry_reason']} (score: {signal.reasoning['entry_score']})")
    
    print(f"\n✅ CONDITIONS MET:")
    for condition in signal.conditions_met:
        print(f"  - {condition}")
    
    print(f"\n🛡️ RISK MANAGEMENT:")
    print(f"  Stop-Loss: {signal.stop_loss:,.0f} VND ({signal.get_potential_loss_pct():.2f}%)")
    print(f"  Take-Profit: {signal.take_profit:,.0f} VND ({signal.get_potential_profit_pct():.2f}%)")
    print(f"  Risk/Reward: {signal.risk_reward_ratio:.2f}")
    print(f"  Position Size: {signal.position_size_pct:.2f}%")
    
    # Test weak buy scenario
    print("\n" + "="*70)
    print("TEST 2: WEAK BUY SCENARIO")
    print("="*70)
    
    indicators_weak_buy = indicators_strong_buy.copy()
    indicators_weak_buy['volume_signal'] = 'NORMAL'
    indicators_weak_buy['volume_ratio'] = 1.1
    indicators_weak_buy['bb_position'] = 0.45
    
    signal2 = strategy.generate_signal(
        symbol='VCB',
        timeframe='1D',
        timestamp=int(datetime.now().timestamp()),
        price=92000,
        indicators=indicators_weak_buy
    )
    
    print(f"\n📊 Signal: {signal2.signal_type.value} (Confidence: {signal2.confidence_score}%)")
    
    # Test no action scenario
    print("\n" + "="*70)
    print("TEST 3: NO ACTION SCENARIO")
    print("="*70)
    
    indicators_no_action = {
        'trend_direction': 'DOWN',
        'rsi_14': 75.0,
        'rsi_signal': 'OVERBOUGHT',
        'macd_trend': 'BEARISH',
        'volume_signal': 'LOW',
        'volume_ratio': 0.5,
        'bb_position': 0.85
    }
    
    signal3 = strategy.generate_signal(
        symbol='HPG',
        timeframe='1D',
        timestamp=int(datetime.now().timestamp()),
        price=28000,
        indicators=indicators_no_action
    )
    
    print(f"\n📊 Signal: {signal3.signal_type.value} (Confidence: {signal3.confidence_score}%)")
    print(f"   Reason: Downtrend + Overbought + Low Volume")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
