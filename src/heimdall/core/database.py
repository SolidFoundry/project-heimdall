# heimdall/core/database.py
# 复用自py_ai_core的数据库配置

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from .config import settings

# 1. 创建一个异步的数据库引擎 (Engine)
#    - an Engine is the starting point for any SQLAlchemy application.
#    - It's the "home base" for the actual database and its DBAPI.
#    - echo=True 会打印出所有执行的 SQL 语句，在开发时非常有用，生产环境可以关闭。
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=True,  # 方便调试，可以看到生成的 SQL
)

# 2. 创建一个异步的会话工厂 (Session Factory)
#    - a sessionmaker object is a factory for producing Session objects.
#    - We will use this factory to create new sessions for each request.
#    - `expire_on_commit=False` 是使用 FastAPI 时的推荐设置。
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3. 创建一个声明式的基类 (Declarative Base)
#    - Our database model classes will inherit from this class.
#    - It allows SQLAlchemy to map our Python classes to database tables.
Base = declarative_base()


# 4. 创建一个依赖注入函数，用于在 API 端点中获取数据库会话
#    This is a dependency that we can inject into our FastAPI routes.
async def get_db() -> AsyncSession:
    """
    FastAPI 依赖项，用于获取一个数据库会话。
    它确保每个请求都使用一个独立的会话，并在请求结束后关闭它。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()