"""
Backtesting Framework
Simulate trading on historical data to collect clean performance data
"""

import sys
sys.path.insert(0, '/Volumes/Data/projects/ckbot')

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from indicators.calculator import IndicatorCalculator
from strategies.pro_trader_strategy import ProTraderStrategy
from strategies.signal import Signal, SignalType
from database.db_manager import TradingDatabase

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Backtesting engine for Pro Trader strategy
    
    Features:
    - Simulate trades on historical data
    - Track performance (win rate, profit/loss, etc.)
    - Generate clean training data
    - Validate indicator logic
    """
    
    def __init__(self,
                 initial_capital: float = 100_000_000,
                 db_path: str = 'database/trading.db'):
        """
        Initialize backtest engine
        
        Args:
            initial_capital: Starting capital (VND)
            db_path: Database path
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.db = TradingDatabase(db_path=db_path)
        
        # Components
        self.indicator_calculator = IndicatorCalculator()
        self.strategy = ProTraderStrategy()
        
        # Tracking
        self.trades: List[Dict] = []
        self.open_positions: Dict[str, Dict] = {}
        
        logger.info(f"✅ BacktestEngine initialized")
        logger.info(f"   Initial Capital: {initial_capital:,.0f} VND")
    
    def run_backtest(self,
                    data_dict: Dict[str, pd.DataFrame],
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            data_dict: Dictionary mapping symbol to DataFrame
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Backtest results
        """
        logger.info("\n" + "="*80)
        logger.info("🔬 STARTING BACKTEST")
        logger.info("="*80)
        
        # Filter by date if specified
        if start_date or end_date:
            data_dict = self._filter_by_date(data_dict, start_date, end_date)
        
        # Get all unique timestamps across all symbols
        all_timestamps = self._get_all_timestamps(data_dict)
        
        logger.info(f"\n📊 Backtest Parameters:")
        logger.info(f"   Symbols: {len(data_dict)}")
        logger.info(f"   Timepoints: {len(all_timestamps)}")
        logger.info(f"   Date Range: {self._format_timestamp(all_timestamps[0])} → {self._format_timestamp(all_timestamps[-1])}")
        
        # Simulate trading day by day
        for i, timestamp in enumerate(all_timestamps):
            if i % 30 == 0:  # Progress every 30 days
                logger.info(f"\n📅 Processing {self._format_timestamp(timestamp)} ({i}/{len(all_timestamps)})")
            
            # Check open positions (stop-loss / take-profit)
            self._check_positions(data_dict, timestamp)
            
            # Generate signals for this timestamp
            self._generate_signals(data_dict, timestamp)
        
        # Close remaining positions
        self._close_all_positions(data_dict, all_timestamps[-1])
        
        # Calculate results
        results = self._calculate_results()
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _filter_by_date(self, data_dict: Dict, start_date: Optional[str], end_date: Optional[str]) -> Dict:
        """Filter data by date range"""
        filtered = {}
        
        for symbol, df in data_dict.items():
            df_copy = df.copy()
            
            if start_date:
                start_ts = int(pd.Timestamp(start_date).timestamp())
                df_copy = df_copy[df_copy['timestamp'] >= start_ts]
            
            if end_date:
                end_ts = int(pd.Timestamp(end_date).timestamp())
                df_copy = df_copy[df_copy['timestamp'] <= end_ts]
            
            if not df_copy.empty:
                filtered[symbol] = df_copy
        
        return filtered
    
    def _get_all_timestamps(self, data_dict: Dict) -> List[int]:
        """Get all unique timestamps sorted"""
        all_ts = set()
        
        for df in data_dict.values():
            all_ts.update(df['timestamp'].tolist())
        
        return sorted(list(all_ts))
    
    def _generate_signals(self, data_dict: Dict, timestamp: int):
        """Generate signals for all symbols at given timestamp"""
        for symbol, df in data_dict.items():
            # Get data up to this timestamp
            historical_data = df[df['timestamp'] <= timestamp]
            
            if len(historical_data) < 250:
                continue  # Not enough data
            
            # Get current price
            current_row = historical_data[historical_data['timestamp'] == timestamp]
            if current_row.empty:
                continue
            
            current_price = float(current_row['close'].iloc[0])
            
            # Skip if already have position
            if symbol in self.open_positions:
                continue
            
            # Calculate indicators
            try:
                indicators = self.indicator_calculator.calculate_for_signal(historical_data)
            except Exception as e:
                logger.debug(f"Error calculating indicators for {symbol}: {e}")
                continue
            
            # Generate signal
            signal = self.strategy.generate_signal(
                symbol=symbol,
                timeframe='1D',
                timestamp=timestamp,
                price=current_price,
                indicators=indicators,
                total_capital=self.current_capital
            )
            
            # Execute if buy signal
            if signal.is_buy_signal() and signal.confidence_score >= 60:
                self._execute_buy(signal, timestamp)
    
    def _execute_buy(self, signal: Signal, timestamp: int):
        """Execute buy order"""
        # Calculate position size (in VND)
        position_value = self.current_capital * (signal.position_size_pct / 100)
        
        # Calculate quantity (simplified - assume can buy fractional shares)
        quantity = position_value / signal.price
        
        # Open position
        self.open_positions[signal.symbol] = {
            'signal': signal,
            'entry_timestamp': timestamp,
            'entry_price': signal.price,
            'quantity': quantity,
            'position_value': position_value,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit
        }
        
        # Reduce capital
        self.current_capital -= position_value
        
        logger.debug(f"✅ BUY {signal.symbol} @ {signal.price:,.0f} (confidence: {signal.confidence_score}%)")
    
    def _check_positions(self, data_dict: Dict, timestamp: int):
        """Check open positions for stop-loss / take-profit"""
        symbols_to_close = []
        
        for symbol, position in self.open_positions.items():
            if symbol not in data_dict:
                continue
            
            df = data_dict[symbol]
            current_row = df[df['timestamp'] == timestamp]
            
            if current_row.empty:
                continue
            
            current_price = float(current_row['close'].iloc[0])
            
            # Check stop-loss
            if current_price <= position['stop_loss']:
                self._close_position(symbol, current_price, timestamp, 'STOP_LOSS')
                symbols_to_close.append(symbol)
            
            # Check take-profit
            elif current_price >= position['take_profit']:
                self._close_position(symbol, current_price, timestamp, 'TAKE_PROFIT')
                symbols_to_close.append(symbol)
        
        # Remove closed positions
        for symbol in symbols_to_close:
            del self.open_positions[symbol]
    
    def _close_position(self, symbol: str, exit_price: float, exit_timestamp: int, reason: str):
        """Close position"""
        position = self.open_positions[symbol]
        
        # Calculate P&L
        entry_price = position['entry_price']
        quantity = position['quantity']
        
        profit_loss = (exit_price - entry_price) * quantity
        profit_loss_pct = ((exit_price - entry_price) / entry_price) * 100
        
        # Calculate holding days
        holding_days = (exit_timestamp - position['entry_timestamp']) / (24 * 3600)
        
        # Return capital + profit/loss
        self.current_capital += position['position_value'] + profit_loss
        
        # Record trade
        trade = {
            'symbol': symbol,
            'entry_timestamp': position['entry_timestamp'],
            'entry_price': entry_price,
            'exit_timestamp': exit_timestamp,
            'exit_price': exit_price,
            'quantity': quantity,
            'profit_loss': profit_loss,
            'profit_loss_pct': profit_loss_pct,
            'holding_days': holding_days,
            'reason': reason,
            'signal': position['signal']
        }
        
        self.trades.append(trade)
        
        logger.debug(f"❌ SELL {symbol} @ {exit_price:,.0f} ({profit_loss_pct:+.2f}%) - {reason}")
    
    def _close_all_positions(self, data_dict: Dict, final_timestamp: int):
        """Close all remaining positions at end of backtest"""
        for symbol in list(self.open_positions.keys()):
            df = data_dict[symbol]
            final_row = df[df['timestamp'] == final_timestamp]
            
            if not final_row.empty:
                final_price = float(final_row['close'].iloc[0])
                self._close_position(symbol, final_price, final_timestamp, 'BACKTEST_END')
        
        self.open_positions.clear()
    
    def _calculate_results(self) -> Dict:
        """Calculate backtest results"""
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'total_return_pct': 0
            }
        
        # Basic stats
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['profit_loss'] > 0]
        losing_trades = [t for t in self.trades if t['profit_loss'] <= 0]
        
        win_rate = len(winning_trades) / total_trades * 100
        
        # Returns
        total_return = self.current_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # Average metrics
        avg_profit = sum(t['profit_loss_pct'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['profit_loss_pct'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        avg_holding = sum(t['holding_days'] for t in self.trades) / total_trades
        
        # Max drawdown (simplified)
        max_loss = min([t['profit_loss_pct'] for t in self.trades], default=0)
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'avg_profit_pct': avg_profit,
            'avg_loss_pct': avg_loss,
            'avg_holding_days': avg_holding,
            'max_loss_pct': max_loss,
            'final_capital': self.current_capital
        }
    
    def _print_summary(self, results: Dict):
        """Print backtest summary"""
        print("\n" + "="*80)
        print("📊 BACKTEST RESULTS")
        print("="*80)
        
        print(f"\n💰 CAPITAL:")
        print(f"   Initial: {self.initial_capital:,.0f} VND")
        print(f"   Final: {results['final_capital']:,.0f} VND")
        print(f"   Return: {results['total_return']:+,.0f} VND ({results['total_return_pct']:+.2f}%)")
        
        print(f"\n📈 TRADES:")
        print(f"   Total: {results['total_trades']}")
        print(f"   Wins: {results['winning_trades']} ({results['win_rate']:.1f}%)")
        print(f"   Losses: {results['losing_trades']}")
        
        print(f"\n📊 PERFORMANCE:")
        print(f"   Avg Profit: {results['avg_profit_pct']:+.2f}%")
        print(f"   Avg Loss: {results['avg_loss_pct']:+.2f}%")
        print(f"   Avg Holding: {results['avg_holding_days']:.1f} days")
        print(f"   Max Loss: {results['max_loss_pct']:.2f}%")
        
        print("\n" + "="*80)
    
    def save_trades_to_db(self):
        """Save backtest trades to database"""
        logger.info("\n💾 Saving trades to database...")
        
        self.db.connect()
        
        for trade in self.trades:
            signal = trade['signal']
            
            # Save signal
            signal_data = signal.to_dict()
            signal_data['is_executed'] = 1
            signal_data['execution_price'] = trade['entry_price']
            signal_data['is_closed'] = 1
            signal_data['close_price'] = trade['exit_price']
            signal_data['close_timestamp'] = trade['exit_timestamp']
            signal_data['profit_loss_pct'] = trade['profit_loss_pct']
            signal_data['holding_days'] = int(trade['holding_days'])
            
            self.db.create_signal(signal_data)
        
        self.db.disconnect()
        
        logger.info(f"✅ Saved {len(self.trades)} trades to database")
    
    def _format_timestamp(self, timestamp: int) -> str:
        """Format timestamp to readable date"""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    
    def export_trades_to_csv(self, filepath: str = 'backtest_trades.csv'):
        """Export trades to CSV for analysis"""
        if not self.trades:
            logger.warning("No trades to export")
            return
        
        # Convert to DataFrame
        trades_data = []
        for trade in self.trades:
            trades_data.append({
                'symbol': trade['symbol'],
                'entry_date': self._format_timestamp(trade['entry_timestamp']),
                'entry_price': trade['entry_price'],
                'exit_date': self._format_timestamp(trade['exit_timestamp']),
                'exit_price': trade['exit_price'],
                'profit_loss_pct': trade['profit_loss_pct'],
                'holding_days': trade['holding_days'],
                'reason': trade['reason'],
                'confidence': trade['signal'].confidence_score
            })
        
        df = pd.DataFrame(trades_data)
        df.to_csv(filepath, index=False)
        
        logger.info(f"✅ Exported trades to {filepath}")


if __name__ == "__main__":
    # Example usage will be in separate test file
    print("Backtesting framework ready!")
