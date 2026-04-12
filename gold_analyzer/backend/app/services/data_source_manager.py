"""
数据源管理服务
"""
from pathlib import Path
from typing import Dict, List, Optional, Any
from app.services.data_sources import (
    BaseDataSource,
    YahooFinanceSource,
    AlphaVantageSource,
    GoldPriceApiSource,
    MockDataSource,
    DATA_SOURCES,
    DEFAULT_SOURCE,
)


def _load_api_key_from_file(filename: str) -> Optional[str]:
    """从文件加载API Key"""
    try:
        # 获取data目录下的文件路径
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        key_file = data_dir / filename
        if key_file.exists():
            content = key_file.read_text().strip()
            if content:
                return content
    except Exception as e:
        print(f"加载API Key文件失败: {e}")
    return None


class DataSourceManager:
    """数据源管理器"""

    def __init__(self):
        self._sources: Dict[str, BaseDataSource] = {}
        self._current_source: str = DEFAULT_SOURCE
        self._api_keys: Dict[str, str] = {}

        # 从文件加载默认API Key
        self._load_default_api_keys()

        # 初始化默认数据源
        self._init_sources()

    def _load_default_api_keys(self):
        """从文件加载默认API Key"""
        # 加载 Gold Price API Key
        gold_price_key = _load_api_key_from_file("share_api_key.txt")
        if gold_price_key:
            self._api_keys["gold_price_api"] = gold_price_key
            print(f"已加载 Gold Price API Key")

    def _init_sources(self):
        """初始化所有数据源实例"""
        # Yahoo Finance (不需要API Key)
        self._sources["yahoo_finance"] = YahooFinanceSource()

        # Alpha Vantage (需要API Key)
        self._sources["alpha_vantage"] = AlphaVantageSource(
            api_key=self._api_keys.get("alpha_vantage", "demo")
        )

        # Gold Price API (需要API Key，已从文件加载)
        self._sources["gold_price_api"] = GoldPriceApiSource(
            api_key=self._api_keys.get("gold_price_api", "")
        )

        # 模拟数据源
        self._sources["mock"] = MockDataSource()

    def get_source(self, source_name: Optional[str] = None) -> BaseDataSource:
        """获取数据源实例"""
        name = source_name or self._current_source

        if name not in self._sources:
            raise ValueError(f"未知的数据源: {name}")

        return self._sources[name]

    def set_current_source(self, source_name: str):
        """设置当前数据源"""
        if source_name not in DATA_SOURCES:
            raise ValueError(f"未知的数据源: {source_name}")
        self._current_source = source_name

    def get_current_source(self) -> str:
        """获取当前数据源名称"""
        return self._current_source

    def set_api_key(self, source_name: str, api_key: str):
        """设置数据源的API Key"""
        self._api_keys[source_name] = api_key

        # 重新初始化需要API Key的数据源
        if source_name == "alpha_vantage":
            self._sources["alpha_vantage"] = AlphaVantageSource(api_key=api_key)
        elif source_name == "gold_price_api":
            self._sources["gold_price_api"] = GoldPriceApiSource(api_key=api_key)

    def list_sources(self) -> List[Dict[str, Any]]:
        """列出所有可用的数据源"""
        result = []
        for name, source_class in DATA_SOURCES.items():
            result.append({
                "name": name,
                "description": source_class.description,
                "requires_api_key": source_class.requires_api_key,
                "is_current": name == self._current_source,
                "has_api_key": bool(self._api_keys.get(name))
            })
        return result

    async def check_availability(self, source_name: str) -> bool:
        """检查数据源是否可用"""
        if source_name not in self._sources:
            return False
        return await self._sources[source_name].is_available()

    async def check_all_availability(self) -> Dict[str, bool]:
        """检查所有数据源的可用性"""
        result = {}
        for name, source in self._sources.items():
            result[name] = await source.is_available()
        return result


# 单例实例
data_source_manager = DataSourceManager()
