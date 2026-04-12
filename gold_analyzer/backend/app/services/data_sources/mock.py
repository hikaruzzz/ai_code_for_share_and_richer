"""
模拟数据源适配器（用于演示和测试）
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import random

from .base import BaseDataSource


class MockDataSource(BaseDataSource):
    """模拟数据源"""

    name = "mock"
    description = "模拟数据 (用于演示和测试)"
    requires_api_key = False

    # 模拟的基础价格
    BASE_PRICES = {
        "GC=F": 2350.0,
        "DX-Y.NYB": 104.0,
        "XAUUSD=X": 2340.0,
        "GLD": 215.0,
    }

    SYMBOLS = {
        "GC=F": "黄金期货",
        "XAUUSD=X": "现货黄金",
        "DX-Y.NYB": "美元指数",
        "GLD": "黄金ETF",
    }

    async def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """生成模拟实时价格"""
        base_price = self.BASE_PRICES.get(symbol, 100.0)
        change_percent = random.uniform(-2, 2)
        change = base_price * change_percent / 100
        price = base_price + change

        return {
            "symbol": symbol,
            "name": self.SYMBOLS.get(symbol, symbol),
            "price": round(price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "open": round(base_price * random.uniform(0.995, 1.005), 2),
            "high": round(price * random.uniform(1.0, 1.01), 2),
            "low": round(price * random.uniform(0.99, 1.0), 2),
            "volume": random.randint(100000, 500000),
            "previous_close": round(base_price, 2),
            "timestamp": datetime.now()
        }

    async def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """生成模拟历史价格数据"""
        base_price = self.BASE_PRICES.get(symbol, 100.0)
        days = self.period_to_days(period)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

        # 使用随机游走生成价格
        np.random.seed(hash(symbol) % 2**32)
        returns = np.random.normal(0.0005, 0.015, days)
        prices = base_price * np.exp(np.cumsum(returns))

        # 生成OHLCV数据
        df = pd.DataFrame({
            'timestamp': dates,
            'Open': prices * np.random.uniform(0.995, 1.005, days),
            'High': prices * np.random.uniform(1.0, 1.02, days),
            'Low': prices * np.random.uniform(0.98, 1.0, days),
            'Close': prices,
            'Volume': np.random.randint(100000, 500000, days).astype(float)
        })

        return df

    async def get_kline_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """生成模拟K线数据"""
        df = await self.get_historical_prices(symbol, "1y")
        klines = []

        for _, row in df.iterrows():
            klines.append({
                "timestamp": row["timestamp"].isoformat(),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })

        return klines

    async def is_available(self) -> bool:
        """模拟数据源始终可用"""
        return True
