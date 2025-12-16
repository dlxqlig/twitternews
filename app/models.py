from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String, unique=True, index=True)
    author_name = Column(String)
    author_handle = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Analysis
    relevance_score = Column(Float, default=0.0)
    analysis_summary = Column(Text, nullable=True)
    is_sent_to_telegram = Column(Boolean, default=False)
    
class TwitterList(Base):
    __tablename__ = "twitter_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True)
    name = Column(String, nullable=True)
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    key = Column(String, primary_key=True, index=True)
    value = Column(String)
