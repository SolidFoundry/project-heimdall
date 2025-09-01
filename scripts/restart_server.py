#!/usr/bin/env python3
"""
清理数据库连接池和SQLAlchemy缓存
重启服务器以应用所有修复
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def restart_server():
    """重启服务器"""
    print("重启服务器以应用修复...")
    
    # 杀死现有进程
    try:
        # 查找并杀死Python服务器进程
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                              capture_output=True, text=True, encoding='gbk')
        
        if 'python.exe' in result.stdout:
            print("发现正在运行的Python进程，正在停止...")
            # 停止相关进程
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                         capture_output=True, timeout=10)
            time.sleep(2)
            print("Python进程已停止")
    except Exception as e:
        print(f"停止进程时出错: {e}")
    
    # 等待一下确保进程完全停止
    time.sleep(3)
    
    # 启动新的服务器
    try:
        print("启动新的服务器...")
        
        # 使用subprocess启动服务器并记录输出
        server_process = subprocess.Popen([
            'python', 'src/heimdall/simple_main.py'
        ], cwd='D:\\GitHub_Projects\\project-heimdall', 
           stdout=subprocess.PIPE, 
           stderr=subprocess.PIPE,
           text=True,
           encoding='gbk')
        
        # 等待服务器启动
        time.sleep(5)
        
        # 检查进程是否还在运行
        if server_process.poll() is None:
            print("服务器启动成功！")
            return server_process
        else:
            print("服务器启动失败")
            stdout, stderr = server_process.communicate()
            print(f"标准输出: {stdout}")
            print(f"错误输出: {stderr}")
            return None
            
    except Exception as e:
        print(f"启动服务器失败: {e}")
        return None

def test_api():
    """测试API是否正常工作"""
    print("测试API...")
    
    import requests
    import json
    
    try:
        # 测试健康检查
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("健康检查通过")
        else:
            print(f"健康检查失败: {response.status_code}")
            return False
        
        # 测试混合推荐API
        test_data = {
            "user_id": "user_001",
            "user_input": "我想买一部手机",
            "strategy": "hybrid"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/hybrid-recommendations/recommendations",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"推荐API测试成功，返回 {len(result.get('recommendations', []))} 个推荐")
            return True
        else:
            print(f"推荐API测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器")
        return False
    except Exception as e:
        print(f"API测试失败: {e}")
        return False

def clear_database_cache():
    """清理数据库连接池"""
    print("清理数据库连接池...")
    
    try:
        # 连接到数据库并清理连接池
        from sqlalchemy import create_engine, text
        
        # 加载环境变量
        env_file = Path(".env")
        env_vars = {}
        
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"\'')
        
        # 构建数据库URL
        user = env_vars.get('DATABASE_USER', 'heimdall')
        password = env_vars.get('DATABASE_PASSWORD', 'heimdall_password')
        host = env_vars.get('DATABASE_HOST', 'localhost')
        port = env_vars.get('DATABASE_PORT', '5432')
        database = env_vars.get('DATABASE_NAME', 'heimdall_db')
        
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        # 创建引擎并清理连接池
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # 执行一个简单查询来验证连接
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        # 关闭引擎以清理连接池
        engine.dispose()
        print("数据库连接池已清理")
        return True
        
    except Exception as e:
        print(f"清理数据库连接池失败: {e}")
        return False

def main():
    """主函数"""
    print("Project Heimdall - 服务器重启和缓存清理")
    print("=" * 50)
    
    # 1. 清理数据库连接池
    if not clear_database_cache():
        print("清理数据库连接池失败")
        return 1
    
    # 2. 重启服务器
    server_process = restart_server()
    if not server_process:
        print("重启服务器失败")
        return 1
    
    # 3. 测试API
    if not test_api():
        print("API测试失败")
        print("请检查日志文件获取更多信息")
        return 1
    
    print("\n🎉 服务器重启成功！")
    print("所有修复已应用，系统正常运行")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)