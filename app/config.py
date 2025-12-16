from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ADMIN_PASSWORD: str = "admin123"
    
    # Database
    DATABASE_URL: str = "sqlite:////root/work/twitternews/database/automation.db"
    
    # Twitter
    TWITTER_AUTH_TOKEN: str
    TWITTER_CT0_TOKEN: str
    TWITTER_LIST_URLS: str  # Comma separated
    
    # LLM
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    QWEN_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "gemini-1.5-pro"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    
    # Automation
    AUTOMATION_CHECK_INTERVAL_MINUTES: int = 5
    DEFAULT_SCORE_THRESHOLD: float = 0.85
    DEFAULT_PROMPT: str = """
    你是一名精通中英文的科技新闻编辑，需要按照以下步骤处理推文：
    1. 判断推文语言；如果不是中文，请先将整段推文准确翻译成中文，写入 translation 字段，内容以“翻译：”开头。
    2. 基于中文内容分析其与科技、人工智能或加密货币的相关性，给出 0.0~1.0 的评分，写入 score 字段（浮点数）。
    3. 用中文撰写简洁要点，写入 summary 字段，内容以“摘要：”开头。
    4. 仅返回严格的 JSON，字段顺序不限，不要额外文本。
    
    Tweet: {tweet_text}
    
    Output format (JSON):
    {{"score": 0.8, "translation": "翻译：...", "summary": "摘要：..."}}
    """
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
