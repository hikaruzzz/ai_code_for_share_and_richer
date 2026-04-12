"""
Gold Price API 数据源适配器
https://gold-price-api.omkar.cloud/
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx
import pandas as pd

from .base import BaseDataSource


class GoldPriceApiSource(BaseDataSource):
    """Gold Price API 数据源 (omkar.cloud)"""

    name = "gold_price_api"
    description = "Gold Price API (实时黄金期货，5000次/月免费)"
    requires_api_key = True

    # API配置
    API_URL = "https://gold-price-api.omkar.cloud/price"

    # 支持的品种（此API只支持黄金）
    SUPPORTED_SYMBOLS = ["GC=F", "XAUUSD=X", "GOLD"]

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取实时黄金价格"""
        # 检查是否支持该品种
        if symbol not in self.SUPPORTED_SYMBOLS:
            return None

        if not self.api_key:
            print("Gold Price API: 未配置API Key")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.API_URL,
                    headers={"API-Key": self.api_key},
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    price = data.get("price_usd")
                    updated_at = data.get("updated_at")

                    # 解析时间
                    if updated_at:
                        timestamp = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.now()

                    return {
                        "symbol": symbol,
                        "name": "黄金期货",
                        "price": price,
                        "change": None,
                        "change_percent": None,
                        "open": None,
                        "high": None,
                        "low": None,
                        "volume": None,
                        "previous_close": None,
                        "timestamp": timestamp
                    }

                elif response.status_code == 401:
                    print("Gold Price API: API Key无效")
                    return None
                elif response.status_code == 429:
                    print("Gold Price API: 请求频率超限")
                    return None
                else:
                    print(f"Gold Price API: 请求失败 {response.status_code}")
                    return None

        except Exception as e:
            print(f"Gold Price API请求异常: {e}")
            return None

    async def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """获取历史价格（不支持）"""
        print("Gold Price API: 不支持历史数据查询")
        return pd.DataFrame()

    async def get_kline_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """获取K线数据（不支持）"""
        return []

    async def is_available(self) -> bool:
        """检查API是否可用"""
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.API_URL,
                    headers={"API-Key": self.api_key},
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False
