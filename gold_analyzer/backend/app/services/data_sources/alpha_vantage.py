"""
Alpha Vantage 数据源适配器
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import httpx

from .base import BaseDataSource


class AlphaVantageSource(BaseDataSource):
    """Alpha Vantage 数据源"""

    name = "alpha_vantage"
    description = "Alpha Vantage (免费API，需注册，500次/天)"
    requires_api_key = True

    BASE_URL = "https://www.alphavantage.co/query"

    # Alpha Vantage 黄金相关品种
    SYMBOLS = {
        "GLD": "黄金ETF",
        "GDX": "金矿股ETF",
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key or "demo"

    async def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取实时价格 (使用GLOBAL_QUOTE接口)"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": self.api_key
                }
                response = await client.get(self.BASE_URL, params=params)
                data = response.json()

                if "Global Quote" not in data:
                    return None

                quote = data["Global Quote"]
                price = float(quote.get("05. price", 0))
                prev_close = float(quote.get("08. previous close", price))
                change = price - prev_close
                change_percent = (change / prev_close * 100) if prev_close else 0

                return {
                    "symbol": symbol,
                    "name": self.SYMBOLS.get(symbol, symbol),
                    "price": price,
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "open": float(quote.get("02. open", 0)),
                    "high": float(quote.get("03. high", 0)),
                    "low": float(quote.get("04. low", 0)),
                    "volume": int(quote.get("06. volume", 0)),
                    "previous_close": prev_close,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Alpha Vantage获取实时价格失败: {e}")
            return None

    async def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """获取历史价格数据"""
        try:
            days = self.period_to_days(period)
            output_size = "full" if days > 100 else "compact"

            async with httpx.AsyncClient() as client:
                params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": symbol,
                    "outputsize": output_size,
                    "apikey": self.api_key
                }
                response = await client.get(self.BASE_URL, params=params)
                data = response.json()

                if "Time Series (Daily)" not in data:
                    return pd.DataFrame()

                time_series = data["Time Series (Daily)"]
                df_data = []

                for date_str, values in time_series.items():
                    df_data.append({
                        "timestamp": pd.to_datetime(date_str),
                        "Open": float(values["1. open"]),
                        "High": float(values["2. high"]),
                        "Low": float(values["3. low"]),
                        "Close": float(values["4. close"]),
                        "Volume": float(values["5. volume"])
                    })

                df = pd.DataFrame(df_data)
                df = df.sort_values("timestamp")
                # 限制返回的数据量
                df = df.tail(days)

                return df.reset_index(drop=True)
        except Exception as e:
            print(f"Alpha Vantage获取历史价格失败: {e}")
            return pd.DataFrame()

    async def get_kline_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """获取K线数据"""
        df = await self.get_historical_prices(symbol, "1y", interval)

        if df.empty:
            return []

        klines = []
        for _, row in df.iterrows():
            klines.append({
                "timestamp": row["timestamp"].isoformat(),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"]
            })

        return klines

    async def is_available(self) -> bool:
        """检查数据源是否可用"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": "GLD",
                    "apikey": self.api_key
                }
                response = await client.get(self.BASE_URL, params=params)
                data = response.json()
                return "Global Quote" in data and data["Global Quote"]
        except:
            return False
