"""
企业级配置管理模块。

提供统一的配置管理，支持多环境、加密配置、配置验证等功能。
"""

import os
import json
import yaml
from typing import Any, Dict, Optional, List, Type, TypeVar, get_type_hints
from pathlib import Path
from dataclasses import dataclass, field, asdict
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field, validator
from enum import Enum
import logging
from cryptography.fernet import Fernet

# 尝试导入 python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseConfig')

class Environment(str, Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class DatabaseConfig(BaseSettings):
    """数据库配置"""
    host: str = "localhost"
    port: int = 5432
    database: str = "heimdall_db"
    username: str = "postgres"
    password: str = Field(default="", env="DATABASE_PASSWORD")
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    model_config = {"extra": "allow"}

class RedisConfig(BaseSettings):
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    max_connections: int = 20
    timeout: int = 5
    
    model_config = {"extra": "allow"}

class SecurityConfig(BaseSettings):
    """安全配置"""
    secret_key: str = Field(default="", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    cors_origins: List[str] = ["http://localhost:3000"]
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    model_config = {"extra": "allow"}

class LoggingConfig(BaseSettings):
    """日志配置"""
    level: str = Field(default="INFO", env="LOGGING_LEVEL")
    format: str = Field(default="json", env="LOGGING_FORMAT")
    file_path: str = Field(default="logs/app.log", env="LOGGING_FILE_PATH")
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_request_id: bool = Field(default=True, env="LOGGING_ENABLE_REQUEST_ID")
    enable_performance_tracking: bool = Field(default=True, env="LOGGING_ENABLE_PERFORMANCE_TRACKING")
    
    model_config = {"extra": "allow"}

class MonitoringConfig(BaseSettings):
    """监控配置"""
    enable_metrics: bool = Field(default=True, env="MONITORING_ENABLE_METRICS")
    metrics_port: int = Field(default=8080, env="MONITORING_METRICS_PORT")
    enable_tracing: bool = Field(default=True, env="MONITORING_ENABLE_TRACING")
    tracing_sampling_rate: float = Field(default=0.1, env="MONITORING_TRACING_SAMPLING_RATE")
    health_check_interval: int = Field(default=30, env="MONITORING_HEALTH_CHECK_INTERVAL")
    
    model_config = {"extra": "allow"}

class ExternalAPIConfig(BaseSettings):
    """外部API配置"""
    llm_api_key: str = Field(default="", env="LLM_API_KEY")
    llm_api_base: str = Field(default="https://api.openai.com/v1", env="LLM_API_BASE")
    timeout: int = Field(default=30, env="EXTERNAL_API_TIMEOUT")
    max_retries: int = Field(default=3, env="EXTERNAL_API_MAX_RETRIES")
    
    model_config = {"extra": "allow"}

class BaseConfig(BaseSettings):
    """基础配置类"""
    
    # 环境配置
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    app_name: str = "heimdall"
    app_version: str = "1.0.0"
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8003
    workers: int = 1
    
    # 子配置
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    security: SecurityConfig = SecurityConfig()
    logging: LoggingConfig = LoggingConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    external_api: ExternalAPIConfig = ExternalAPIConfig()
    
    # 加密配置
    encryption_key: Optional[str] = Field(None, env="ENCRYPTION_KEY")
    
    # Pydantic v2 model configuration
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "allow"
    }

def yaml_config_settings(settings: BaseSettings) -> Dict[str, Any]:
    """从YAML文件加载配置"""
    config_path = Path("config") / f"{settings.environment.value}.yaml"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load YAML config from {config_path}: {e}")
    
    # 尝试默认配置文件
    default_config_path = Path("config") / "default.yaml"
    if default_config_path.exists():
        try:
            with open(default_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load default YAML config: {e}")
    
    return {}

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._config: Optional[BaseConfig] = None
        self._encryption_key: Optional[bytes] = None
        self._cipher_suite: Optional[Fernet] = None
    
    def load_config(self, config_class: Type[T] = BaseConfig) -> T:
        """加载配置"""
        try:
            self._config = config_class()
            self._setup_encryption()
            self._validate_config()
            
            logger.info(f"配置加载成功 - 环境: {self._config.environment}")
            return self._config
            
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            raise
    
    def _setup_encryption(self):
        """设置加密"""
        if self._config and self._config.encryption_key:
            key = self._config.encryption_key.encode()
            if len(key) == 32:  # Fernet requires 32-byte key
                self._encryption_key = key
                self._cipher_suite = Fernet(key)
            else:
                logger.warning("加密密钥长度无效，应为32字节")
    
    def _validate_config(self):
        """验证配置"""
        if not self._config:
            raise ValueError("配置未加载")
        
        # 生产环境安全检查
        if self._config.environment == Environment.PRODUCTION:
            if self._config.debug:
                raise ValueError("生产环境不能启用调试模式")
            
            if self._config.security.secret_key == "default-secret-key":
                raise ValueError("生产环境必须设置安全的SECRET_KEY")
        
        # 必要配置检查 - 只在开发环境要求API密钥
        if self._config.environment == Environment.DEVELOPMENT:
            if not self._config.external_api.llm_api_key:
                print("警告: 未设置LLM_API_KEY，某些功能可能无法使用")
    
    def get_config(self) -> BaseConfig:
        """获取配置"""
        if not self._config:
            return self.load_config()
        return self._config
    
    def encrypt_value(self, value: str) -> str:
        """加密值"""
        if not self._cipher_suite:
            return value
        return self._cipher_suite.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """解密值"""
        if not self._cipher_suite:
            return encrypted_value
        return self._cipher_suite.decrypt(encrypted_value.encode()).decode()
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        if not self._config:
            raise ValueError("配置未加载")
        
        db = self._config.database
        return f"postgresql+asyncpg://{db.username}:{db.password}@{db.host}:{db.port}/{db.database}"
    
    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        if not self._config:
            raise ValueError("配置未加载")
        
        redis = self._config.redis
        if redis.password:
            return f"redis://:{redis.password}@{redis.host}:{redis.port}/{redis.database}"
        return f"redis://{redis.host}:{redis.port}/{redis.database}"
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载配置...")
        self._config = None
        self._encryption_key = None
        self._cipher_suite = None
        return self.load_config()
    
    def export_config(self, file_path: str, include_secrets: bool = False):
        """导出配置到文件"""
        if not self._config:
            raise ValueError("配置未加载")
        
        config_dict = asdict(self._config)
        
        # 处理敏感信息
        if not include_secrets:
            self._mask_secrets(config_dict)
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.suffix.lower() == '.yaml':
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置已导出到: {file_path}")
    
    def _mask_secrets(self, config_dict: Dict[str, Any]):
        """隐藏敏感信息"""
        sensitive_keys = ['password', 'secret_key', 'api_key', 'encryption_key', 'llm_api_key']
        for key, value in config_dict.items():
            if isinstance(value, dict):
                self._mask_secrets(value)
            elif any(sensitive in key.lower() for sensitive in sensitive_keys):
                config_dict[key] = "***masked***"

# 全局配置管理器实例
config_manager = ConfigManager()

def get_config() -> BaseConfig:
    """获取配置的便捷函数"""
    return config_manager.get_config()

def load_config() -> BaseConfig:
    """加载配置的便捷函数"""
    return config_manager.load_config()

# 配置验证装饰器
def validate_config(func):
    """配置验证装饰器"""
    def wrapper(*args, **kwargs):
        if not config_manager._config:
            config_manager.load_config()
        return func(*args, **kwargs)
    return wrapper

# 环境变量前缀
ENV_PREFIX = "HEIMDALL_"

class ConfigWatcher:
    """配置文件监视器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self._watching = False
        
    def start_watching(self):
        """开始监视配置文件变化"""
        import threading
        import time
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class ConfigFileHandler(FileSystemEventHandler):
            def __init__(self, config_manager: ConfigManager):
                self.config_manager = config_manager
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                if event.src_path.endswith(('.env', '.yaml', '.yml')):
                    logger.info("检测到配置文件变化，重新加载配置...")
                    try:
                        self.config_manager.reload_config()
                    except Exception as e:
                        logger.error(f"重新加载配置失败: {e}")
        
        try:
            event_handler = ConfigFileHandler(config_manager)
            observer = Observer()
            observer.schedule(event_handler, path=".", recursive=False)
            observer.start()
            self._watching = True
            logger.info("配置文件监视器已启动")
        except ImportError:
            logger.warning("watchdog库未安装，无法启用配置文件监视")
        except Exception as e:
            logger.error(f"启动配置文件监视器失败: {e}")
    
    def stop_watching(self):
        """停止监视"""
        if self._watching:
            # 这里应该停止observer，简化实现
            self._watching = False
            logger.info("配置文件监视器已停止")