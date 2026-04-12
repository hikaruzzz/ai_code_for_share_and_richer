"""
数据源适配器基类
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd


class BaseDataSource(ABC):
    """数据源适配器基类"""

    # 数据源名称
    name: str = "base"
    # 数据源描述
    description: str = "基础数据源"
    # 是否需要API Key
    requires_api_key: bool = False

    @abstractmethod
    async def get_realtime_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时价格

        Args:
            symbol: 交易品种代码

        Returns:
            价格信息字典，包含:
            - symbol: 品种代码
            - price: 当前价格
            - change: 涨跌额
            - change_percent: 涨跌幅
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - volume: 成交量
            - timestamp: 时间戳
        """
        pass

    @abstractmethod
    async def get_historical_prices(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        获取历史价格数据

        Args:
            symbol: 交易品种代码
            period: 时间周期
            interval: 时间间隔

        Returns:
            DataFrame，包含列: timestamp, Open, High, Low, Close, Volume
        """
        pass

    @abstractmethod
    async def get_kline_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据

        Args:
            symbol: 交易品种代码
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间间隔

        Returns:
            K线数据列表
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        检查数据源是否可用

        Returns:
            是否可用
        """
        pass

    def period_to_days(self, period: str) -> int:
        """将period转换为天数"""
        mapping = {
            "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
            "6mo": 180, "1y": 365, "2y": 730, "5y": 1825,
            "10y": 3650, "ytd": 365, "max": 365
        }
        return mapping.get(period, 365)
