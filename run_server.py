#!/usr/bin/env python3
"""
Project Heimdall 主服务器启动脚本
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def main():
    """主函数"""
    # 设置项目根目录
    project_root = Path(__file__).parent
    
    # 设置 Python 路径
    python_path = str(project_root / "src")
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] = f"{python_path}:{os.environ['PYTHONPATH']}"
    else:
        os.environ["PYTHONPATH"] = python_path
    
    # 创建日志目录
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 加载环境变量
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"[OK] 已加载环境变量文件: {env_file}")
    
    # 启动服务器
    try:
        print("=== 启动 Project Heimdall 服务器 ===")
        print(f"当前工作目录: {project_root}")
        print(f"Python 路径: {python_path}")
        
        # 导入并运行应用
        from src.heimdall.main import app
        
        # 导入 uvicorn
        import uvicorn
        
        # 启动服务器
        uvicorn.run(
            "src.heimdall.main:app",
            host="0.0.0.0",
            port=8003,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()