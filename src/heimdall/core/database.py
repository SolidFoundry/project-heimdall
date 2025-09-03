# ===================================================================
# 海姆达尔数据库配置模块
# ===================================================================
# 该模块配置了 SQLAlchemy 异步数据库连接，包括：
# - 异步引擎创建
# - 会话工厂配置
# - 声明式基类定义
# - FastAPI 依赖注入函数
# ===================================================================

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from .config import settings


# 1. 创建异步数据库引擎
#    - Engine 是任何 SQLAlchemy 应用的起点
#    - 管理数据库连接池和 DBAPI 连接
#    - echo=True 会打印所有执行的 SQL 语句，便于调试
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,  # 从配置获取异步数据库连接字符串
    echo=settings.DEBUG,          # 调试模式时显示 SQL，生产环境自动关闭
    pool_size=20,                 # 连接池大小
    max_overflow=30,              # 最大溢出连接数
    pool_pre_ping=True,           # 连接前检查连接是否有效
    pool_recycle=3600,            # 连接回收时间（秒）
)


# 2. 创建异步会话工厂
#    - sessionmaker 是用于创建 Session 对象的工厂
#    - 每个请求都会使用工厂创建一个新的会话
#    - expire_on_commit=False 是 FastAPI 推荐设置，避免提交后对象过期
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,      # 不自动提交
    autoflush=False,       # 不自动刷新
    bind=engine,           # 绑定到引擎
    class_=AsyncSession,   # 使用异步会话类
    expire_on_commit=False, # 提交后对象不过期
)


# 3. 创建声明式基类
#    - 所有数据库模型类都将继承这个基类
#    - 允许 SQLAlchemy 将 Python 类映射到数据库表
#    - 提供了 ORM 功能的核心
Base = declarative_base()


# 4. FastAPI 依赖注入函数
#    用于在 API 端点中获取数据库会话
#    确保每个请求使用独立的会话，并在请求结束后自动关闭
async def get_db() -> AsyncSession:
    """获取数据库会话的依赖函数
    
    这是一个 FastAPI 依赖注入函数，用于为每个 API 请求提供一个独立的数据库会话。
    使用上下文管理器确保会话在使用后正确关闭。
    
    Yields:
        AsyncSession: 异步数据库会话对象
        
    Note:
        - 每个请求都会获得一个新的会话
        - 请求结束后会自动关闭会话
        - 使用 yield 语句支持异步上下文管理
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ===================================================================
# 使用说明：
# 1. 在 FastAPI 路由中，通过依赖注入使用数据库会话：
#    @app.get("/items/")
#    async def read_items(db: AsyncSession = Depends(get_db)):
#        pass
#
# 2. 在模型文件中，继承 Base 类创建数据库模型：
#    class User(Base):
#        __tablename__ = "users"
#        id = Column(Integer, primary_key=True)
#
# 3. 创建数据库表：
#    async with engine.begin() as conn:
#        await conn.run_sync(Base.metadata.create_all)
# ===================================================================