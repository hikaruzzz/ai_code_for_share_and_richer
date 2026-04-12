"""
新闻数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, UniqueConstraint
from app.db.database import Base


class NewsModel(Base):
    """新闻数据表"""
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, comment="新闻标题")
    content = Column(Text, comment="新闻内容")
    source = Column(String(100), comment="新闻来源")
    url = Column(String(1000), comment="新闻链接")
    sentiment = Column(Float, comment="情感得分 (-1到1)")
    relevance_score = Column(Float, comment="相关度得分")
    published_at = Column(DateTime, index=True, comment="发布时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    __table_args__ = (
        UniqueConstraint('url', name='uix_news_url'),
    )

    def __repr__(self):
        return f"<News({self.title[:30]}..., sentiment={self.sentiment})>"
