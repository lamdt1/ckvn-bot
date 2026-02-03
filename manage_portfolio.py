
import argparse
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.transaction_manager import TransactionManager
from bot.config import BotConfig

def main():
    parser = argparse.ArgumentParser(description='Manage Trading Transactions')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add transaction command
    add_parser = subparsers.add_parser('add', help='Add a transaction')
    add_parser.add_argument('symbol', type=str, help='Stock symbol (e.g., VNM)')
    add_parser.add_argument('type', type=str, choices=['buy', 'sell'], help='Transaction type')
    add_parser.add_argument('quantity', type=int, help='Quantity')
    add_parser.add_argument('price', type=float, help='Price per share')
    add_parser.add_argument('--fees', type=float, default=0, help='Transaction fees')
    add_parser.add_argument('--notes', type=str, default=None, help='Average/Note')

    # List command
    list_parser = subparsers.add_parser('list', help='List transactions')
    list_parser.add_argument('--symbol', type=str, default=None, help='Filter by symbol')

    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Add symbol to watchlist (Qty 0)')
    watch_parser.add_argument('symbol', type=str, help='Stock symbol')
    
    # Unwatch command
    unwatch_parser = subparsers.add_parser('unwatch', help='Remove symbol from portfolio/watchlist')
    unwatch_parser.add_argument('symbol', type=str, help='Stock symbol')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync portfolio.json from history')

    args = parser.parse_args()
    
    mgr = TransactionManager(db_path="database/trading.db")
    
    if args.command == 'add':
        success = mgr.add_transaction(
            symbol=args.symbol,
            type=args.type,
            quantity=args.quantity,
            price=args.price,
            fees=args.fees,
            notes=args.notes
        )
        if success:
            print(f"✅ Successfully added transaction for {args.symbol}")
        else:
            print("❌ Failed to add transaction")
            
    elif args.command == 'watch':
        if mgr.add_watch_symbol(args.symbol):
            print(f"✅ Added {args.symbol} to watchlist")
        else:
            print(f"❌ Failed to add {args.symbol}")
            
    elif args.command == 'unwatch':
        if mgr.remove_watch_symbol(args.symbol):
            print(f"✅ Removed {args.symbol} from portfolio")
        else:
            print(f"❌ Failed to remove {args.symbol}")
            
    elif args.command == 'list':
        txs = mgr.get_transactions(symbol=args.symbol)
        print("\n📊 TRANSACTION HISTORY")
        print("="*80)
        print(f"{'Date':<20} {'Symbol':<8} {'Type':<6} {'Qty':<10} {'Price':<12} {'Total':<15}")
        print("-"*80)
        
        for tx in txs:
            date_str = datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M')
            total = tx['quantity'] * tx['price']
            print(f"{date_str:<20} {tx['symbol']:<8} {tx['type']:<6} {tx['quantity']:<10,d} {tx['price']:<12,.0f} {total:<15,.0f}")
        print("="*80)
        
    elif args.command == 'sync':
        mgr.recalculate_portfolio_json()
        print("✅ Synced portfolio.json from transaction history")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
