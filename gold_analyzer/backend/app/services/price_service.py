"""
价格数据服务模块
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price import PriceModel
from app.config import settings
from app.services.data_source_manager import data_source_manager


class PriceService:
    """价格数据服务"""

    # 支持的交易品种
    SYMBOLS = {
        "GC=F": "黄金期货",
        "XAUUSD=X": "现货黄金",
        "DX-Y.NYB": "美元指数",
        "GLD": "黄金ETF",
    }

    # 黄金相关品种
    GOLD_SYMBOLS = ["GC=F", "XAUUSD=X", "GOLD", "GLD"]

    # 不支持所有品种的数据源
    GOLD_ONLY_SOURCES = ["gold_price_api"]

    async def get_realtime_price(
        self,
        symbol: str = "GC=F",
        source: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """获取实时价格"""
        source_name = source or data_source_manager.get_current_source()

        # 检查数据源是否支持该品种
        if source_name in self.GOLD_ONLY_SOURCES and symbol not in self.GOLD_SYMBOLS:
            return {
                "error": f"数据源 '{source_name}' 不支持品种 '{symbol}'，仅支持黄金相关品种",
                "error_code": "UNSUPPORTED_SYMBOL"
            }

        try:
            data_source = data_source_manager.get_source(source_name)
            price_data = await data_source.get_realtime_price(symbol)

            if price_data:
                price_data["data_source"] = data_source.name
                return price_data

            return {
                "error": f"数据源 '{source_name}' 返回空数据",
                "error_code": "EMPTY_RESPONSE"
            }

        except Exception as e:
            return {
                "error": f"获取实时价格失败: {str(e)}",
                "error_code": "REQUEST_FAILED"
            }

    async def get_historical_prices_from_db(
        self,
        session: AsyncSession,
        symbol: str,
        data_source: str,
        limit: int = 500
    ) -> pd.DataFrame:
        """从数据库获取历史价格数据"""
        query = select(PriceModel).where(
            PriceModel.symbol == symbol,
            PriceModel.data_source == data_source
        ).order_by(PriceModel.timestamp.desc()).limit(limit)

        result = await session.execute(query)
        prices = result.scalars().all()

        if not prices:
            return pd.DataFrame()

        # 转换为DataFrame
        data = []
        for p in reversed(prices):
            data.append({
                'timestamp': p.timestamp,
                'Open': p.open,
                'High': p.high,
                'Low': p.low,
                'Close': p.close,
                'Volume': p.volume
            })

        return pd.DataFrame(data)

    async def get_historical_prices(
        self,
        symbol: str = "GC=F",
        period: str = "1y",
        interval: str = "1d",
        source: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> tuple[pd.DataFrame, Optional[str]]:
        """
        获取历史价格数据

        Returns:
            (DataFrame, error_message) - 数据和错误信息
        """
        source_name = source or data_source_manager.get_current_source()

        # 检查数据源是否支持该品种
        if source_name in self.GOLD_ONLY_SOURCES and symbol not in self.GOLD_SYMBOLS:
            return pd.DataFrame(), f"数据源 '{source_name}' 不支持品种 '{symbol}'"

        # 检查数据源是否支持历史数据
        if source_name in self.GOLD_ONLY_SOURCES:
            return pd.DataFrame(), f"数据源 '{source_name}' 不支持历史数据查询"

        # 优先从数据库获取
        if session:
            df = await self.get_historical_prices_from_db(session, symbol, source_name)
            if not df.empty:
                print(f"从数据库获取 {source_name} 的 {len(df)} 条历史数据")
                return df, None

        # 数据库没有，从API获取
        try:
            data_source = data_source_manager.get_source(source_name)
            df = await data_source.get_historical_prices(symbol, period, interval)

            if not df.empty:
                print(f"从 {source_name} API 获取 {len(df)} 条历史数据")
                return df, None

            return pd.DataFrame(), f"数据源 '{source_name}' 返回空数据"

        except Exception as e:
            return pd.DataFrame(), f"获取历史数据失败: {str(e)}"

    async def get_kline_data(
        self,
        symbol: str = "GC=F",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d",
        source: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """获取K线数据"""
        source_name = source or data_source_manager.get_current_source()

        # 检查数据源是否支持
        if source_name in self.GOLD_ONLY_SOURCES and symbol not in self.GOLD_SYMBOLS:
            return [], f"数据源 '{source_name}' 不支持品种 '{symbol}'"

        if source_name in self.GOLD_ONLY_SOURCES:
            return [], f"数据源 '{source_name}' 不支持K线数据查询"

        try:
            data_source = data_source_manager.get_source(source_name)
            klines = await data_source.get_kline_data(symbol, start_date, end_date, interval)

            if klines:
                return klines, None

            return [], f"数据源 '{source_name}' 返回空数据"

        except Exception as e:
            return [], f"获取K线数据失败: {str(e)}"

    async def save_price_data(
        self,
        session: AsyncSession,
        symbol: str,
        data: Dict[str, Any],
        data_source: str = "yahoo_finance"
    ) -> Optional[PriceModel]:
        """保存价格数据到数据库"""
        try:
            ts = data.get("timestamp", datetime.now())
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))

            # 检查是否已存在
            existing = await session.execute(
                select(PriceModel).where(
                    PriceModel.symbol == symbol,
                    PriceModel.data_source == data_source,
                    PriceModel.timestamp == ts
                )
            )
            if existing.scalar_one_or_none():
                return None

            price = PriceModel(
                symbol=symbol,
                data_source=data_source,
                timestamp=ts,
                open=data.get("open"),
                high=data.get("high"),
                low=data.get("low"),
                close=data.get("price") or data.get("close"),
                volume=data.get("volume")
            )

            session.add(price)
            await session.commit()
            await session.refresh(price)
            return price

        except Exception as e:
            print(f"保存价格数据失败: {e}")
            await session.rollback()
            return None

    async def get_prices_from_db(
        self,
        session: AsyncSession,
        symbol: str,
        data_source: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500
    ) -> List[PriceModel]:
        """从数据库获取历史价格数据"""
        query = select(PriceModel).where(PriceModel.symbol == symbol)

        if data_source:
            query = query.where(PriceModel.data_source == data_source)

        if start_time:
            query = query.where(PriceModel.timestamp >= start_time)
        if end_time:
            query = query.where(PriceModel.timestamp <= end_time)

        query = query.order_by(PriceModel.timestamp.desc()).limit(limit)

        result = await session.execute(query)
        return result.scalars().all()

    async def fetch_and_save_prices(
        self,
        session: AsyncSession,
        symbol: str = "GC=F",
        period: str = "1mo",
        source: Optional[str] = None
    ) -> tuple[int, Optional[str]]:
        """获取并保存历史价格数据"""
        source_name = source or data_source_manager.get_current_source()

        # 检查支持性
        if source_name in self.GOLD_ONLY_SOURCES and symbol not in self.GOLD_SYMBOLS:
            return 0, f"数据源 '{source_name}' 不支持品种 '{symbol}'"

        if source_name in self.GOLD_ONLY_SOURCES:
            return 0, f"数据源 '{source_name}' 不支持历史数据查询"

        df, error = await self.get_historical_prices(symbol, period, source=source_name, session=session)
        if error or df.empty:
            return 0, error or "获取数据为空"

        count = 0
        for _, row in df.iterrows():
            ts = row.get("timestamp") or row.get("Date") or row.get("Datetime")
            if ts is None:
                continue

            ts_dt = ts.to_pydatetime() if hasattr(ts, 'to_pydatetime') else ts

            existing = await session.execute(
                select(PriceModel).where(
                    PriceModel.symbol == symbol,
                    PriceModel.data_source == source_name,
                    PriceModel.timestamp == ts_dt
                )
            )
            if existing.scalar_one_or_none():
                continue

            price = PriceModel(
                symbol=symbol,
                data_source=source_name,
                timestamp=ts_dt,
                open=row.get("Open") or row.get("open"),
                high=row.get("High") or row.get("high"),
                low=row.get("Low") or row.get("low"),
                close=row.get("Close") or row.get("close"),
                volume=row.get("Volume") or row.get("volume")
            )
            session.add(price)
            count += 1

        await session.commit()
        return count, None

    async def calculate_correlation(
        self,
        symbol1: str = "GC=F",
        symbol2: str = "DX-Y.NYB",
        period: str = "1y",
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """计算两个品种的相关性"""
        df1, err1 = await self.get_historical_prices(symbol1, period, source=source)
        df2, err2 = await self.get_historical_prices(symbol2, period, source=source)

        if err1:
            return {"error": f"{symbol1}: {err1}"}
        if err2:
            return {"error": f"{symbol2}: {err2}"}
        if df1.empty or df2.empty:
            return {"error": "无法获取数据"}

        try:
            df1_copy = df1.copy()
            df2_copy = df2.copy()

            ts_col1 = "timestamp" if "timestamp" in df1_copy.columns else "Date"
            ts_col2 = "timestamp" if "timestamp" in df2_copy.columns else "Date"

            df1_copy.set_index(ts_col1, inplace=True)
            df2_copy.set_index(ts_col2, inplace=True)

            close_col1 = "Close" if "Close" in df1_copy.columns else "close"
            close_col2 = "Close" if "Close" in df2_copy.columns else "close"

            merged = pd.merge(
                df1_copy[[close_col1]],
                df2_copy[[close_col2]],
                left_index=True,
                right_index=True,
                suffixes=("_1", "_2")
            )

            correlation = merged[close_col1 + "_1"].corr(merged[close_col2 + "_2"])

            return {
                "symbol1": symbol1,
                "symbol2": symbol2,
                "correlation": float(correlation),
                "period": period,
                "data_points": len(merged),
                "interpretation": "负相关" if correlation < -0.3 else "正相关" if correlation > 0.3 else "弱相关"
            }
        except Exception as e:
            return {"error": f"计算相关性失败: {str(e)}"}


# 单例实例
price_service = PriceService()
