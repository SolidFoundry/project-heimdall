# 文件路径: src/heimdall/main.py
# 企业级AI意图广告引擎 - 架构重构版本

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

# ===================================================================
# 1. 在任何其他应用代码之前，立即配置日志系统
# ===================================================================
from heimdall.core.logging_config import setup_logging

setup_logging()

# ===================================================================
# 2. 导入企业级模块
# ===================================================================
from heimdall.core.database import engine, Base
from heimdall.api.endpoints import analysis, testing, advertising
from heimdall.api.endpoints.enterprise_recommendations import router as enterprise_router
from heimdall.api.endpoints.hybrid_recommendations import router as hybrid_router
from heimdall.core.middleware import CtxTimingMiddleware
from heimdall.core.structured_logging import RequestIdMiddleware
from heimdall.core.utils import limiter
from heimdall.core.telemetry import setup_telemetry

# 企业级安全、配置、监控、错误处理
from heimdall.core.security import setup_security_middleware, get_current_user
from heimdall.core.config_manager import config_manager, load_config
from heimdall.core.monitoring import monitoring_manager
from heimdall.core.error_handling import setup_error_handling, error_handler

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# 获取一个已经配置好的logger实例
logger = logging.getLogger(__name__)


# ===================================================================
# 3. 后台任务与应用生命周期管理
# ===================================================================
async def heartbeat_task():
    """一个后台任务，每小时打印一次心跳日志。"""
    heartbeat_logger = logging.getLogger("heimdall.heartbeat")
    while True:
        heartbeat_logger.info("心跳: 海姆达尔服务正在运行...")
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """企业级FastAPI应用生命周期管理器。"""
    # === 应用启动时执行 ===
    logger.info("🚀 启动企业级海姆达尔应用...")
    
    # 1. 加载配置
    try:
        config = load_config()
        logger.info(f"✅ 配置加载成功 - 环境: {config.environment}")
    except Exception as e:
        logger.error(f"❌ 配置加载失败: {e}")
        raise
    
    # 2. 初始化数据库
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ 数据库表已检查并成功创建。")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        logger.info("⚠️  应用将在无数据库模式下运行，部分功能可能不可用。")

    # 3. 初始化监控系统
    try:
        monitoring_manager.setup_monitoring(app)
        logger.info("✅ 监控系统已初始化。")
    except Exception as e:
        logger.error(f"❌ 监控系统初始化失败: {e}")

    # 4. 初始化遥测系统
    try:
        setup_telemetry(app)
        logger.info("✅ 遥测系统已初始化。")
    except Exception as e:
        logger.warning(f"⚠️  遥测系统初始化失败: {e}")

    # 5. 启动后台任务
    heartbeat = asyncio.create_task(heartbeat_task())
    logger.info("✅ 心跳日志后台任务已启动。")

    logger.info("🎉 企业级海姆达尔应用启动完成！")
    
    yield  # FastAPI应用在此处运行

    # === 应用关闭时执行 ===
    logger.info("🔄 正在关闭企业级海姆达尔应用...")
    
    # 1. 停止后台任务
    heartbeat.cancel()
    try:
        await heartbeat
    except asyncio.CancelledError:
        logger.info("✅ 心跳日志后台任务已成功取消。")
    
    # 2. 生成错误报告
    try:
        from heimdall.core.error_handling import ErrorReporter
        error_report = ErrorReporter.generate_error_report()
        logger.info(f"📊 错误统计: {error_report['total_errors']} 个错误")
    except Exception as e:
        logger.error(f"❌ 生成错误报告失败: {e}")
    
    logger.info("✅ 企业级海姆达尔应用已成功关闭。")


