# 测试用的heimdall启动文件，包含测试接口
import logging
from fastapi import FastAPI
from heimdall.api.endpoints import analysis, testing

# 配置基础日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Project Heimdall - AI Intent Advertising Engine",
    description="一个用于洞察用户意图并提供精准广告推荐的AI引擎原型。",
    version="0.1.0"
)

# 挂载路由
app.include_router(analysis.router, prefix="/api/v1", tags=["意图分析"])
app.include_router(testing.router, prefix="/api/v1", tags=["测试接口"])

@app.get("/", tags=["健康检查"])
async def read_root():
    """根路径，用于简单的健康检查。"""
    return {"status": "ok", "project": "Heimdall"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_main:app", host="0.0.0.0", port=8001, reload=True)