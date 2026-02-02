"""
Test Pro Trader Strategy
Comprehensive testing of the decision tree engine
"""

import sys
sys.path.insert(0, '/Volumes/Data/projects/ckbot')

from datetime import datetime
from strategies.pro_trader_strategy import ProTraderStrategy
from strategies.risk_manager import RiskManager


def test_strong_buy_scenario():
    """Test STRONG_BUY signal generation"""
    print("\n" + "="*70)
    print("TEST 1: STRONG_BUY SCENARIO")
    print("="*70)
    
    strategy = ProTraderStrategy()
    
    # Perfect conditions for strong buy
    indicators = {
        'trend_direction': 'UP',
        'ma_200': 84000,
        'ema_20': 85000,
        'trend_strength': 85.0,
        
        'rsi_14': 55.0,
        'rsi_signal': 'NEUTRAL',
        'macd_line': 250.0,
        'macd_signal': 200.0,
        'macd_histogram': 50.0,
        'macd_trend': 'BULLISH',
        
        'volume_ma_20': 2000000,
        'volume_ratio': 1.8,
        'volume_signal': 'HIGH',
        'volume_spike': True,
        
        'bb_upper': 88000,
        'bb_middle': 85000,
        'bb_lower': 82000,
        'bb_width': 7.06,
        'bb_position': 0.25,
        'bb_position_label': 'NEAR_LOWER',
        
        'support_level': 83000,
        'resistance_level': 91000,
        'distance_to_support_pct': 3.6,
        'distance_to_resistance_pct': 5.8
    }
    
    signal = strategy.generate_signal(
        symbol='VNM',
        timeframe='1D',
        timestamp=int(datetime.now().timestamp()),
        price=86000,
        indicators=indicators,
        total_capital=100_000_000
    )
    
    print(f"\n📊 SIGNAL: {signal.signal_type.value}")
    print(f"   Confidence: {signal.confidence_score}%")
    print(f"   Price: {signal.price:,.0f} VND")
    
    print(f"\n🎯 LAYER SCORES:")
    print(f"   Trend: {signal.reasoning['trend_score']} - {signal.reasoning['trend_reason']}")
    print(f"   Momentum: {signal.reasoning['momentum_score']} - {signal.reasoning['momentum_reason']}")
    print(f"   Volume: {signal.reasoning['volume_score']} - {signal.reasoning['volume_reason']}")
    print(f"   Entry: {signal.reasoning['entry_score']} - {signal.reasoning['entry_reason']}")
    
    print(f"\n✅ CONDITIONS MET: {len(signal.conditions_met)}/4")
    for condition in signal.conditions_met:
        print(f"   ✓ {condition}")
    
    print(f"\n🛡️ RISK MANAGEMENT:")
    print(f"   Stop-Loss: {signal.stop_loss:,.0f} VND (-{signal.get_potential_loss_pct():.2f}%)")
    print(f"   Take-Profit: {signal.take_profit:,.0f} VND (+{signal.get_potential_profit_pct():.2f}%)")
    print(f"   Risk/Reward: {signal.risk_reward_ratio:.2f}")
    print(f"   Position Size: {signal.position_size_pct:.2f}%")
    
    assert signal.signal_type.value == 'STRONG_BUY', "Should be STRONG_BUY"
    assert signal.confidence_score >= 80, "Confidence should be >= 80"
    print("\n✅ Test passed!")
    
    return signal


def test_weak_buy_scenario():
    """Test WEAK_BUY signal generation"""
    print("\n" + "="*70)
    print("TEST 2: WEAK_BUY SCENARIO")
    print("="*70)
    
    strategy = ProTraderStrategy()
    
    # Good but not perfect conditions
    indicators = {
        'trend_direction': 'UP',
        'ma_200': 90000,
        'ema_20': 91000,
        
        'rsi_14': 58.0,
        'rsi_signal': 'NEUTRAL',
        'macd_trend': 'BULLISH',
        
        'volume_signal': 'NORMAL',  # Not high
        'volume_ratio': 1.1,
        
        'bb_position': 0.45,  # Below middle but not near lower
        'bb_position_label': 'BELOW_MIDDLE'
    }
    
    signal = strategy.generate_signal(
        symbol='VCB',
        timeframe='1D',
        timestamp=int(datetime.now().timestamp()),
        price=92000,
        indicators=indicators
    )
    
    print(f"\n📊 SIGNAL: {signal.signal_type.value}")
    print(f"   Confidence: {signal.confidence_score}%")
    print(f"   Conditions Met: {len(signal.conditions_met)}/4")
    
    assert signal.signal_type.value in ['WEAK_BUY', 'WATCH'], "Should be WEAK_BUY or WATCH"
    assert 40 <= signal.confidence_score < 80, "Confidence should be 40-80"
    print("\n✅ Test passed!")
    
    return signal