# ===================================================================
# 4. 应用工厂函数
# ===================================================================
def create_app() -> FastAPI:
    """创建并配置企业级FastAPI应用实例。"""
    app = FastAPI(
        title="Project Heimdall - AI Intent Advertising Engine",
        description="企业级AI意图识别与广告推荐引擎，具备完整的安全、监控、错误处理能力。",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # 将limiter实例的状态与app关联
    app.state.limiter = limiter

    # 企业级中间件配置 (顺序很重要，外层先添加)
    
    # 1. 错误处理中间件 (最外层，捕获所有异常)
    setup_error_handling(app)
    
    # 2. 安全中间件 (认证、授权、输入验证、安全头部)
    setup_security_middleware(app)
    
    # 3. 速率限制中间件
    app.add_middleware(SlowAPIMiddleware)
    
    # 4. 请求追踪中间件
    app.add_middleware(RequestIdMiddleware)
    
    # 5. 性能监控中间件
    app.add_middleware(CtxTimingMiddleware)
    
    logger.info("✅ 企业级中间件栈已配置完成。")

    # 挂载路由
    app.include_router(analysis.router, prefix="/api/v1")
    app.include_router(testing.router, prefix="/api/v1")
    app.include_router(advertising.router)
    app.include_router(enterprise_router)
    app.include_router(hybrid_router)
    logger.info("✅ 路由挂载完成。")

    # 企业级异常处理器
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        logger.warning(f"速率限制触发: {exc.detail}")
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "type": "rate_limit_error",
                    "message": f"请求过于频繁: {exc.detail}",
                    "retry_after": 60
                },
                "request_id": getattr(request.state, 'request_id', 'N/A')
            },
        )

    # 增强的健康检查端点
    @app.get("/", tags=["健康检查"])
    async def read_root(request: Request):
        """根路径健康检查"""
        logger.info("根路径健康检查请求", extra={"request_id": request.state.request_id})
        return {
            "status": "ok", 
            "project": "Heimdall",
            "version": "1.0.0",
            "environment": config_manager.get_config().environment.value,
            "request_id": request.state.request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @app.get("/health", tags=["健康检查"])
    async def health_check(request: Request):
        """详细的企业级健康检查"""
        logger.info("详细健康检查请求", extra={"request_id": request.state.request_id})
        
        from datetime import datetime
        config = config_manager.get_config()
        
        # 收集各组件健康状态
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request.state.request_id,
            "version": "1.0.0",
            "environment": config.environment.value,
            "components": {
                "database": "unknown",
                "redis": "unknown", 
                "monitoring": "unknown",
                "security": "unknown",
                "logging": "unknown"
            },
            "metrics": {
                "uptime": "unknown",
                "memory_usage": "unknown",
                "cpu_usage": "unknown",
                "error_count": "unknown"
            }
        }
        
        # 检查各组件状态
        try:
            # 数据库检查
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
                health_status["components"]["database"] = "healthy"
        except Exception as e:
            health_status["components"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        # 监控系统检查
        try:
            metrics = monitoring_manager.metrics_collector.get_system_metrics()
            health_status["components"]["monitoring"] = "healthy"
            health_status["metrics"].update(metrics)
        except Exception as e:
            health_status["components"]["monitoring"] = f"unhealthy: {str(e)}"
        
        # 安全系统检查
        try:
            # 检查安全配置
            security_config = config.security
            if security_config.secret_key.get_secret_value():
                health_status["components"]["security"] = "healthy"
            else:
                health_status["components"]["security"] = "degraded: missing secret key"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["security"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        # 错误统计
        try:
            error_stats = error_handler.get_error_stats()
            health_status["metrics"]["error_count"] = error_stats["total_errors"]
            if error_stats["total_errors"] > 100:
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["metrics"]["error_count"] = f"unknown: {str(e)}"
        
        logger.info("健康检查完成", extra={"request_id": request.state.request_id})
        return health_status

    # 企业级信息端点
    @app.get("/info", tags=["系统信息"])
    async def system_info(request: Request):
        """系统信息端点"""
        logger.info("系统信息请求", extra={"request_id": request.state.request_id})
        
        config = config_manager.get_config()
        return {
            "application": {
                "name": "Project Heimdall",
                "version": "1.0.0",
                "description": "企业级AI意图广告引擎",
                "environment": config.environment.value
            },
            "architecture": {
                "framework": "FastAPI",
                "database": "PostgreSQL + SQLAlchemy",
                "cache": "Redis",
                "monitoring": "Prometheus + Custom",
                "security": "JWT + Rate Limiting + Input Validation"
            },
            "features": [
                "AI意图识别",
                "广告推荐引擎", 
                "实时会话管理",
                "工具调用能力",
                "分布式追踪",
                "企业级监控",
                "自动错误恢复"
            ],
            "request_id": request.state.request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    logger.info("✅ 企业级应用配置完成。")
    return app


# ===================================================================
# 5. 创建并导出应用实例
# ===================================================================
app = create_app()