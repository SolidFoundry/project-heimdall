#!/usr/bin/env python3
"""
简化的服务器启动脚本
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
    from src.heimdall.main import app
    import uvicorn
    
    print("=== 启动 Project Heimdall 服务器 ===")
    print("服务器地址:")
    print("  - 主页: http://localhost:8003/")
    print("  - 企业级界面: http://localhost:8003/enterprise")
    print("  - 测试平台: http://localhost:8003/test")
    print("  - API文档: http://localhost:8003/docs")
    print("  - 健康检查: http://localhost:8003/health")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info",
        reload=False
    )
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖都已安装")
    sys.exit(1)
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)