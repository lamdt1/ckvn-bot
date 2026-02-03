"""
Portfolio Tracker
Track personal portfolio performance and send updates
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class PortfolioTracker:
    """
    Track portfolio performance
    
    Features:
    - Load portfolio from JSON
    - Fetch current prices
    - Calculate P&L
    - Generate portfolio summary
    - Alert on significant changes
    """
    
    def __init__(self, 
                 portfolio_path: str = 'portfolio.json',
                 alert_threshold_pct: float = 5.0):
        """
        Initialize portfolio tracker
        
        Args:
            portfolio_path: Path to portfolio.json
            alert_threshold_pct: Alert if P&L changes > this %
        """
        self.portfolio_path = portfolio_path
        self.alert_threshold = alert_threshold_pct
        self.portfolio = {}
        
        self._load_portfolio()
        logger.info(f"✅ Portfolio tracker initialized ({len(self.portfolio)} symbols)")
    
    def _load_portfolio(self):
        """Load portfolio from JSON file"""
        try:
            with open(self.portfolio_path, 'r', encoding='utf-8') as f:
                self.portfolio = json.load(f)
            
            logger.info(f"📁 Loaded portfolio: {list(self.portfolio.keys())}")
            
        except FileNotFoundError:
            logger.warning(f"⚠️ Portfolio file not found: {self.portfolio_path}")
            self.portfolio = {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in portfolio file: {e}")
            self.portfolio = {}
    
    def get_symbols(self) -> List[str]:
        """Get list of symbols in portfolio"""
        return list(self.portfolio.keys())
    
    def calculate_position(self, symbol: str, current_price: float) -> Optional[Dict]:
        """
        Calculate position P&L
        
        Args:
            symbol: Stock symbol
            current_price: Current market price
            
        Returns:
            Dictionary with position details
        """
        if symbol not in self.portfolio:
            return None
        
        position = self.portfolio[symbol]
        avg_price = position.get('avg_price', 0)
        quantity = position.get('quantity', 0)
        
        if quantity == 0:
            # Watch-only position
            return None
            
        if avg_price == 0:
            return None
        
        # Calculate P&L
        total_cost = avg_price * quantity
        current_value = current_price * quantity
        profit_loss = current_value - total_cost
        profit_loss_pct = (profit_loss / total_cost) * 100
        
        return {
            'symbol': symbol,
            'avg_price': avg_price,
            'current_price': current_price,
            'quantity': quantity,
            'total_cost': total_cost,
            'current_value': current_value,
            'profit_loss': profit_loss,
            'profit_loss_pct': profit_loss_pct,
            'status': self._get_status(profit_loss_pct)
        }
    
    def _get_status(self, pnl_pct: float) -> str:
        """Get position status based on P&L"""
        if pnl_pct >= 15:
            return '🚀 STRONG PROFIT'
        elif pnl_pct >= 10:
            return '✅ TAKE PROFIT'
        elif pnl_pct >= 5:
            return '📈 GOOD PROFIT'
        elif pnl_pct >= 0:
            return '💚 PROFIT'
        elif pnl_pct >= -5:
            return '⚠️ SMALL LOSS'
        elif pnl_pct >= -7:
            return '🔴 LOSS'
        else:
            return '🚨 CUT LOSS'
    
    def calculate_portfolio(self, prices: Dict[str, float]) -> Dict:
        """
        Calculate entire portfolio P&L
        
        Args:
            prices: Dictionary mapping symbol to current price
            
        Returns:
            Portfolio summary
        """
        positions = []
        total_cost = 0
        total_value = 0
        total_pnl = 0
        
        for symbol in self.portfolio.keys():
            if symbol not in prices:
                logger.warning(f"⚠️ No price data for {symbol}")
                continue
            
            position = self.calculate_position(symbol, prices[symbol])
            if position:
                positions.append(position)
                total_cost += position['total_cost']
                total_value += position['current_value']
                total_pnl += position['profit_loss']
        
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # Sort by P&L %
        positions.sort(key=lambda x: x['profit_loss_pct'], reverse=True)
        
        return {
            'timestamp': datetime.now(),
            'positions': positions,
            'total_cost': total_cost,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'num_positions': len(positions),
            'num_profit': sum(1 for p in positions if p['profit_loss'] > 0),
            'num_loss': sum(1 for p in positions if p['profit_loss'] < 0)
        }
    
    def get_alerts(self, portfolio_summary: Dict) -> List[Dict]:
        """
        Get alerts for significant changes
        
        Args:
            portfolio_summary: Portfolio summary from calculate_portfolio
            
        Returns:
            List of alerts
        """
        alerts = []
        
        for position in portfolio_summary['positions']:
            pnl_pct = position['profit_loss_pct']
            
            # Take profit alert
            if pnl_pct >= 15:
                alerts.append({
                    'type': 'TAKE_PROFIT',
                    'symbol': position['symbol'],
                    'pnl_pct': pnl_pct,
                    'message': f"🚀 {position['symbol']}: Lời {pnl_pct:.1f}% - Cân nhắc chốt lời!"
                })
            
            # Cut loss alert
            elif pnl_pct <= -7:
                alerts.append({
                    'type': 'CUT_LOSS',
                    'symbol': position['symbol'],
                    'pnl_pct': pnl_pct,
                    'message': f"🚨 {position['symbol']}: Lỗ {pnl_pct:.1f}% - Cân nhắc cắt lỗ!"
                })
        
        return alerts
    
    def format_summary(self, portfolio_summary: Dict) -> str:
        """
        Format portfolio summary for notification
        
        Args:
            portfolio_summary: Portfolio summary
            
        Returns:
            Formatted text
        """
        summary = portfolio_summary
        
        # Header
        text = "📊 PORTFOLIO UPDATE\n"
        text += "=" * 50 + "\n\n"
        
        # Overall stats
        text += f"💰 Tổng quan:\n"
        text += f"  Vốn: {summary['total_cost']:,.0f} VND\n"
        text += f"  Giá trị: {summary['total_value']:,.0f} VND\n"
        text += f"  Lời/Lỗ: {summary['total_pnl']:+,.0f} VND ({summary['total_pnl_pct']:+.2f}%)\n"
        text += f"  Số mã: {summary['num_positions']} "
        text += f"(Lời: {summary['num_profit']}, Lỗ: {summary['num_loss']})\n\n"
        
        # Top performers
        text += "🏆 Top 3 Lời:\n"
        top_profit = [p for p in summary['positions'] if p['profit_loss'] > 0][:3]
        for i, pos in enumerate(top_profit, 1):
            text += f"  {i}. {pos['symbol']}: {pos['profit_loss_pct']:+.1f}% "
            text += f"({pos['profit_loss']:+,.0f} VND)\n"
        
        if not top_profit:
            text += "  (Không có)\n"
        
        text += "\n"
        
        # Worst performers
        text += "📉 Top 3 Lỗ:\n"
        top_loss = [p for p in summary['positions'] if p['profit_loss'] < 0][-3:]
        top_loss.reverse()
        for i, pos in enumerate(top_loss, 1):
            text += f"  {i}. {pos['symbol']}: {pos['profit_loss_pct']:+.1f}% "
            text += f"({pos['profit_loss']:+,.0f} VND)\n"
        
        if not top_loss:
            text += "  (Không có)\n"
        
        text += "\n"
        
        # Alerts
        alerts = self.get_alerts(summary)
        if alerts:
            text += "⚠️ Cảnh báo:\n"
            for alert in alerts:
                text += f"  {alert['message']}\n"
            text += "\n"
        
        # Timestamp
        text += f"🕐 Cập nhật: {summary['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += "=" * 50
        
        return text
    
    def format_detailed_positions(self, portfolio_summary: Dict) -> str:
        """
        Format detailed position list
        
        Args:
            portfolio_summary: Portfolio summary
            
        Returns:
            Formatted text
        """
        text = "📋 CHI TIẾT DANH MỤC\n"
        text += "=" * 50 + "\n\n"
        
        for pos in portfolio_summary['positions']:
            text += f"{pos['status']} {pos['symbol']}\n"
            text += f"  Giá TB: {pos['avg_price']:,.0f} VND\n"
            text += f"  Giá HT: {pos['current_price']:,.0f} VND\n"
            text += f"  SL: {pos['quantity']:,} CP\n"
            text += f"  Vốn: {pos['total_cost']:,.0f} VND\n"
            text += f"  Giá trị: {pos['current_value']:,.0f} VND\n"
            text += f"  L/L: {pos['profit_loss']:+,.0f} VND ({pos['profit_loss_pct']:+.2f}%)\n"
            text += "\n"
        
        return text


if __name__ == "__main__":
    # Test portfolio tracker
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("PORTFOLIO TRACKER TEST")
    print("=" * 70)
    
    # Initialize tracker
    tracker = PortfolioTracker(portfolio_path='portfolio.json')
    
    # Test with sample prices
    sample_prices = {
        'VNM': 85000,
        'VCB': 95000,
        'HPG': 28000,
        'VIC': 42000,
        'VHM': 55000
    }
    
    # Calculate portfolio
    summary = tracker.calculate_portfolio(sample_prices)
    
    # Print summary
    print("\n" + tracker.format_summary(summary))
    
    # Print detailed positions
    print("\n" + tracker.format_detailed_positions(summary))
    
    print("\n✅ Test completed!")