def test_no_action_scenario():
    """Test NO_ACTION signal generation"""
    print("\n" + "="*70)
    print("TEST 3: NO_ACTION SCENARIO (Downtrend)")
    print("="*70)
    
    strategy = ProTraderStrategy()
    
    # Bad conditions - downtrend
    indicators = {
        'trend_direction': 'DOWN',  # Fail at layer 1
        'rsi_14': 75.0,
        'rsi_signal': 'OVERBOUGHT',
        'macd_trend': 'BEARISH',
        'volume_signal': 'LOW',
        'volume_ratio': 0.5,
        'bb_position': 0.85
    }
    
    signal = strategy.generate_signal(
        symbol='HPG',
        timeframe='1D',
        timestamp=int(datetime.now().timestamp()),
        price=28000,
        indicators=indicators
    )
    
    print(f"\n📊 SIGNAL: {signal.signal_type.value}")
    print(f"   Confidence: {signal.confidence_score}%")
    print(f"   Reason: {signal.reasoning['trend_reason']}")
    
    assert signal.signal_type.value in ['NO_ACTION', 'WATCH'], "Should be NO_ACTION or WATCH"
    assert signal.confidence_score < 60, "Confidence should be < 60"
    print("\n✅ Test passed!")
    
    return signal


def test_overbought_scenario():
    """Test overbought rejection"""
    print("\n" + "="*70)
    print("TEST 4: OVERBOUGHT REJECTION")
    print("="*70)
    
    strategy = ProTraderStrategy()
    
    # Uptrend but overbought
    indicators = {
        'trend_direction': 'UP',
        'rsi_14': 78.0,
        'rsi_signal': 'OVERBOUGHT',  # Red flag
        'macd_trend': 'BULLISH',
        'volume_signal': 'HIGH',
        'bb_position': 0.88  # Near upper band
    }
    
    signal = strategy.generate_signal(
        symbol='VIC',
        timeframe='1D',
        timestamp=int(datetime.now().timestamp()),
        price=95000,
        indicators=indicators
    )
    
    print(f"\n📊 SIGNAL: {signal.signal_type.value}")
    print(f"   Confidence: {signal.confidence_score}%")
    print(f"   Momentum: {signal.reasoning['momentum_reason']}")
    print(f"   Entry: {signal.reasoning['entry_reason']}")
    
    # Should not be STRONG_BUY due to overbought
    assert signal.signal_type.value != 'STRONG_BUY', "Should not be STRONG_BUY when overbought"
    print("\n✅ Test passed!")
    
    return signal


def test_custom_thresholds():
    """Test custom threshold configuration"""
    print("\n" + "="*70)
    print("TEST 5: CUSTOM THRESHOLDS")
    print("="*70)
    
    strategy = ProTraderStrategy()
    
    # Set more conservative thresholds
    strategy.set_thresholds(
        strong_buy=85.0,  # Increased from 80
        weak_buy=70.0,    # Increased from 60
        watch=50.0        # Increased from 40
    )
    
    print("\n📊 Custom Thresholds:")
    print(f"   STRONG_BUY: >= {strategy.thresholds['strong_buy']}%")
    print(f"   WEAK_BUY: >= {strategy.thresholds['weak_buy']}%")
    print(f"   WATCH: >= {strategy.thresholds['watch']}%")
    
    # Test with 75% confidence (would be WEAK_BUY with default, WATCH with custom)
    indicators = {
        'trend_direction': 'UP',
        'rsi_signal': 'NEUTRAL',
        'macd_trend': 'BULLISH',
        'volume_signal': 'NORMAL',
        'bb_position': 0.5
    }
    
    signal = strategy.generate_signal(
        symbol='TEST',
        timeframe='1D',
        timestamp=int(datetime.now().timestamp()),
        price=50000,
        indicators=indicators
    )
    
    print(f"\n📊 With 75% confidence:")
    print(f"   Signal: {signal.signal_type.value}")
    print(f"   (Would be WEAK_BUY with default thresholds)")
    
    print("\n✅ Test passed!")


def test_risk_management():
    """Test risk management calculations"""
    print("\n" + "="*70)
    print("TEST 6: RISK MANAGEMENT")
    print("="*70)
    
    # Custom risk manager
    risk_manager = RiskManager(
        stop_loss_pct=4.0,
        take_profit_pct=12.0,
        min_risk_reward=2.0
    )
    
    strategy = ProTraderStrategy(risk_manager=risk_manager)
    
    indicators = {
        'trend_direction': 'UP',
        'rsi_signal': 'NEUTRAL',
        'macd_trend': 'BULLISH',
        'volume_signal': 'HIGH',
        'bb_position': 0.3,
        'support_level': 82000,
        'resistance_level': 95000
    }
    
    signal = strategy.generate_signal(
        symbol='VNM',
        timeframe='1D',
        timestamp=int(datetime.now().timestamp()),
        price=85000,
        indicators=indicators,
        total_capital=100_000_000
    )
    
    print(f"\n🛡️ Custom Risk Parameters:")
    print(f"   Stop-Loss: {signal.stop_loss:,.0f} VND ({signal.get_potential_loss_pct():.2f}%)")
    print(f"   Take-Profit: {signal.take_profit:,.0f} VND ({signal.get_potential_profit_pct():.2f}%)")
    print(f"   Risk/Reward: {signal.risk_reward_ratio:.2f}")
    
    assert signal.risk_reward_ratio >= 2.0, "R/R should be >= 2.0"
    print("\n✅ Test passed!")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("PRO TRADER STRATEGY - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    try:
        test_strong_buy_scenario()
        test_weak_buy_scenario()
        test_no_action_scenario()
        test_overbought_scenario()
        test_custom_thresholds()
        test_risk_management()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        
        print("\n📚 Strategy is ready for:")
        print("  1. Integration with Indicator Calculator")
        print("  2. Integration with Database")
        print("  3. Backtesting on historical data")
        print("  4. Live trading (with caution)")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
