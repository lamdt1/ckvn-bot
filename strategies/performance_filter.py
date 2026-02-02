"""
Symbol Performance Filter
Tracks trading performance per symbol and filters based on historical results
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import sqlite3

logger = logging.getLogger(__name__)


class SymbolPerformanceFilter:
    """
    Performance-based symbol filtering
    
    Features:
    - Track win rate per symbol
    - Skip poor performers (< 40% win rate after 5+ trades)
    - Adjust confidence based on historical performance
    - Implement cooldown after consecutive losses
    """
    
    def __init__(self, 
                 db_path: str,
                 min_trades_for_filter: int = 5,
                 min_win_rate: float = 40.0,
                 cooldown_days: int = 7,
                 consecutive_losses_for_cooldown: int = 3):
        """
        Initialize performance filter
        
        Args:
            db_path: Path to trading database
            min_trades_for_filter: Minimum trades before filtering (default: 5)
            min_win_rate: Minimum win rate % to continue trading (default: 40%)
            cooldown_days: Days to skip symbol after consecutive losses (default: 7)
            consecutive_losses_for_cooldown: Number of losses to trigger cooldown (default: 3)
        """
        self.db_path = db_path
        self.min_trades_for_filter = min_trades_for_filter
        self.min_win_rate = min_win_rate
        self.cooldown_days = cooldown_days
        self.consecutive_losses_for_cooldown = consecutive_losses_for_cooldown
        
        logger.info(f"✅ Performance filter initialized (min_trades={min_trades_for_filter}, min_win_rate={min_win_rate}%)")
    
    def get_symbol_stats(self, symbol: str) -> Optional[Dict]:
        """
        Get performance statistics for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stats or None if no data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query from signal_performance view
            cursor.execute("""
                SELECT 
                    symbol,
                    total_trades,
                    winning_trades,
                    losing_trades,
                    win_rate,
                    avg_profit_pct,
                    total_profit_pct,
                    max_profit_pct,
                    max_loss_pct,
                    avg_hold_days
                FROM signal_performance
                WHERE symbol = ?
            """, (symbol,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return {
                'symbol': row[0],
                'total_trades': row[1],
                'winning_trades': row[2],
                'losing_trades': row[3],
                'win_rate': row[4],
                'avg_profit_pct': row[5],
                'total_profit_pct': row[6],
                'max_profit_pct': row[7],
                'max_loss_pct': row[8],
                'avg_hold_days': row[9]
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for {symbol}: {e}")
            return None
    
    def get_recent_trades(self, symbol: str, limit: int = 10) -> list:
        """
        Get recent trades for a symbol
        
        Args:
            symbol: Stock symbol
            limit: Number of recent trades to fetch
            
        Returns:
            List of recent trade dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    signal_id,
                    symbol,
                    signal_type,
                    entry_price,
                    exit_price,
                    profit_loss_pct,
                    close_timestamp
                FROM signals
                WHERE symbol = ?
                AND is_closed = 1
                ORDER BY close_timestamp DESC
                LIMIT ?
            """, (symbol, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            trades = []
            for row in rows:
                trades.append({
                    'signal_id': row[0],
                    'symbol': row[1],
                    'signal_type': row[2],
                    'entry_price': row[3],
                    'exit_price': row[4],
                    'profit_loss_pct': row[5],
                    'close_timestamp': row[6]
                })
            
            return trades
            
        except Exception as e:
            logger.error(f"Failed to get recent trades for {symbol}: {e}")
            return []
    
    def check_consecutive_losses(self, symbol: str) -> Tuple[bool, int]:
        """
        Check if symbol has consecutive losses
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Tuple of (has_consecutive_losses, loss_count)
        """
        recent_trades = self.get_recent_trades(symbol, limit=self.consecutive_losses_for_cooldown)
        
        if len(recent_trades) < self.consecutive_losses_for_cooldown:
            return False, 0
        
        # Check if all recent trades are losses
        consecutive_losses = 0
        for trade in recent_trades:
            if trade['profit_loss_pct'] < 0:
                consecutive_losses += 1
            else:
                break
        
        has_consecutive = consecutive_losses >= self.consecutive_losses_for_cooldown
        
        return has_consecutive, consecutive_losses
    
    def is_in_cooldown(self, symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Check if symbol is in cooldown period
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Tuple of (is_in_cooldown, reason)
        """
        # Check consecutive losses
        has_consecutive, loss_count = self.check_consecutive_losses(symbol)
        
        if not has_consecutive:
            return False, None
        
        # Get most recent trade timestamp
        recent_trades = self.get_recent_trades(symbol, limit=1)
        if not recent_trades:
            return False, None
        
        last_trade_time = recent_trades[0]['close_timestamp']
        cooldown_end = last_trade_time + (self.cooldown_days * 24 * 60 * 60)
        current_time = int(datetime.now().timestamp())
        
        if current_time < cooldown_end:
            days_left = (cooldown_end - current_time) / (24 * 60 * 60)
            reason = f"{loss_count} consecutive losses, cooldown for {days_left:.1f} more days"
            return True, reason
        
        return False, None
    
    def should_skip_symbol(self, symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Determine if symbol should be skipped
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Tuple of (should_skip, reason)
        """
        # Get performance stats
        stats = self.get_symbol_stats(symbol)
        
        # No history - don't skip (give it a chance)
        if not stats:
            return False, None
        
        # Not enough trades - don't skip yet
        if stats['total_trades'] < self.min_trades_for_filter:
            return False, None
        
        # Check cooldown first
        in_cooldown, cooldown_reason = self.is_in_cooldown(symbol)
        if in_cooldown:
            return True, f"COOLDOWN: {cooldown_reason}"
        
        # Check win rate
        if stats['win_rate'] < self.min_win_rate:
            reason = f"Low win rate: {stats['win_rate']:.1f}% < {self.min_win_rate}% (after {stats['total_trades']} trades)"
            return True, reason
        
        # Check if average profit is negative
        if stats['avg_profit_pct'] < -2.0:  # Losing more than 2% on average
            reason = f"Negative avg profit: {stats['avg_profit_pct']:.2f}%"
            return True, reason
        
        return False, None
    
    def adjust_confidence(self, symbol: str, base_confidence: float) -> Tuple[float, str]:
        """
        Adjust confidence score based on historical performance
        
        Args:
            symbol: Stock symbol
            base_confidence: Base confidence from strategy (0-100)
            
        Returns:
            Tuple of (adjusted_confidence, reason)
        """
        stats = self.get_symbol_stats(symbol)
        
        # No history - use base confidence
        if not stats or stats['total_trades'] < self.min_trades_for_filter:
            return base_confidence, "No historical data"
        
        adjustment = 0.0
        reasons = []
        
        # 1. Win rate adjustment (-10 to +10 points)
        win_rate = stats['win_rate']
        if win_rate >= 70:
            adjustment += 10
            reasons.append(f"High win rate ({win_rate:.1f}%): +10")
        elif win_rate >= 60:
            adjustment += 5
            reasons.append(f"Good win rate ({win_rate:.1f}%): +5")
        elif win_rate <= 40:
            adjustment -= 10
            reasons.append(f"Low win rate ({win_rate:.1f}%): -10")
        elif win_rate <= 50:
            adjustment -= 5
            reasons.append(f"Below avg win rate ({win_rate:.1f}%): -5")
        
        # 2. Average profit adjustment (-5 to +5 points)
        avg_profit = stats['avg_profit_pct']
        if avg_profit >= 5.0:
            adjustment += 5
            reasons.append(f"High avg profit ({avg_profit:.2f}%): +5")
        elif avg_profit >= 3.0:
            adjustment += 3
            reasons.append(f"Good avg profit ({avg_profit:.2f}%): +3")
        elif avg_profit < 0:
            adjustment -= 5
            reasons.append(f"Negative avg profit ({avg_profit:.2f}%): -5")
        
        # 3. Recent performance (-5 to +5 points)
        recent_trades = self.get_recent_trades(symbol, limit=5)
        if len(recent_trades) >= 3:
            recent_wins = sum(1 for t in recent_trades if t['profit_loss_pct'] > 0)
            recent_win_rate = (recent_wins / len(recent_trades)) * 100
            
            if recent_win_rate >= 80:
                adjustment += 5
                reasons.append(f"Hot streak ({recent_win_rate:.0f}% recent): +5")
            elif recent_win_rate <= 20:
                adjustment -= 5
                reasons.append(f"Cold streak ({recent_win_rate:.0f}% recent): -5")
        
        # Apply adjustment
        adjusted_confidence = max(0, min(100, base_confidence + adjustment))
        
        reason = f"Base: {base_confidence:.1f}% → Adjusted: {adjusted_confidence:.1f}% ({', '.join(reasons)})"
        
        return adjusted_confidence, reason
    
    def get_all_symbol_rankings(self) -> list:
        """
        Get all symbols ranked by performance
        
        Returns:
            List of symbol stats sorted by performance
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    symbol,
                    total_trades,
                    win_rate,
                    avg_profit_pct,
                    total_profit_pct
                FROM signal_performance
                WHERE total_trades >= ?
                ORDER BY total_profit_pct DESC
            """, (self.min_trades_for_filter,))
            
            rows = cursor.fetchall()
            conn.close()
            
            rankings = []
            for row in rows:
                rankings.append({
                    'symbol': row[0],
                    'total_trades': row[1],
                    'win_rate': row[2],
                    'avg_profit_pct': row[3],
                    'total_profit_pct': row[4]
                })
            
            return rankings
            
        except Exception as e:
            logger.error(f"Failed to get symbol rankings: {e}")
            return []
    
    def print_performance_summary(self):
        """Print performance summary for all symbols"""
        rankings = self.get_all_symbol_rankings()
        
        if not rankings:
            print("\n📊 No performance data yet")
            return
        
        print("\n" + "="*80)
        print("📊 SYMBOL PERFORMANCE RANKINGS")
        print("="*80)
        print(f"{'Rank':<6} {'Symbol':<8} {'Trades':<8} {'Win Rate':<12} {'Avg P&L':<12} {'Total P&L':<12}")
        print("-"*80)
        
        for i, stats in enumerate(rankings, 1):
            win_rate_str = f"{stats['win_rate']:.1f}%"
            avg_pnl_str = f"{stats['avg_profit_pct']:+.2f}%"
            total_pnl_str = f"{stats['total_profit_pct']:+.2f}%"
            
            print(f"{i:<6} {stats['symbol']:<8} {stats['total_trades']:<8} {win_rate_str:<12} {avg_pnl_str:<12} {total_pnl_str:<12}")
        
        print("="*80)


if __name__ == "__main__":
    # Test performance filter
    print("="*70)
    print("PERFORMANCE FILTER TEST")
    print("="*70)
    
    # Initialize filter
    filter = SymbolPerformanceFilter(
        db_path="database/trading.db",
        min_trades_for_filter=5,
        min_win_rate=40.0,
        cooldown_days=7
    )
    
    # Test with example symbol
    test_symbol = "VNM"
    
    print(f"\n📊 Testing with symbol: {test_symbol}")
    
    # Get stats
    stats = filter.get_symbol_stats(test_symbol)
    if stats:
        print(f"\n✅ Performance Stats:")
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Win Rate: {stats['win_rate']:.1f}%")
        print(f"  Avg Profit: {stats['avg_profit_pct']:.2f}%")
    else:
        print(f"\n⚠️ No performance data for {test_symbol}")
    
    # Check if should skip
    should_skip, reason = filter.should_skip_symbol(test_symbol)
    if should_skip:
        print(f"\n🚫 SKIP: {reason}")
    else:
        print(f"\n✅ CONTINUE: Symbol passed filters")
    
    # Adjust confidence
    base_confidence = 75.0
    adjusted, reason = filter.adjust_confidence(test_symbol, base_confidence)
    print(f"\n🎯 Confidence Adjustment:")
    print(f"  {reason}")
    
    # Print rankings
    filter.print_performance_summary()
