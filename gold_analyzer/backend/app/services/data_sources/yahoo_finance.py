"""
Yahoo Finance 数据源适配器
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import yfinance as yf

from .base import BaseDataSource


class YahooFinanceSource(BaseDataSource):
    """Yahoo Finance 数据源"""

    name = "yahoo_finance"
    description = "Yahoo Finance (免费，15分钟延迟)"
    requires_api_key = False

    # 支持的交易品种映射
    SYMBOLS = {
        "GC=F": "黄金期货",
        "XAUUSD=X": "现货黄金",
        "DX-Y.NYB": "美元指数"
    }

    async def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取实时价格"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            price = info.get("regularMarketPrice")
            if price is None:
                return None

            return {
                "symbol": symbol,
                "name": self.SYMBOLS.get(symbol, symbol),
                "price": price,
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0),
                "open": info.get("regularMarketOpen"),
                "high": info.get("dayHigh"),
                "low": info.get("dayLow"),
                "volume": info.get("regularMarketVolume"),
                "previous_close": info.get("previousClose"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Yahoo Finance获取实时价格失败: {e}")
            return None

    async def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """获取历史价格数据"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                return pd.DataFrame()

            df.reset_index(inplace=True)
            # 重命名日期列
            if 'Date' in df.columns:
                df.rename(columns={"Date": "timestamp"}, inplace=True)
            elif 'Datetime' in df.columns:
                df.rename(columns={"Datetime": "timestamp"}, inplace=True)

            return df
        except Exception as e:
            print(f"Yahoo Finance获取历史价格失败: {e}")
            return pd.DataFrame()

    async def get_kline_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """获取K线数据"""
        try:
            ticker = yf.Ticker(symbol)

            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date, interval=interval)
            else:
                df = ticker.history(period="1y", interval=interval)

            if df.empty:
                return []

            klines = []
            for index, row in df.iterrows():
                klines.append({
                    "timestamp": index.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row["Volume"])
                })

            return klines
        except Exception as e:
            print(f"Yahoo Finance获取K线数据失败: {e}")
            return []

    async def is_available(self) -> bool:
        """检查数据源是否可用"""
        try:
            ticker = yf.Ticker("GC=F")
            info = ticker.info
            return info.get("regularMarketPrice") is not None
        except:
            return False
