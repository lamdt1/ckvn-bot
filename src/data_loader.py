from vnstock import Vnstock
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List

class DataLoader:
    _vnstock_client = None

    @classmethod
    def get_client(cls):
        if cls._vnstock_client is None:
            cls._vnstock_client = Vnstock()
        return cls._vnstock_client

    @staticmethod
    def get_realtime_prices(symbols: List[str]) -> pd.DataFrame:
        """Lấy bảng giá hiện tại sử dụng Vnstock v3 (Source: VCI)."""
        try:
            v = DataLoader.get_client()
            # PRICE BOARD
            df = v.stock(symbol=symbols[0], source='VCI').trading.price_board(symbols_list=symbols)
            
            if df.empty:
                return pd.DataFrame()

            # Xử lý MultiIndex columns
            if isinstance(df.columns, pd.MultiIndex):
                # Lấy level 1 làm tên cột chính nếu có
                df.columns = [col[1] if col[1] else col[0] for col in df.columns.values]
            
            # Chuẩn hóa tên cột cho main.py
            rename_map = {
                'symbol': 'Mã CP',
                'match_price': 'Giá Khớp Lệnh'
            }
            df = df.rename(columns=rename_map)
            
            # Đảm bảo các cột cần thiết có kiểu dữ liệu đúng
            if 'Giá Khớp Lệnh' in df.columns:
                df['Giá Khớp Lệnh'] = pd.to_numeric(df['Giá Khớp Lệnh'], errors='coerce')
                
            return df
        except Exception as e:
            print(f"Error fetching real-time prices (v3): {e}")
            return pd.DataFrame()

    @staticmethod
    def get_historical_data(symbol: str, days: int = 50) -> pd.DataFrame:
        """Lấy dữ liệu lịch sử sử dụng Vnstock v3 (Source: VCI)."""
        try:
            v = DataLoader.get_client()
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # HISTORY
            df = v.stock(symbol=symbol, source='VCI').quote.history(
                start=start_date, 
                end=end_date
            )
            
            if df.empty:
                return pd.DataFrame()

            # Quy đổi đơn vị: Vnstock v3 history trả về đơn vị 1000 VND
            # Chúng ta nhân 1000 để khớp với giá portfolio và giá realtime
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                if col in df.columns:
                    df[col] = df[col] * 1000
            
            return df
        except Exception as e:
            print(f"Error fetching historical data for {symbol} (v3): {e}")
            return pd.DataFrame()
