"""
Advanced Query Helpers for Trading Database
Provides high-level analysis functions for strategy optimization
"""

from database.db_manager import TradingDatabase
from typing import List, Dict, Any, Optional
import json


class StrategyAnalyzer:
    """Advanced analysis tools for trading strategies"""
    
    def __init__(self, db: TradingDatabase):
        self.db = db
        
    def find_best_strategies(self, min_trades: int = 10, 
                            min_win_rate: float = 60.0) -> List[Dict[str, Any]]:
        """
        Find best performing strategies
        
        Args:
            min_trades: Minimum number of closed trades
            min_win_rate: Minimum win rate percentage
            
        Returns:
            List of top strategies
        """
        query = """
        SELECT * FROM v_strategy_performance
        WHERE closed_positions >= ?
          AND win_rate_pct >= ?
        ORDER BY total_pnl_pct DESC, win_rate_pct DESC
        LIMIT 10
        """
        
        rows = self.db.execute_query(query, (min_trades, min_win_rate))
        return [dict(row) for row in rows]
        
    def find_worst_strategies(self, min_trades: int = 5) -> List[Dict[str, Any]]:
        """
        Find worst performing strategies to avoid
        
        Args:
            min_trades: Minimum number of trades
            
        Returns:
            List of worst strategies
        """
        query = """
        SELECT * FROM v_strategy_performance
        WHERE closed_positions >= ?
        ORDER BY total_pnl_pct ASC, win_rate_pct ASC
        LIMIT 10
        """
        
        rows = self.db.execute_query(query, (min_trades,))
        return [dict(row) for row in rows]
        
    def analyze_indicator_importance(self) -> Dict[str, Any]:
        """
        Analyze which indicators contribute most to winning trades
        
        Returns:
            Dictionary with indicator importance scores
        """
        # Analyze trend direction impact
        trend_query = """
        SELECT 
            json_extract(reasoning, '$.trend_direction') as trend,
            COUNT(*) as trades,
            ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
            ROUND(
                100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
                2
            ) as win_rate
        FROM signals
        WHERE is_closed = 1 AND reasoning IS NOT NULL
        GROUP BY trend
        """
        
        # Analyze RSI signal impact
        rsi_query = """
        SELECT 
            json_extract(reasoning, '$.rsi_signal') as rsi_signal,
            COUNT(*) as trades,
            ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
            ROUND(
                100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
                2
            ) as win_rate
        FROM signals
        WHERE is_closed = 1 AND reasoning IS NOT NULL
        GROUP BY rsi_signal
        """
        
        # Analyze MACD trend impact
        macd_query = """
        SELECT 
            json_extract(reasoning, '$.macd_trend') as macd_trend,
            COUNT(*) as trades,
            ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
            ROUND(
                100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
                2
            ) as win_rate
        FROM signals
        WHERE is_closed = 1 AND reasoning IS NOT NULL
        GROUP BY macd_trend
        """
        
        # Analyze volume signal impact
        volume_query = """
        SELECT 
            json_extract(reasoning, '$.volume_signal') as volume_signal,
            COUNT(*) as trades,
            ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
            ROUND(
                100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
                2
            ) as win_rate
        FROM signals
        WHERE is_closed = 1 AND reasoning IS NOT NULL
        GROUP BY volume_signal
        """
        
        return {
            'trend': [dict(row) for row in self.db.execute_query(trend_query)],
            'rsi': [dict(row) for row in self.db.execute_query(rsi_query)],
            'macd': [dict(row) for row in self.db.execute_query(macd_query)],
            'volume': [dict(row) for row in self.db.execute_query(volume_query)]
        }
        
    def find_optimal_holding_period(self) -> List[Dict[str, Any]]:
        """
        Analyze optimal holding period for maximum profit
        
        Returns:
            List of holding period analysis
        """
        query = """
        SELECT 
            CASE 
                WHEN holding_days <= 1 THEN '0-1 days'
                WHEN holding_days <= 3 THEN '2-3 days'
                WHEN holding_days <= 7 THEN '4-7 days'
                WHEN holding_days <= 14 THEN '8-14 days'
                WHEN holding_days <= 30 THEN '15-30 days'
                ELSE '30+ days'
            END as holding_period,
            COUNT(*) as trades,
            ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
            ROUND(
                100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
                2
            ) as win_rate,
            ROUND(MAX(profit_loss_pct), 2) as max_win,
            ROUND(MIN(profit_loss_pct), 2) as max_loss
        FROM signals
        WHERE is_closed = 1 AND holding_days IS NOT NULL
        GROUP BY holding_period
        ORDER BY 
            CASE holding_period
                WHEN '0-1 days' THEN 1
                WHEN '2-3 days' THEN 2
                WHEN '4-7 days' THEN 3
                WHEN '8-14 days' THEN 4
                WHEN '15-30 days' THEN 5
                ELSE 6
            END
        """
        
        rows = self.db.execute_query(query)
        return [dict(row) for row in rows]
        
    def analyze_confidence_accuracy(self) -> List[Dict[str, Any]]:
        """
        Check if high confidence signals actually perform better
        
        Returns:
            List of confidence vs performance analysis
        """
        query = """
        SELECT 
            CASE 
                WHEN confidence_score >= 90 THEN '90-100 (Very High)'
                WHEN confidence_score >= 80 THEN '80-89 (High)'
                WHEN confidence_score >= 70 THEN '70-79 (Medium-High)'
                WHEN confidence_score >= 60 THEN '60-69 (Medium)'
                ELSE '0-59 (Low)'
            END as confidence_range,
            COUNT(*) as trades,
            ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
            ROUND(
                100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
                2
            ) as win_rate,
            ROUND(AVG(confidence_score), 2) as avg_confidence
        FROM signals
        WHERE is_closed = 1 AND confidence_score IS NOT NULL
        GROUP BY confidence_range
        ORDER BY avg_confidence DESC
        """
        
        rows = self.db.execute_query(query)
        return [dict(row) for row in rows]
        
    def find_best_entry_conditions(self, min_trades: int = 5) -> List[Dict[str, Any]]:
        """
        Find best entry conditions (price position in Bollinger Bands, distance to support, etc.)
        
        Args:
            min_trades: Minimum number of trades
            
        Returns:
            List of entry condition analysis
        """
        query = """
        SELECT 
            CASE 
                WHEN json_extract(reasoning, '$.bb_position') < 0.2 THEN 'Near Lower BB'
                WHEN json_extract(reasoning, '$.bb_position') < 0.4 THEN 'Below Middle BB'
                WHEN json_extract(reasoning, '$.bb_position') < 0.6 THEN 'Around Middle BB'
                WHEN json_extract(reasoning, '$.bb_position') < 0.8 THEN 'Above Middle BB'
                ELSE 'Near Upper BB'
            END as bb_entry_zone,
            COUNT(*) as trades,
            ROUND(AVG(profit_loss_pct), 2) as avg_pnl,
            ROUND(
                100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / COUNT(*),
                2
            ) as win_rate
        FROM signals
        WHERE is_closed = 1 
          AND reasoning IS NOT NULL
          AND json_extract(reasoning, '$.bb_position') IS NOT NULL
        GROUP BY bb_entry_zone
        HAVING trades >= ?
        ORDER BY win_rate DESC, avg_pnl DESC
        """
        
        rows = self.db.execute_query(query, (min_trades,))
        return [dict(row) for row in rows]
        
    def analyze_timeframe_performance(self) -> List[Dict[str, Any]]:
        """
        Compare performance between 1D and 4H timeframes
        
        Returns:
            List of timeframe performance comparison
        """
        query = """
        SELECT 
            timeframe,
            COUNT(*) as total_signals,
            SUM(CASE WHEN is_closed = 1 THEN 1 ELSE 0 END) as closed_trades,
            ROUND(
                100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / 
                NULLIF(SUM(CASE WHEN is_closed = 1 THEN 1 ELSE 0 END), 0),
                2
            ) as win_rate,
            ROUND(AVG(CASE WHEN is_closed = 1 THEN profit_loss_pct END), 2) as avg_pnl,
            ROUND(SUM(CASE WHEN is_closed = 1 THEN profit_loss_pct ELSE 0 END), 2) as total_pnl,
            ROUND(AVG(CASE WHEN is_closed = 1 THEN holding_days END), 2) as avg_holding_days
        FROM signals
        GROUP BY timeframe
        ORDER BY total_pnl DESC
        """
        
        rows = self.db.execute_query(query)
        return [dict(row) for row in rows]
        
    def get_monthly_performance_trend(self) -> List[Dict[str, Any]]:
        """
        Get monthly performance trend to identify seasonal patterns
        
        Returns:
            List of monthly performance data
        """
        query = """
        SELECT 
            strftime('%Y-%m', datetime(timestamp, 'unixepoch')) as month,
            COUNT(*) as total_signals,
            SUM(CASE WHEN is_closed = 1 THEN 1 ELSE 0 END) as closed_trades,
            ROUND(
                100.0 * SUM(CASE WHEN profit_loss_pct > 0 THEN 1 ELSE 0 END) / 
                NULLIF(SUM(CASE WHEN is_closed = 1 THEN 1 ELSE 0 END), 0),
                2
            ) as win_rate,
            ROUND(AVG(CASE WHEN is_closed = 1 THEN profit_loss_pct END), 2) as avg_pnl,
            ROUND(SUM(CASE WHEN is_closed = 1 THEN profit_loss_pct ELSE 0 END), 2) as total_pnl
        FROM signals
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
        """
        
        rows = self.db.execute_query(query)
        return [dict(row) for row in rows]
        
    def generate_optimization_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report
        
        Returns:
            Dictionary with all optimization insights
        """
        return {
            'best_strategies': self.find_best_strategies(min_trades=5, min_win_rate=50),
            'worst_strategies': self.find_worst_strategies(min_trades=5),
            'indicator_importance': self.analyze_indicator_importance(),
            'optimal_holding_period': self.find_optimal_holding_period(),
            'confidence_accuracy': self.analyze_confidence_accuracy(),
            'best_entry_conditions': self.find_best_entry_conditions(min_trades=3),
            'timeframe_comparison': self.analyze_timeframe_performance(),
            'monthly_trend': self.get_monthly_performance_trend()
        }
        
    def print_optimization_report(self):
        """Print formatted optimization report"""
        report = self.generate_optimization_report()
        
        print("\n" + "="*70)
        print("STRATEGY OPTIMIZATION REPORT")
        print("="*70)
        
        # Best Strategies
        print("\n📈 TOP PERFORMING STRATEGIES:")
        print("-" * 70)
        for strat in report['best_strategies'][:5]:
            print(f"\n{strat['strategy_name']} ({strat['signal_type']})")
            print(f"  Trades: {strat['closed_positions']} | Win Rate: {strat['win_rate_pct']}%")
            print(f"  Avg P&L: {strat['avg_pnl_pct']}% | Total P&L: {strat['total_pnl_pct']}%")
        
        # Indicator Importance
        print("\n\n🔬 INDICATOR IMPORTANCE ANALYSIS:")
        print("-" * 70)
        
        for indicator_name, data in report['indicator_importance'].items():
            if data:
                print(f"\n{indicator_name.upper()}:")
                for item in data:
                    value = item.get(indicator_name) or item.get(f'{indicator_name}_signal') or item.get(f'{indicator_name}_trend')
                    print(f"  {value}: {item['trades']} trades | "
                          f"Win Rate: {item['win_rate']}% | Avg P&L: {item['avg_pnl']}%")
        
        # Optimal Holding Period
        print("\n\n⏱️  OPTIMAL HOLDING PERIOD:")
        print("-" * 70)
        for period in report['optimal_holding_period']:
            print(f"{period['holding_period']}: {period['trades']} trades | "
                  f"Win Rate: {period['win_rate']}% | Avg P&L: {period['avg_pnl']}%")
        
        # Confidence Accuracy
        print("\n\n🎯 CONFIDENCE vs ACTUAL PERFORMANCE:")
        print("-" * 70)
        for conf in report['confidence_accuracy']:
            print(f"{conf['confidence_range']}: {conf['trades']} trades | "
                  f"Win Rate: {conf['win_rate']}% | Avg P&L: {conf['avg_pnl']}%")
        
        # Entry Conditions
        print("\n\n🎪 BEST ENTRY CONDITIONS (Bollinger Bands):")
        print("-" * 70)
        for entry in report['best_entry_conditions']:
            print(f"{entry['bb_entry_zone']}: {entry['trades']} trades | "
                  f"Win Rate: {entry['win_rate']}% | Avg P&L: {entry['avg_pnl']}%")
        
        # Timeframe Comparison
        print("\n\n📊 TIMEFRAME COMPARISON:")
        print("-" * 70)
        for tf in report['timeframe_comparison']:
            print(f"{tf['timeframe']}: {tf['closed_trades']} trades | "
                  f"Win Rate: {tf['win_rate']}% | Total P&L: {tf['total_pnl']}%")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    from database.db_manager import TradingDatabase
    
    # Connect to database
    db = TradingDatabase()
    db.connect()
    
    # Create analyzer
    analyzer = StrategyAnalyzer(db)
    
    # Generate and print report
    analyzer.print_optimization_report()
    
    db.disconnect()
