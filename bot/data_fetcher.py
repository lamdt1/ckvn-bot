"""
Data Fetcher
Fetches stock price data from various sources (vnstock, SSI API, etc.)
"""

import sys
import pandas as pd
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Fetches stock price data from multiple sources
    
    Supported sources:
    - vnstock: Free, easy to use (recommended for testing)
    - ssi: SSI iBoard API (requires account)
    - csv: Load from CSV files (for backtesting)
    """
    
    def __init__(self, source: str = 'vnstock'):
        """
        Initialize data fetcher
        
        Args:
            source: Data source ('vnstock', 'ssi', 'csv')
        """
        self.source = source.lower()
        self._validate_source()
        
    def _validate_source(self):
        """Validate data source"""
        valid_sources = ['vnstock', 'ssi', 'csv']
        if self.source not in valid_sources:
            raise ValueError(f"Invalid source: {self.source}. Must be one of {valid_sources}")
    
    def fetch_historical_data(self,
                             symbol: str,
                             timeframe: str = '1D',
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             limit: int = 250) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data
        
        Args:
            symbol: Stock symbol (e.g., 'VNM')
            timeframe: Timeframe ('1D', '4H', '1H')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            if self.source == 'vnstock':
                return self._fetch_vnstock(symbol, start_date, end_date, limit)
            elif self.source == 'ssi':
                return self._fetch_ssi(symbol, timeframe, start_date, end_date)
            elif self.source == 'csv':
                return self._fetch_csv(symbol, timeframe)
            else:
                logger.error(f"Unsupported source: {self.source}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _fetch_vnstock(self,
                      symbol: str,
                      start_date: Optional[str],
                      end_date: Optional[str],
                      limit: int) -> Optional[pd.DataFrame]:
        """
        Fetch data from vnstock
        
        Note: vnstock only supports daily data
        """
        try:
            # Try to import vnstock
            try:
                from vnstock import Quote
            except ImportError:
                logger.error("vnstock not installed. Install with: pip install vnstock")
                return None
            
            # Calculate dates if not provided
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            if not start_date:
                # Estimate start date based on limit (including weekends)
                # Multiply by 1.5 to ensure we get enough trading days
                days_back = int(limit * 1.5)
                start = datetime.now() - timedelta(days=days_back)
                start_date = start.strftime('%Y-%m-%d')
            
            logger.info(f"Fetching {symbol} from vnstock ({start_date} to {end_date})...")
            
            # Fetch data using Quote API (vnstock v3)
            quote = Quote(symbol=symbol, source='VCI')
            df = quote.history(start=start_date, end=end_date, resolution='1D')
            
            if df is None or df.empty:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Standardize column names
            df = self._standardize_columns(df, source='vnstock')
            
            # Add symbol column
            df['symbol'] = symbol
            
            # Slice to requested limit if we fetched more
            if len(df) > limit:
                df = df.iloc[-limit:]
            
            logger.info(f"✅ Fetched {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"vnstock fetch error for {symbol}: {e}")
            return None
    
    def _fetch_ssi(self,
                  symbol: str,
                  timeframe: str,
                  start_date: Optional[str],
                  end_date: Optional[str]) -> Optional[pd.DataFrame]:
        """
        Fetch data from SSI API
        
        Note: Requires SSI account and API key
        """
        logger.warning("SSI API integration not yet implemented")
        logger.info("Please use 'vnstock' source or implement SSI API integration")
        return None
    
    def _fetch_csv(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Load data from CSV file
        
        Expected CSV format:
        timestamp,open,high,low,close,volume
        """
        try:
            filepath = f"data/{symbol}_{timeframe}.csv"
            df = pd.read_csv(filepath)
            
            # Standardize columns
            df = self._standardize_columns(df, source='csv')
            df['symbol'] = symbol
            
            logger.info(f"✅ Loaded {len(df)} candles from {filepath}")
            return df
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {filepath}")
            return None
        except Exception as e:
            logger.error(f"Error loading CSV for {symbol}: {e}")
            return None
    
    def _standardize_columns(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """
        Standardize column names across different sources
        
        Target format:
        - timestamp (unix timestamp)
        - open, high, low, close, volume
        """
        # Column mapping for different sources
        column_maps = {
            'vnstock': {
                'time': 'timestamp',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            },
            'csv': {
                'timestamp': 'timestamp',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
        }
        
        # Get column map for source
        col_map = column_maps.get(source, {})
        
        # Rename columns
        df = df.rename(columns=col_map)
        
        # Convert timestamp to unix timestamp if needed
        if 'timestamp' in df.columns:
            if df['timestamp'].dtype == 'object':
                # Parse datetime string
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Convert to unix timestamp
            if pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = df['timestamp'].astype(int) // 10**9
        
        # Select only required columns
        required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        available_cols = [col for col in required_cols if col in df.columns]
        
        df = df[available_cols].copy()
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def fetch_multiple_symbols(self,
                               symbols: List[str],
                               timeframe: str = '1D',
                               limit: int = 250) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols
        
        Args:
            symbols: List of stock symbols
            timeframe: Timeframe
            limit: Number of candles per symbol
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}
        
        for symbol in symbols:
            logger.info(f"Fetching {symbol}...")
            df = self.fetch_historical_data(symbol, timeframe, limit=limit)
            
            if df is not None and not df.empty:
                results[symbol] = df
            else:
                logger.warning(f"Skipping {symbol} - no data")
        
        logger.info(f"\n✅ Successfully fetched {len(results)}/{len(symbols)} symbols")
        return results
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get latest closing price for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Latest closing price or None
        """
        df = self.fetch_historical_data(symbol, limit=1)
        
        if df is not None and not df.empty:
            return float(df['close'].iloc[-1])
        
        return None


if __name__ == "__main__":
    # Test data fetcher
    print("="*70)
    print("DATA FETCHER TEST")
    print("="*70)
    
    # Test with vnstock (if available)
    print("\n📊 Testing vnstock source...")
    fetcher = DataFetcher(source='vnstock')
    
    # Fetch single symbol
    print("\nTest 1: Fetch single symbol (VNM)")
    df = fetcher.fetch_historical_data('VNM', limit=10)
    
    if df is not None:
        print(f"✅ Fetched {len(df)} candles")
        print("\nLast 3 candles:")
        print(df[['timestamp', 'close', 'volume']].tail(3))
        
        # Get latest price
        latest_price = fetcher.get_latest_price('VNM')
        print(f"\n💰 Latest price: {latest_price:,.0f} VND")
    else:
        print("❌ Failed to fetch data")
        print("Note: Install vnstock with: pip install vnstock")
    
    # Test multiple symbols
    print("\n" + "="*70)
    print("Test 2: Fetch multiple symbols")
    symbols = ['VNM', 'VCB', 'HPG']
    results = fetcher.fetch_multiple_symbols(symbols, limit=5)
    
    print(f"\n✅ Fetched {len(results)} symbols:")
    for symbol, df in results.items():
        latest = df['close'].iloc[-1]
        print(f"  {symbol}: {latest:,.0f} VND ({len(df)} candles)")
    
    print("\n" + "="*70)
