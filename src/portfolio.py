import json
import os
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class StockPosition(BaseModel):
    avg_price: float
    quantity: int
    last_alert: Optional[float] = None  # timestamp

class Portfolio(BaseModel):
    items: Dict[str, StockPosition]

class PortfolioManager:
    def __init__(self, file_path: str = "portfolio.json"):
        self.file_path = file_path

    def load_portfolio(self) -> Dict[str, StockPosition]:
        if not os.path.exists(self.file_path):
            return {}
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {k: StockPosition(**v) for k, v in data.items()}
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            return {}

    def save_portfolio(self, portfolio_data: Dict[str, StockPosition]):
        try:
            # Convert StockPosition objects back to dicts for JSON serialization
            data_to_save = {k: v.model_dump() for k, v in portfolio_data.items()}
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving portfolio: {e}")

# Practical usage helper
def get_portfolio_manager():
    return PortfolioManager()
