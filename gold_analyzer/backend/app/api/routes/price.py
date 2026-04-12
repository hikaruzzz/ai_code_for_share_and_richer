"""
价格相关API路由
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.services.price_service import price_service
from app.services.data_source_manager import data_source_manager
from app.config import settings

router = APIRouter(prefix="/price", tags=["价格"])


@router.get("/realtime")
async def get_realtime_price(
    symbol: str = Query(default="GC=F", description="交易品种代码"),
    source: Optional[str] = Query(default=None, description="数据源"),
    session: AsyncSession = Depends(get_session)
):
    """获取实时价格"""
    source_name = source or data_source_manager.get_current_source()
    data = await price_service.get_realtime_price(symbol, source_name)

    # 检查是否有错误
    if data and data.get("error"):
        return data

    # 保存到数据库
    if data and not data.get("error"):
        data_source = data.get("data_source", source_name)
        await price_service.save_price_data(session, symbol, data, data_source)

    return data


@router.get("/history")
async def get_historical_prices(
    symbol: str = Query(default="GC=F", description="交易品种代码"),
    period: str = Query(default="1y", description="时间周期"),
    interval: str = Query(default="1d", description="时间间隔"),
    source: Optional[str] = Query(default=None, description="数据源"),
    session: AsyncSession = Depends(get_session)
):
    """获取历史价格数据"""
    source_name = source or data_source_manager.get_current_source()

    df, error = await price_service.get_historical_prices(symbol, period, interval, source_name, session)

    if error:
        return {
            "error": error,
            "error_code": "DATA_FETCH_FAILED",
            "symbol": symbol,
            "data_source": source_name
        }

    if df.empty:
        return {
            "error": "无法获取数据",
            "error_code": "EMPTY_DATA",
            "symbol": symbol,
            "data_source": source_name
        }

    return {
        "symbol": symbol,
        "period": period,
        "interval": interval,
        "data_source": source_name,
        "data_count": len(df),
        "data": df.to_dict(orient="records")[-500:]
    }


@router.get("/kline")
async def get_kline_data(
    symbol: str = Query(default="GC=F", description="交易品种代码"),
    start_date: Optional[str] = Query(default=None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="结束日期 YYYY-MM-DD"),
    interval: str = Query(default="1d", description="时间间隔"),
    source: Optional[str] = Query(default=None, description="数据源")
):
    """获取K线数据"""
    source_name = source or data_source_manager.get_current_source()
    klines, error = await price_service.get_kline_data(symbol, start_date, end_date, interval, source_name)

    if error:
        return {
            "error": error,
            "error_code": "DATA_FETCH_FAILED",
            "symbol": symbol,
            "data_source": source_name
        }

    return {
        "symbol": symbol,
        "count": len(klines),
        "data_source": source_name,
        "data": klines
    }


@router.get("/correlation")
async def get_correlation(
    symbol1: str = Query(default="GC=F", description="品种1代码"),
    symbol2: str = Query(default="DX-Y.NYB", description="品种2代码"),
    period: str = Query(default="1y", description="时间周期"),
    source: Optional[str] = Query(default=None, description="数据源")
):
    """获取两个品种的相关性分析"""
    result = await price_service.calculate_correlation(symbol1, symbol2, period, source)
    return result


@router.post("/sync")
async def sync_price_data(
    symbol: str = Query(default="GC=F", description="交易品种代码"),
    period: str = Query(default="1mo", description="同步时间周期"),
    source: Optional[str] = Query(default=None, description="数据源"),
    session: AsyncSession = Depends(get_session)
):
    """同步历史价格数据到数据库"""
    source_name = source or data_source_manager.get_current_source()
    count, error = await price_service.fetch_and_save_prices(session, symbol, period, source_name)

    if error:
        return {
            "success": False,
            "error": error,
            "symbol": symbol,
            "data_source": source_name
        }

    return {
        "success": True,
        "symbol": symbol,
        "data_source": source_name,
        "synced_count": count,
        "message": f"成功同步 {count} 条记录"
    }


# ============ 数据源管理 API ============

@router.get("/sources")
async def list_data_sources():
    """列出所有可用的数据源"""
    sources = data_source_manager.list_sources()
    return {
        "current_source": data_source_manager.get_current_source(),
        "sources": sources
    }


@router.post("/sources/switch")
async def switch_data_source(
    source: str = Query(..., description="数据源名称")
):
    """切换当前数据源"""
    try:
        data_source_manager.set_current_source(source)
        return {
            "success": True,
            "current_source": source,
            "message": f"已切换到数据源: {source}"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/sources/api-key")
async def set_api_key(
    source: str = Query(..., description="数据源名称"),
    api_key: str = Query(..., description="API Key")
):
    """设置数据源的API Key"""
    try:
        data_source_manager.set_api_key(source, api_key)
        return {
            "success": True,
            "message": f"已设置 {source} 的API Key"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/sources/check")
async def check_sources_availability():
    """检查所有数据源的可用性"""
    availability = await data_source_manager.check_all_availability()
    return {
        "availability": availability
    }
