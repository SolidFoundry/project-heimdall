# --- START OF FILE heimdall/core/config.py (复用自py_ai_core，针对广告推荐场景优化) ---

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- LLM 配置 ---
    LLM_API_KEY: str
    LLM_API_BASE: str
    MODEL_NAME: str

    # --- 数据库配置 ---
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str

    # --- 会话管理 ---
    MAX_HISTORY_MESSAGES: int = 10
    
    # --- 日志系统的高级配置 ---
    LOG_PAYLOADS: bool = False 

    # --- 应用配置 ---
    DEBUG: bool = True
    APP_NAME: str = "Project Heimdall"
    APP_VERSION: str = "0.1.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001

    # --- Redis配置 (用于限流缓存) ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # --- 默认的系统提示词 (针对广告推荐场景优化) ---
    DEFAULT_SYSTEM_PROMPT: str = (
        "你是一个专业的广告推荐AI助手，专门分析用户行为数据并提供精准的产品推荐。"
        "请根据用户的浏览历史、搜索记录等行为数据，分析其真实需求，并推荐最相关的产品广告。"
        "特别注意：当需要处理数值计算或数据分析时，你必须使用相应的工具来获得精确结果。"
    )

    # --- 心跳配置 ---
    HEARTBEAT_INTERVAL_HOURS: int = 1
    HEARTBEAT_ENABLED: bool = True

    # --- 日志配置 ---
    LOG_LEVEL: str = "INFO"
    JSON_LOGGING: bool = True

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """
        生成异步 SQLAlchemy 数据库连接字符串。
        """
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # model_config 是 Pydantic v2 中用于配置模型行为的地方
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", # 告诉 Pydantic (以及依赖它的Starlette) 用UTF-8读取.env
        extra="ignore" # 忽略额外的环境变量
    )

settings = Settings()

# --- END OF FILE heimdall/core/config.py ---