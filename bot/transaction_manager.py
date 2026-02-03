"""
Transaction Manager
Manages actual transaction history and provides alerts based on user's real positions
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import TradingDatabase

logger = logging.getLogger(__name__)

class TransactionManager:
    """
    Manages actual transaction history
    """
    
    def __init__(self, db_path: str = 'database/trading.db'):
        """
        Initialize transaction manager
        
        Args:
            db_path: Path to database
        """
        self.db = TradingDatabase(db_path=db_path)
    
    def add_transaction(self, symbol: str, type: str, quantity: int, price: float,
                       fees: float = 0, notes: str = None) -> bool:
        """
        Add a new transaction
        
        Args:
            symbol: Stock symbol (e.g., 'VNM')
            type: 'BUY' or 'SELL'
            quantity: Number of shares
            price: Price per share
            fees: Total transaction fees
            notes: Optional notes
            
        Returns:
            Success status
        """
        try:
            timestamp = int(datetime.now().timestamp())
            
            query = """
            INSERT INTO transactions 
            (symbol, type, quantity, price, fees, timestamp, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute_update(query, (
                symbol.upper(), type.upper(), quantity, price, fees, timestamp, notes
            ))
            
            logger.info(f"✅ Added transaction: {type} {quantity} {symbol} @ {price:,.0f}")
            
            # Auto-update portfolio.json if PortfolioTracker exists? 
            # Ideally we recalculate portfolio state here
            self.recalculate_portfolio_json()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding transaction: {e}")
            return False
    
    def get_transactions(self, symbol: str = None) -> List[Dict]:
        """Get transaction history"""
        query = "SELECT * FROM transactions"
        params = ()
        
        if symbol:
            query += " WHERE symbol = ?"
            params = (symbol.upper(),)
            
        query += " ORDER BY timestamp DESC"
        
        rows = self.db.execute_query(query, params)
        return [dict(row) for row in rows]
    
    def calculate_portfolio_state(self) -> Dict[str, Dict]:
        """
        Calculate current portfolio state from transaction history
        
        Returns:
            Dict mapping symbol to {avg_price, quantity}
        """
        transactions = self.db.execute_query("SELECT * FROM transactions ORDER BY timestamp ASC")
        
        portfolio = {}
        
        for tx in transactions:
            symbol = tx['symbol']
            qty = tx['quantity']
            price = tx['price']
            type = tx['type']
            
            if symbol not in portfolio:
                portfolio[symbol] = {'quantity': 0, 'total_cost': 0, 'avg_price': 0}
            
            if type == 'BUY':
                # Weighted average price
                current_qty = portfolio[symbol]['quantity']
                current_cost = portfolio[symbol]['total_cost']
                
                new_cost = price * qty
                total_cost = current_cost + new_cost
                total_qty = current_qty + qty
                
                portfolio[symbol]['quantity'] = total_qty
                portfolio[symbol]['total_cost'] = total_cost
                portfolio[symbol]['avg_price'] = total_cost / total_qty if total_qty > 0 else 0
                
            elif type == 'SELL':
                # Reduce quantity, keep avg_price same (FIFO/Weighted avg logic simplified)
                current_qty = portfolio[symbol]['quantity']
                # Cost base reduces proportionally
                avg_price = portfolio[symbol]['avg_price']
                
                # Check if selling more than owned (short selling? or data error)
                if qty > current_qty:
                    logger.warning(f"⚠️ Selling more {symbol} than owned: {qty} > {current_qty}")
                    # Allow negative for now or cap at 0? Let's allow negative to show error
                
                remaining_qty = current_qty - qty
                remaining_cost = remaining_qty * avg_price
                
                portfolio[symbol]['quantity'] = remaining_qty
                portfolio[symbol]['total_cost'] = remaining_cost
        
        # Filter out closed positions (qty 0)
        active_portfolio = {
            k: {
                'avg_price': v['avg_price'],
                'quantity': v['quantity'],
                'last_alert': None
            } 
            for k, v in portfolio.items()
        }
        
        return active_portfolio

    def recalculate_portfolio_json(self, filepath: str = 'portfolio.json'):
        """Recalculate and save to portfolio.json, preserving manual watch entries"""
        # 1. Calculate state from transactions (Source of Truth for holdings)
        portfolio_from_txs = self.calculate_portfolio_state()
        
        # 2. Load existing json to get manual watch entries (qty=0)
        existing_portfolio = {}
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_portfolio = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load existing portfolio: {e}")

        # 3. Merge: Start with txs, add manual entries if not present
        final_portfolio = portfolio_from_txs.copy()
        
        for symbol, data in existing_portfolio.items():
            if symbol not in final_portfolio:
                # Keep it as a watch entry (preserve data if needed, or reset to 0)
                # If it was a watch entry (qty=0), keep it.
                # If it had qty but no txs supporting it... we assume sync wipes it?
                # User request implies they want to "add" without editing json.
                # So we respect existing keys not in txs.
                final_portfolio[symbol] = data
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(final_portfolio, f, indent=4)
            logger.info("✅ Updated portfolio.json (synced with transactions)")
        except Exception as e:
            logger.error(f"❌ Error updating portfolio.json: {e}")

    def add_watch_symbol(self, symbol: str, filepath: str = 'portfolio.json') -> bool:
        """Add a symbol to watch (0 quantity)"""
        symbol = symbol.upper()
        try:
            portfolio = {}
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    portfolio = json.load(f)
            
            if symbol in portfolio:
                logger.info(f"Symbol {symbol} already in portfolio")
                return True
                
            portfolio[symbol] = {
                "avg_price": 0,
                "quantity": 0,
                "last_alert": None
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(portfolio, f, indent=4)
                
            return True
        except Exception as e:
            logger.error(f"Error adding watch symbol: {e}")
            return False

    def remove_watch_symbol(self, symbol: str, filepath: str = 'portfolio.json') -> bool:
        """Remove a symbol from portfolio"""
        symbol = symbol.upper()
        try:
            portfolio = {}
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    portfolio = json.load(f)
            
            if symbol not in portfolio:
                logger.warning(f"Symbol {symbol} not found in portfolio")
                return False
                
            # If it has > 0 quantity, warn? Or just delete?
            # User expectation: "remove 1 code".
            del portfolio[symbol]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(portfolio, f, indent=4)
                
            return True
        except Exception as e:
            logger.error(f"Error removing symbol: {e}")
            return False

    def check_price_alerts(self, current_prices: Dict[str, float]) -> List[Dict]:
        """
        Check for alerts based on actual transaction history
        Logic: 
        1. Price dropped below last BUY price by X%? (Buy more?)
        2. Price rose above last SELL price (if sold recently)? 
        
        Returns:
            List of alerts
        """
        alerts = []
        
        # Get last transaction for each symbol
        query = """
        SELECT symbol, type, price, timestamp 
        FROM transactions 
        GROUP BY symbol 
        HAVING max(timestamp)
        """
        last_txs = self.db.execute_query(query)
        
        for tx in last_txs:
            symbol = tx['symbol']
            last_price = tx['price']
            type = tx['type']
            
            if symbol not in current_prices:
                continue
                
            current = current_prices[symbol]
            
            # Alert Logic 1: Price dropped below last BUY price (DCA opportunity)
            if type == 'BUY' and current < last_price:
                drop_pct = (last_price - current) / last_price * 100
                if drop_pct >= 5.0: # Configurable threshold?
                    alerts.append({
                        'symbol': symbol,
                        'message': f"📉 {symbol} giá {current:,.0f} thấp hơn {drop_pct:.1f}% so với lần mua gần nhất ({last_price:,.0f}). Cân nhắc mua thêm?",
                        'type': 'PRICE_DROP_BELOW_BUY'
                    })
            
            # Alert Logic 2: Price rose above last SELL price (Regret/Re-entry?)
            elif type == 'SELL' and current > last_price:
                diff_pct = (current - last_price) / last_price * 100
                if diff_pct >= 5.0:
                    alerts.append({
                        'symbol': symbol,
                        'message': f"📈 {symbol} giá {current:,.0f} đã tăng {diff_pct:.1f}% so với lần bán gần nhất ({last_price:,.0f}).",
                        'type': 'PRICE_ABOVE_SELL'
                    })
                    
        return alerts
