"""
Risk Manager
Handles risk management calculations: stop-loss, take-profit, position sizing
"""

from typing import Dict, Optional, Tuple
import math


class RiskManager:
    """
    Risk management calculator for Pro Trader strategy
    
    Implements:
    - Stop-loss calculation (fixed % or ATR-based)
    - Take-profit calculation (fixed % or risk-reward based)
    - Position sizing (fixed % or Kelly Criterion)
    - Risk/Reward ratio validation
    """
    
    def __init__(self,
                 stop_loss_pct: float = 5.0,
                 take_profit_pct: float = 10.0,
                 position_size_pct: float = 5.0,
                 min_risk_reward: float = 1.5,
                 max_position_size_pct: float = 10.0,
                 use_atr_stop_loss: bool = False,
                 atr_multiplier: float = 2.0):
        """
        Initialize risk manager
        
        Args:
            stop_loss_pct: Default stop-loss percentage (default: 5%)
            take_profit_pct: Default take-profit percentage (default: 10%)
            position_size_pct: Default position size as % of capital (default: 5%)
            min_risk_reward: Minimum acceptable risk/reward ratio (default: 1.5)
            max_position_size_pct: Maximum position size (default: 10%)
            use_atr_stop_loss: Use ATR for stop-loss calculation (default: False)
            atr_multiplier: ATR multiplier for stop-loss (default: 2.0)
        """
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.position_size_pct = position_size_pct
        self.min_risk_reward = min_risk_reward
        self.max_position_size_pct = max_position_size_pct
        self.use_atr_stop_loss = use_atr_stop_loss
        self.atr_multiplier = atr_multiplier
    
    def calculate_stop_loss(self, 
                           price: float, 
                           indicators: Dict[str, any]) -> float:
        """
        Calculate stop-loss price
        
        Args:
            price: Current price
            indicators: Dictionary with indicator values
            
        Returns:
            Stop-loss price
        """
        if self.use_atr_stop_loss and 'atr' in indicators and indicators['atr']:
            # ATR-based stop-loss
            atr = indicators['atr']
            stop_loss = price - (atr * self.atr_multiplier)
        else:
            # Fixed percentage stop-loss
            stop_loss = price * (1 - self.stop_loss_pct / 100)
        
        # Optional: Use support level as stop-loss if closer
        if 'support_level' in indicators and indicators['support_level']:
            support = indicators['support_level']
            # Use support if it's within reasonable range (2-8% below price)
            distance_pct = ((price - support) / price) * 100
            if 2 <= distance_pct <= 8:
                stop_loss = max(stop_loss, support * 0.99)  # Slightly below support
        
        return round(stop_loss, 2)
    
    def calculate_take_profit(self,
                             price: float,
                             stop_loss: float,
                             indicators: Dict[str, any],
                             target_rr: float = 2.0) -> float:
        """
        Calculate take-profit price
        
        Args:
            price: Current price
            stop_loss: Stop-loss price
            indicators: Dictionary with indicator values
            target_rr: Target risk/reward ratio (default: 2.0)
            
        Returns:
            Take-profit price
        """
        # Calculate risk
        risk = price - stop_loss
        
        # Method 1: Risk/Reward based
        rr_take_profit = price + (risk * target_rr)
        
        # Method 2: Fixed percentage
        fixed_take_profit = price * (1 + self.take_profit_pct / 100)
        
        # Use the more conservative (lower) target
        take_profit = min(rr_take_profit, fixed_take_profit)
        
        # Optional: Use resistance level as take-profit if closer
        if 'resistance_level' in indicators and indicators['resistance_level']:
            resistance = indicators['resistance_level']
            # Use resistance if it's within reasonable range
            distance_pct = ((resistance - price) / price) * 100
            if 5 <= distance_pct <= 15:
                take_profit = min(take_profit, resistance * 0.99)  # Slightly below resistance
        
        return round(take_profit, 2)
    
    def calculate_risk_reward_ratio(self,
                                   price: float,
                                   stop_loss: float,
                                   take_profit: float) -> float:
        """
        Calculate risk/reward ratio
        
        Args:
            price: Current price
            stop_loss: Stop-loss price
            take_profit: Take-profit price
            
        Returns:
            Risk/Reward ratio
        """
        risk = price - stop_loss
        reward = take_profit - price
        
        if risk <= 0:
            return 0.0
        
        rr_ratio = reward / risk
        return round(rr_ratio, 2)
    
    def calculate_position_size(self,
                               price: float,
                               stop_loss: float,
                               total_capital: float,
                               confidence_score: float,
                               max_risk_per_trade_pct: float = 2.0) -> Tuple[float, int]:
        """
        Calculate position size based on risk management
        
        Args:
            price: Current price
            stop_loss: Stop-loss price
            total_capital: Total available capital
            confidence_score: Signal confidence (0-100)
            max_risk_per_trade_pct: Max risk per trade as % of capital (default: 2%)
            
        Returns:
            Tuple of (position_size_pct, quantity)
        """
        # Calculate risk per share
        risk_per_share = price - stop_loss
        
        if risk_per_share <= 0:
            return 0.0, 0
        
        # Calculate max capital to risk
        max_risk_capital = total_capital * (max_risk_per_trade_pct / 100)
        
        # Calculate quantity based on risk
        quantity = int(max_risk_capital / risk_per_share)
        
        # Calculate position value
        position_value = quantity * price
        
        # Calculate position size as % of capital
        position_size_pct = (position_value / total_capital) * 100
        
        # Adjust based on confidence score
        # Higher confidence = larger position (up to max)
        confidence_multiplier = confidence_score / 100
        adjusted_position_pct = position_size_pct * confidence_multiplier
        
        # Cap at max position size
        final_position_pct = min(adjusted_position_pct, self.max_position_size_pct)
        
        # Recalculate quantity based on final position size
        final_position_value = total_capital * (final_position_pct / 100)
        final_quantity = int(final_position_value / price)
        
        return round(final_position_pct, 2), final_quantity
    
    def validate_signal(self,
                       price: float,
                       stop_loss: float,
                       take_profit: float) -> Tuple[bool, str]:
        """
        Validate if signal meets risk management criteria
        
        Args:
            price: Current price
            stop_loss: Stop-loss price
            take_profit: Take-profit price
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check stop-loss is below price
        if stop_loss >= price:
            return False, "Stop-loss must be below current price"
        
        # Check take-profit is above price
        if take_profit <= price:
            return False, "Take-profit must be above current price"
        
        # Check risk/reward ratio
        rr_ratio = self.calculate_risk_reward_ratio(price, stop_loss, take_profit)
        if rr_ratio < self.min_risk_reward:
            return False, f"Risk/Reward ratio {rr_ratio:.2f} below minimum {self.min_risk_reward}"
        
        # Check stop-loss is not too tight (< 1%)
        stop_loss_pct = ((price - stop_loss) / price) * 100
        if stop_loss_pct < 1.0:
            return False, f"Stop-loss too tight ({stop_loss_pct:.2f}%)"
        
        # Check stop-loss is not too wide (> 15%)
        if stop_loss_pct > 15.0:
            return False, f"Stop-loss too wide ({stop_loss_pct:.2f}%)"
        
        return True, "Valid"
    
    def calculate_all(self,
                     price: float,
                     indicators: Dict[str, any],
                     total_capital: float = 100_000_000,
                     confidence_score: float = 80.0) -> Dict[str, any]:
        """
        Calculate all risk management parameters
        
        Args:
            price: Current price
            indicators: Dictionary with indicator values
            total_capital: Total capital (default: 100M VND)
            confidence_score: Signal confidence (default: 80%)
            
        Returns:
            Dictionary with all risk management parameters
        """
        # Calculate stop-loss
        stop_loss = self.calculate_stop_loss(price, indicators)
        
        # Calculate take-profit
        take_profit = self.calculate_take_profit(price, stop_loss, indicators)
        
        # Calculate risk/reward ratio
        rr_ratio = self.calculate_risk_reward_ratio(price, stop_loss, take_profit)
        
        # Calculate position size
        position_size_pct, quantity = self.calculate_position_size(
            price, stop_loss, total_capital, confidence_score
        )
        
        # Validate signal
        is_valid, validation_reason = self.validate_signal(price, stop_loss, take_profit)
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': rr_ratio,
            'position_size_pct': position_size_pct,
            'quantity': quantity,
            'is_valid': is_valid,
            'validation_reason': validation_reason,
            'potential_profit_pct': ((take_profit - price) / price) * 100,
            'potential_loss_pct': ((price - stop_loss) / price) * 100
        }


if __name__ == "__main__":
    # Test Risk Manager
    print("="*70)
    print("RISK MANAGER TEST")
    print("="*70)
    
    risk_manager = RiskManager(
        stop_loss_pct=5.0,
        take_profit_pct=10.0,
        position_size_pct=5.0,
        min_risk_reward=1.5
    )
    
    # Sample data
    price = 86000
    indicators = {
        'support_level': 83000,
        'resistance_level': 91000,
        'atr': 2000
    }
    total_capital = 100_000_000  # 100M VND
    confidence_score = 85.0
    
    # Calculate all parameters
    risk_params = risk_manager.calculate_all(
        price, indicators, total_capital, confidence_score
    )
    
    print(f"\n📊 Price: {price:,.0f} VND")
    print(f"💰 Capital: {total_capital:,.0f} VND")
    print(f"🎯 Confidence: {confidence_score}%")
    
    print(f"\n🛡️ RISK MANAGEMENT:")
    print(f"  Stop-Loss: {risk_params['stop_loss']:,.0f} VND ({risk_params['potential_loss_pct']:.2f}%)")
    print(f"  Take-Profit: {risk_params['take_profit']:,.0f} VND ({risk_params['potential_profit_pct']:.2f}%)")
    print(f"  Risk/Reward: {risk_params['risk_reward_ratio']:.2f}")
    
    print(f"\n💼 POSITION SIZING:")
    print(f"  Position Size: {risk_params['position_size_pct']:.2f}%")
    print(f"  Quantity: {risk_params['quantity']} shares")
    print(f"  Position Value: {risk_params['quantity'] * price:,.0f} VND")
    
    print(f"\n✅ VALIDATION:")
    print(f"  Valid: {risk_params['is_valid']}")
    print(f"  Reason: {risk_params['validation_reason']}")
    
    print("\n" + "="*70)
