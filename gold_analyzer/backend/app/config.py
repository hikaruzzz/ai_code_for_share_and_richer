"""
配置管理模块
"""
from pathlib import Path
from pydantic_settings import BaseSettings

# 数据目录（使用绝对路径）
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 数据库文件路径
DB_PATH = DATA_DIR / "gold_analyzer.db"


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "黄金行情分析系统"
    app_version: str = "1.0.0"
    debug: bool = True

    # 数据库配置（使用绝对路径）
    database_url: str = f"sqlite+aiosqlite:///{DB_PATH.as_posix()}"

    # 数据源配置
    gold_symbol: str = "GC=F"  # 黄金期货
    dxy_symbol: str = "DX-Y.NYB"  # 美元指数

    # 定时任务配置
    price_update_interval: int = 300  # 5分钟更新一次价格
    news_update_interval: int = 900  # 15分钟更新一次新闻

    # API配置
    api_prefix: str = "/api"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
