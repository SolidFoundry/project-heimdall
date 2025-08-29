# 测试用的heimdall启动文件，包含测试接口 (数据库版本)
import logging
from fastapi import FastAPI
from heimdall.api.endpoints import analysis
from heimdall.api.endpoints.testing_db import router as testing_router

# 导入数据库和日志配置
from heimdall.py_ai_core.core.database import engine, Base
from heimdall.py_ai_core.logging_config import setup_logging
from sqlalchemy.exc import SQLAlchemyError

# 配置日志系统
setup_logging()

# 获取配置好的logger
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Project Heimdall - AI Intent Advertising Engine (DB Version)",
    description="一个用于洞察用户意图并提供精准广告推荐的AI引擎原型。(数据库版本)",
    version="0.2.0"
)

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("正在启动应用...")
    
    try:
        # 创建数据库表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表已成功创建")
    except SQLAlchemyError as e:
        logger.error("数据库表创建失败: %s", e)
        raise
    except Exception as e:
        logger.error("应用启动失败: %s", e)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("正在关闭应用...")

# 挂载路由
app.include_router(analysis.router, prefix="/api/v1", tags=["意图分析"])
app.include_router(testing_router, prefix="/api/v1", tags=["测试接口"])

@app.get("/", tags=["健康检查"])
async def read_root():
    """根路径，用于简单的健康检查。"""
    return {"status": "ok", "project": "Heimdall", "version": "0.2.0"}

if __name__ == "__main__":
    import uvicorn
    logger.info("启动服务器...")
    uvicorn.run("test_main_db:app", host="0.0.0.0", port=8001, reload=True)