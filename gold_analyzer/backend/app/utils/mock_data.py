"""
模拟数据服务（用于演示和测试）
当 Yahoo Finance API 限流时使用
"""
import random
from datetime import datetime, timedelta
from typing import List
import pandas as pd
import numpy as np


class MockDataService:
    """模拟数据服务"""

    # 模拟的基础价格
    BASE_PRICES = {
        "GC=F": 2350.0,  # 黄金期货
        "DX-Y.NYB": 104.0,  # 美元指数
        "XAUUSD=X": 2340.0  # 现货黄金
    }

    def generate_realtime_price(self, symbol: str = "GC=F") -> dict:
        """生成模拟实时价格"""
        base_price = self.BASE_PRICES.get(symbol, 100.0)
        change_percent = random.uniform(-2, 2)
        change = base_price * change_percent / 100
        price = base_price + change

        return {
            "symbol": symbol,
            "name": self._get_symbol_name(symbol),
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

    def generate_historical_prices(
        self,
        symbol: str = "GC=F",
        days: int = 365
    ) -> pd.DataFrame:
        """生成模拟历史价格数据"""
        base_price = self.BASE_PRICES.get(symbol, 100.0)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

        # 使用随机游走生成价格
        np.random.seed(hash(symbol) % 2**32)
        returns = np.random.normal(0.0005, 0.015, days)
        prices = base_price * np.exp(np.cumsum(returns))

        # 生成OHLCV数据
        data = pd.DataFrame({
            'timestamp': dates,
            'Open': prices * np.random.uniform(0.995, 1.005, days),
            'High': prices * np.random.uniform(1.0, 1.02, days),
            'Low': prices * np.random.uniform(0.98, 1.0, days),
            'Close': prices,
            'Volume': np.random.randint(100000, 500000, days).astype(float)
        })

        return data

    def generate_kline_data(
        self,
        symbol: str = "GC=F",
        days: int = 365
    ) -> List[dict]:
        """生成模拟K线数据"""
        df = self.generate_historical_prices(symbol, days)
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

    def generate_correlation(
        self,
        symbol1: str = "GC=F",
        symbol2: str = "DX-Y.NYB"
    ) -> dict:
        """生成模拟相关性分析"""
        # 黄金和美元通常呈负相关
        correlation = random.uniform(-0.8, -0.4)

        return {
            "symbol1": symbol1,
            "symbol2": symbol2,
            "correlation": round(correlation, 3),
            "period": "1y",
            "data_points": 252,
            "interpretation": "负相关" if correlation < -0.3 else "弱相关"
        }

    def _get_symbol_name(self, symbol: str) -> str:
        """获取品种名称"""
        names = {
            "GC=F": "黄金期货",
            "DX-Y.NYB": "美元指数",
            "XAUUSD=X": "现货黄金"
        }
        return names.get(symbol, symbol)


# 单例实例
mock_data_service = MockDataService()
