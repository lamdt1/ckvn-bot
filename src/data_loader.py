from vnstock import stock_historical_data, price_board
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List

class DataLoader:
    @staticmethod
    def get_realtime_prices(symbols: List[str]) -> pd.DataFrame:
        """Lấy bảng giá hiện tại cho danh sách mã chứng khoán."""
        try:
            # vnstock price_board trả về DataFrame
            df = price_board(",".join(symbols))
            return df
        except Exception as e:
            print(f"Error fetching real-time prices: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_historical_data(symbol: str, days: int = 50) -> pd.DataFrame:
        """Lấy dữ liệu lịch sử để tính toán RSI/MA. Mặc định lấy 50 ngày để đủ dữ liệu cho MA20/RSI14."""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            df = stock_historical_data(symbol, start_date, end_date, "1D", "stock")
            return df
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
