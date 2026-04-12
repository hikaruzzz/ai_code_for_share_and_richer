"""
价格数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from app.db.database import Base


class PriceModel(Base):
    """价格数据表"""
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True, comment="交易品种代码")
    data_source = Column(String(50), nullable=False, default="yahoo_finance", index=True, comment="数据源")
    timestamp = Column(DateTime, nullable=False, index=True, comment="时间戳")
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    volume = Column(Float, comment="成交量")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        UniqueConstraint('symbol', 'data_source', 'timestamp', name='uix_symbol_source_timestamp'),
    )

    def __repr__(self):
        return f"<Price({self.symbol}, {self.data_source}, {self.timestamp}, close={self.close})>"
