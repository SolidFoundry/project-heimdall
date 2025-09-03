# ===================================================================
# 海姆达尔核心配置模块
# ===================================================================
# 该模块定义了应用的所有配置项，使用 Pydantic Settings 进行类型安全的配置管理
# 所有配置项都可以通过环境变量进行设置
# ===================================================================

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """海姆达尔应用配置类
    
    继承自 Pydantic BaseSettings，提供类型安全的配置管理。
    所有配置项都可以通过环境变量或 .env 文件进行设置。
    """
    
    # --- 大语言模型配置 ---
    LLM_API_KEY: str
    """通义千问API密钥"""
    
    LLM_API_BASE: str
    """通义千问API基础URL"""
    
    MODEL_NAME: str
    """使用的模型名称，如 qwen-max"""

    # --- 数据库配置 ---
    DATABASE_USER: str
    """数据库用户名"""
    
    DATABASE_PASSWORD: str
    """数据库密码"""
    
    DATABASE_HOST: str
    """数据库主机地址"""
    
    DATABASE_PORT: int
    """数据库端口"""
    
    DATABASE_NAME: str
    """数据库名称"""

    # --- 会话管理配置 ---
    MAX_HISTORY_MESSAGES: int = 10
    """最大历史消息数量，用于智能截断"""
    
    # --- 日志系统的高级配置 ---
    LOG_PAYLOADS: bool = False 
    """是否记录请求/响应载荷（生产环境建议关闭）"""

    # --- 应用基础配置 ---
    DEBUG: bool = True
    """是否为调试模式"""
    
    APP_NAME: str = "Project Heimdall"
    """应用名称"""
    
    APP_VERSION: str = "0.1.0"
    """应用版本"""
    
    API_HOST: str = "0.0.0.0"
    """API服务监听地址"""
    
    API_PORT: int = 8001
    """API服务端口"""

    # --- Redis配置 (用于限流和缓存) ---
    REDIS_HOST: str = "localhost"
    """Redis服务器地址"""
    
    REDIS_PORT: int = 6379
    """Redis服务器端口"""
    
    REDIS_PASSWORD: str = ""
    """Redis密码（空表示无密码）"""
    
    REDIS_DB: int = 0
    """Redis数据库编号"""

    # --- 默认的系统提示词 (针对广告推荐场景优化) ---
    DEFAULT_SYSTEM_PROMPT: str = (
        "你是一个专业的广告推荐AI助手，专门分析用户行为数据并提供精准的产品推荐。"
        "请根据用户的浏览历史、搜索记录等行为数据，分析其真实需求，并推荐最相关的产品广告。"
        "特别注意：当需要处理数值计算或数据分析时，你必须使用相应的工具来获得精确结果。"
    )
    """AI助手的默认系统提示词，定义了AI的角色和行为准则"""

    # --- 心跳任务配置 ---
    HEARTBEAT_INTERVAL_HOURS: int = 1
    """心跳任务运行间隔（小时）"""
    
    HEARTBEAT_ENABLED: bool = True
    """是否启用心跳任务"""

    # --- 日志配置 ---
    LOG_LEVEL: str = "INFO"
    """日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL"""
    
    JSON_LOGGING: bool = True
    """是否启用JSON格式的结构化日志"""

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """生成异步 SQLAlchemy 数据库连接字符串
        
        Returns:
            str: 格式为 postgresql+asyncpg://user:pass@host:port/db 的连接字符串
        """
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # Pydantic v2 配置
    model_config = SettingsConfigDict(
        env_file=".env",                    # 从 .env 文件加载环境变量
        env_file_encoding="utf-8",          # 使用 UTF-8 编码读取 .env 文件
        extra="ignore"                      # 忽略未在类中定义的环境变量
    )


# 创建全局配置实例
settings = Settings()

# ===================================================================
# 配置使用说明：
# 1. 所有配置项都可以通过环境变量设置
# 2. 优先级：命令行参数 > 环境变量 > .env 文件 > 默认值
# 3. 敏感信息（如密码、API密钥）建议通过环境变量设置
# 4. 开发时可以使用 .env 文件，但不要将其提交到版本控制
# ===================================================================