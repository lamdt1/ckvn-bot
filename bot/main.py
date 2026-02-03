"""
Main Trading Bot
Orchestrates all components for automated signal generation
"""

import sys
import os
# Add parent directory to path (works in both local and Docker)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime
from typing import List, Dict
import time

from bot.config import BotConfig
from bot.data_fetcher import DataFetcher
from bot.signal_generator import SignalGenerator
from bot.position_manager import PositionManager
from bot.notification import NotificationManager
from bot.portfolio_tracker import PortfolioTracker
from strategies.signal import Signal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingBot:
    """
    Main trading bot orchestrator
    
    Workflow:
    1. Fetch price data for all symbols
    2. Generate trading signals
    3. Update open positions
    4. Check stop-loss / take-profit
    5. Send notifications
    """
    
    def __init__(self, config: BotConfig = None):
        """
        Initialize trading bot
        
        Args:
            config: Bot configuration (uses BotConfig if None)
        """
        self.config = config or BotConfig
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration")
        
        # Initialize components
        logger.info("🤖 Initializing Trading Bot...")
        
        self.data_fetcher = DataFetcher(source=self.config.DATA_SOURCE)
        self.signal_generator = SignalGenerator(
            total_capital=self.config.TOTAL_CAPITAL,
            min_confidence=self.config.MIN_CONFIDENCE_SCORE,
            db_path=str(self.config.DATABASE_PATH),
            enable_learning=self.config.ENABLE_LEARNING,
            min_trades_for_filter=self.config.MIN_TRADES_FOR_FILTER,
            min_win_rate=self.config.MIN_WIN_RATE,
            cooldown_days=self.config.COOLDOWN_DAYS
        )
        self.position_manager = PositionManager(
            db_path=str(self.config.DATABASE_PATH)
        )
        
        # Initialize notification manager
        self.notification_manager = None
        if self.config.TELEGRAM_ENABLED or self.config.ZALO_ENABLED:
            self.notification_manager = NotificationManager(
                telegram_token=self.config.TELEGRAM_TOKEN if self.config.TELEGRAM_ENABLED else None,
                telegram_chat_id=self.config.TELEGRAM_CHAT_ID if self.config.TELEGRAM_ENABLED else None,
                zalo_token=self.config.ZALO_TOKEN if self.config.ZALO_ENABLED else None,
                zalo_chat_id=self.config.ZALO_CHAT_ID if self.config.ZALO_ENABLED else None
            )
            
            enabled_channels = []
            if self.config.TELEGRAM_ENABLED:
                enabled_channels.append("Telegram")
            if self.config.ZALO_ENABLED:
                enabled_channels.append("Zalo")
            
            logger.info(f"✅ Notifications enabled: {', '.join(enabled_channels)}")
        else:
            logger.info("⏸️ All notifications disabled")
        
        # Initialize portfolio tracker
        self.portfolio_tracker = None
        if self.config.ENABLE_PORTFOLIO_TRACKING:
            try:
                self.portfolio_tracker = PortfolioTracker(
                    portfolio_path=self.config.PORTFOLIO_PATH,
                    alert_threshold_pct=self.config.PORTFOLIO_ALERT_THRESHOLD
                )
                logger.info("✅ Portfolio tracking enabled")
            except Exception as e:
                logger.warning(f"⚠️ Portfolio tracking disabled: {e}")
                self.portfolio_tracker = None
        else:
            logger.info("⏸️ Portfolio tracking disabled")
        
        logger.info("✅ Trading Bot initialized")
        self.config.print_config()
    
    def fetch_data(self) -> Dict[str, any]:
        """
        Fetch price data for all symbols
        
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        logger.info(f"\n📊 Fetching data for {len(self.config.SYMBOLS)} symbols...")
        
        data_dict = self.data_fetcher.fetch_multiple_symbols(
            symbols=self.config.SYMBOLS,
            timeframe=self.config.TIMEFRAMES[0],
            limit=250
        )
        
        return data_dict
    
    def generate_signals(self, data_dict: Dict) -> List[Signal]:
        """
        Generate trading signals
        
        Args:
            data_dict: Dictionary mapping symbol to DataFrame
            
        Returns:
            List of generated signals
        """
        logger.info("\n🎯 Generating signals...")
        
        signals = self.signal_generator.generate_signals_batch(
            data_dict=data_dict,
            timeframe=self.config.TIMEFRAMES[0],
            save_to_db=True
        )
        
        return signals
    
    def update_positions(self, data_dict: Dict):
        """
        Update open positions with current prices
        
        Args:
            data_dict: Dictionary mapping symbol to DataFrame
        """
        logger.info("\n💼 Updating open positions...")
        
        # Load open positions
        self.position_manager.load_open_positions()
        
        if not self.position_manager.positions:
            logger.info("  No open positions")
            return
        
        # Get current prices
        current_prices = {}
        for symbol, df in data_dict.items():
            if not df.empty:
                current_prices[symbol] = float(df['close'].iloc[-1])
        
        # Update positions
        self.position_manager.update_positions(current_prices)
        
        # Print positions
        self.position_manager.print_positions()
        
        # Check for triggers
        to_close = self.position_manager.check_positions()
        
        if to_close:
            logger.info(f"\n⚠️ {len(to_close)} positions triggered:")
            for item in to_close:
                pos = item['position']
                reason = item['reason']
                logger.info(f"  - {pos.symbol}: {reason}")
                
                # Close position
                self.position_manager.close_position(
                    symbol=pos.symbol,
                    close_price=pos.current_price,
                    reason=reason
                )
                
                # Send notification
                if self.notification_manager:
                    action = "STOP_LOSS" if "STOP" in reason else "TAKE_PROFIT"
                    self.notification_manager.send_position_alert(
                        symbol=pos.symbol,
                        action=action,
                        price=pos.current_price,
                        profit_loss_pct=pos.unrealized_pnl_pct,
                        reason=reason
                    )
    
    def _get_daily_stats(self, signals: List[Signal]) -> dict:
        """Calculate daily statistics for summary report"""
        # Count signals by type
        by_type = {}
        for signal in signals:
            signal_type = signal.signal_type.value
            by_type[signal_type] = by_type.get(signal_type, 0) + 1
        
        # Get position stats
        total_pnl, total_pnl_pct = self.position_manager.get_total_pnl()
        
        # Get closed positions today (from database)
        # Simplified - in production, query database for today's closed positions
        closed_today = 0
        wins_today = 0
        losses_today = 0
        
        return {
            'signals_generated': len(signals),
            'strong_buy': by_type.get('STRONG_BUY', 0),
            'weak_buy': by_type.get('WEAK_BUY', 0),
            'watch': by_type.get('WATCH', 0),
            'open_positions': len(self.position_manager.positions),
            'total_pnl_pct': total_pnl_pct,
            'closed_today': closed_today,
            'wins_today': wins_today,
            'losses_today': losses_today
        }
    
    def track_portfolio(self):
        """
        Track portfolio performance and send update
        
        Returns:
            Portfolio summary dict or None
        """
        if not self.portfolio_tracker:
            logger.debug("Portfolio tracking disabled")
            return None
        
        try:
            logger.info("\n📊 Tracking portfolio...")
            
            # Get symbols from portfolio
            symbols = self.portfolio_tracker.get_symbols()
            
            if not symbols:
                logger.warning("⚠️ No symbols in portfolio")
                return None
            
            logger.info(f"Fetching prices for {len(symbols)} symbols...")
            
            # Fetch current prices
            prices = {}
            for symbol in symbols:
                try:
                    df = self.data_fetcher.fetch_historical_data(
                        symbol=symbol,
                        timeframe=self.config.TIMEFRAMES[0],
                        limit=1
                    )
                    
                    if df is not None and not df.empty:
                        prices[symbol] = float(df['close'].iloc[-1])
                        logger.debug(f"  {symbol}: {prices[symbol]:,.0f} VND")
                    else:
                        logger.warning(f"  ⚠️ No data for {symbol}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Error fetching {symbol}: {e}")
            
            if not prices:
                logger.warning("❌ No prices fetched")
                return None
            
            # Calculate portfolio
            summary = self.portfolio_tracker.calculate_portfolio(prices)
            
            # Log summary
            logger.info(f"\n💰 Portfolio Summary:")
            logger.info(f"  Total Value: {summary['total_value']:,.0f} VND")
            logger.info(f"  Total P&L: {summary['total_pnl']:+,.0f} VND ({summary['total_pnl_pct']:+.2f}%)")
            logger.info(f"  Positions: {summary['num_positions']} (Profit: {summary['num_profit']}, Loss: {summary['num_loss']})")
            
            # Get alerts
            alerts = self.portfolio_tracker.get_alerts(summary)
            if alerts:
                logger.info(f"\n⚠️ {len(alerts)} alerts:")
                for alert in alerts:
                    logger.info(f"  {alert['message']}")
            
            # Send notification
            if self.notification_manager:
                # Send summary
                summary_text = self.portfolio_tracker.format_summary(summary)
                self.notification_manager.send_message(summary_text)
                
                # Send detailed positions if requested
                # detailed_text = self.portfolio_tracker.format_detailed_positions(summary)
                # self.notification_manager.send_message(detailed_text)
                
                logger.info("✅ Portfolio update sent")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error tracking portfolio: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_once(self):
        """Run bot workflow once"""
        logger.info("\n" + "="*80)
        logger.info(f"🤖 TRADING BOT RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        try:
            # Step 1: Fetch data
            data_dict = self.fetch_data()
            
            if not data_dict:
                logger.warning("❌ No data fetched, skipping run")
                return
            
            # Step 2: Update positions
            self.update_positions(data_dict)
            
            # Step 3: Generate new signals
            signals = self.generate_signals(data_dict)
            
            # Step 4: Print summary
            self.signal_generator.print_signal_summary(signals)
            
            # Step 5: Send notifications (if enabled)
            if self.notification_manager and signals:
                logger.info("\n📤 Sending Telegram notifications...")
                
                # Filter actionable signals (BUY signals only)
                actionable_signals = [s for s in signals if s.is_actionable()]
                
                if actionable_signals:
                    # Send batch alerts
                    self.notification_manager.send_batch_alerts(actionable_signals)
                    logger.info(f"✅ Sent {len(actionable_signals)} signal alerts")
                else:
                    logger.info("  No actionable signals to send")
                
                # Send daily summary
                stats = self._get_daily_stats(signals)
                self.notification_manager.send_daily_summary(stats)
                logger.info("✅ Sent daily summary")
            
            # Step 6: Track portfolio (if enabled)
            if self.portfolio_tracker:
                self.track_portfolio()
            
            logger.info("\n✅ Bot run completed successfully")
            
        except Exception as e:
            logger.error(f"\n❌ Error during bot run: {e}")
            import traceback
            traceback.print_exc()
    
    def run_continuous(self, interval_minutes: int = None):
        """
        Run bot continuously at specified interval
        
        Args:
            interval_minutes: Run interval in minutes (uses config if None)
        """
        interval = interval_minutes or self.config.RUN_INTERVAL_MINUTES
        
        logger.info(f"\n🔄 Starting continuous mode (interval: {interval} minutes)")
        logger.info("   Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_once()
                
                logger.info(f"\n⏸️ Waiting {interval} minutes until next run...")
                time.sleep(interval * 60)
                
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Bot stopped by user")
    
    def run_scheduled(self, run_time: str = None):
        """
        Run bot at scheduled time daily
        
        Args:
            run_time: Time to run (HH:MM format, uses config if None)
        """
        try:
            import schedule
        except ImportError:
            logger.error("schedule library not installed. Install with: pip install schedule")
            return
        
        run_time = run_time or self.config.RUN_TIME
        
        logger.info(f"\n⏰ Scheduling bot to run daily at {run_time}")
        logger.info("   Press Ctrl+C to stop")
        
        # Schedule job
        schedule.every().day.at(run_time).do(self.run_once)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Bot stopped by user")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Bot')
    parser.add_argument('--mode', choices=['once', 'continuous', 'scheduled'],
                       default='once', help='Run mode')
    parser.add_argument('--interval', type=int, help='Interval in minutes (for continuous mode)')
    parser.add_argument('--time', type=str, help='Run time HH:MM (for scheduled mode)')
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = TradingBot()
    
    # Run based on mode
    if args.mode == 'once':
        bot.run_once()
    elif args.mode == 'continuous':
        bot.run_continuous(interval_minutes=args.interval)
    elif args.mode == 'scheduled':
        bot.run_scheduled(run_time=args.time)


if __name__ == "__main__":
    main()
