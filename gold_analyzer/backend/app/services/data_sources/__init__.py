"""
数据源适配器模块
"""
from .base import BaseDataSource
from .yahoo_finance import YahooFinanceSource
from .alpha_vantage import AlphaVantageSource
from .gold_price_api import GoldPriceApiSource
from .mock import MockDataSource

# 所有可用的数据源
DATA_SOURCES = {
    "yahoo_finance": YahooFinanceSource,
    "alpha_vantage": AlphaVantageSource,
    "gold_price_api": GoldPriceApiSource,
    "mock": MockDataSource,
}

# 默认数据源
DEFAULT_SOURCE = "yahoo_finance"

__all__ = [
    "BaseDataSource",
    "YahooFinanceSource",
    "AlphaVantageSource",
    "MockDataSource",
    "DATA_SOURCES",
    "DEFAULT_SOURCE",
]
