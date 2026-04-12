"""
交易信号数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.db.database import Base


class SignalModel(Base):
    """交易信号表"""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True, comment="交易品种")
    timestamp = Column(DateTime, index=True, comment="信号时间")
    signal_type = Column(String(20), nullable=False, comment="信号类型: STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL")
    confidence = Column(Float, nullable=False, comment="置信度 0-1")
    entry_price = Column(Float, comment="入场价格")
    target_price = Column(Float, comment="目标价格")
    stop_loss = Column(Float, comment="止损价格")
    risk_reward_ratio = Column(Float, comment="风险收益比")

    # 各维度得分
    tech_score = Column(Float, comment="技术指标得分")
    sentiment_score = Column(Float, comment="情感得分")
    dxy_correlation = Column(Float, comment="美元相关性得分")

    reason = Column(Text, comment="信号原因说明")
    indicators_json = Column(Text, comment="指标快照JSON")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    def __repr__(self):
        return f"<Signal({self.signal_type}, confidence={self.confidence:.2f})>"


class ReviewModel(Base):
    """复盘记录表"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, nullable=False, comment="关联信号ID")
    actual_outcome = Column(String(20), comment="实际结果: PROFIT/LOSS/BREAKEVEN")
    actual_target_reached = Column(Integer, comment="是否达到目标价: 1/0")
    actual_high = Column(Float, comment="期间最高价")
    actual_low = Column(Float, comment="期间最低价")
    days_held = Column(Integer, comment="持仓天数")
    profit_percent = Column(Float, comment="盈亏百分比")
    review_notes = Column(Text, comment="复盘备注")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    def __repr__(self):
        return f"<Review(signal_id={self.signal_id}, outcome={self.actual_outcome})>"
