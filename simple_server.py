#!/usr/bin/env python3
"""
最简单的服务器测试脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['PYTHONPATH'] = str(project_root)

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    import uvicorn
    
    # 创建简单的FastAPI应用
    app = FastAPI(title="Project Heimdall Test Server")
    
    @app.get("/")
    async def root():
        return {"message": "Project Heimdall 服务器正常运行", "status": "healthy"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "message": "系统正常"}
    
    @app.get("/enterprise")
    async def enterprise():
        return HTMLResponse("""
        <html>
            <head><title>Project Heimdall - 企业级推荐系统</title></head>
            <body>
                <h1>🎯 Project Heimdall 企业级推荐系统</h1>
                <p>服务器运行正常！</p>
                <p><a href="/docs">API文档</a></p>
                <p><a href="/health">健康检查</a></p>
            </body>
        </html>
        """)
    
    print("=== 启动 Project Heimdall 测试服务器 ===")
    print("服务器地址:")
    print("  - 主页: http://localhost:8003/")
    print("  - 企业级界面: http://localhost:8003/enterprise")
    print("  - API文档: http://localhost:8003/docs")
    print("  - 健康检查: http://localhost:8003/health")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("正在安装缺少的依赖...")
    os.system("pip install fastapi uvicorn")
    sys.exit(1)
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)