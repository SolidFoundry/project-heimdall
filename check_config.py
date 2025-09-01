#!/usr/bin/env python3
"""
配置检查脚本 - 诊断AI意图分析失败问题
检查数据库连接、API密钥等关键配置
"""

import os
import sys
import requests
from datetime import datetime


def check_environment_variables():
    """检查环境变量配置"""
    print("🔍 检查环境变量配置...")
    print("=" * 50)

    required_vars = [
        "OPENAI_API_KEY",
        "OPENAI_API_BASE",
        "MODEL_NAME",
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
    ]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if "PASSWORD" in var or "KEY" in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: 未设置")
            missing_vars.append(var)

    if missing_vars:
        print(f"\n⚠️  缺少 {len(missing_vars)} 个必需的环境变量")
        print("   请设置以下环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
    else:
        print("\n✅ 所有必需的环境变量都已设置")

    return len(missing_vars) == 0


def check_database_connection():
    """检查数据库连接"""
    print("\n🔍 检查数据库连接...")
    print("=" * 50)

    try:
        # 尝试导入数据库模块
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
        from heimdall.core.database import get_db
        from heimdall.core.config import settings

        print(f"   ✅ 数据库配置:")
        print(f"      用户: {settings.DATABASE_USER}")
        print(f"      主机: {settings.DATABASE_HOST}")
        print(f"      端口: {settings.DATABASE_PORT}")
        print(f"      数据库: {settings.DATABASE_NAME}")
        print(
            f"      连接字符串: {settings.ASYNC_DATABASE_URL.replace(settings.DATABASE_PASSWORD, '***')}"
        )

        # 注意：这里只是检查配置，不实际连接数据库
        print("   ℹ️  数据库连接测试需要实际运行应用")

    except ImportError as e:
        print(f"   ❌ 无法导入数据库模块: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 数据库配置检查失败: {e}")
        return False

    return True


def check_api_endpoints():
    """检查API端点可访问性"""
    print("\n🔍 检查API端点...")
    print("=" * 50)

    base_url = "http://localhost:8002"
    endpoints = [
        "/api/v1/health",
        "/api/v1/memory/products",
        "/api/v1/hybrid-recommendations/analyze-intent",
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: 正常 (200)")
            else:
                print(f"   ⚠️  {endpoint}: 状态码 {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {endpoint}: 连接失败 (服务器可能未启动)")
        except Exception as e:
            print(f"   ❌ {endpoint}: 错误 - {e}")

    return True


def check_llm_service():
    """检查LLM服务配置"""
    print("\n🔍 检查LLM服务配置...")
    print("=" * 50)

    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
        from heimdall.services.llm_service import llm_service
        from heimdall.core.config import settings

        print(f"   ✅ LLM服务配置:")
        print(
            f"      API密钥: {settings.OPENAI_API_KEY[:8]}..."
            if settings.OPENAI_API_KEY
            else "未设置"
        )
        print(f"      API基础URL: {settings.OPENAI_API_BASE}")
        print(f"      模型名称: {settings.MODEL_NAME}")

        # 检查API密钥格式
        if settings.OPENAI_API_KEY:
            if settings.OPENAI_API_KEY.startswith("sk-"):
                print("   ✅ API密钥格式正确")
            else:
                print("   ⚠️  API密钥格式可能不正确 (应该以'sk-'开头)")
        else:
            print("   ❌ API密钥未设置")

    except ImportError as e:
        print(f"   ❌ 无法导入LLM服务模块: {e}")
        return False
    except Exception as e:
        print(f"   ❌ LLM服务配置检查失败: {e}")
        return False

    return True


def generate_fix_instructions():
    """生成修复指令"""
    print("\n🔧 修复指令")
    print("=" * 50)

    print("1. 创建环境变量文件 (.env):")
    print("   在项目根目录创建 .env 文件，包含以下内容:")
    print("   ")
    print("   # LLM 配置")
    print("   OPENAI_API_KEY=sk-your-actual-api-key-here")
    print("   OPENAI_API_BASE=https://api.openai.com/v1")
    print("   MODEL_NAME=gpt-3.5-turbo")
    print("   ")
    print("   # 数据库配置")
    print("   DATABASE_USER=heimdall")
    print("   DATABASE_PASSWORD=your_actual_password_here")
    print("   DATABASE_HOST=localhost")
    print("   DATABASE_PORT=5432")
    print("   DATABASE_NAME=heimdall_db")

    print("\n2. 启动数据库服务:")
    print("   # 如果使用Docker")
    print("   docker-compose up -d")
    print("   ")
    print("   # 或者启动本地PostgreSQL服务")

    print("\n3. 重启应用服务器:")
    print("   python enhanced_server.py")

    print("\n4. 验证修复:")
    print("   python check_config.py")


def main():
    """主函数"""
    print("🔧 Project Heimdall 配置诊断工具")
    print("=" * 60)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 执行各项检查
    env_ok = check_environment_variables()
    db_ok = check_database_connection()
    api_ok = check_api_endpoints()
    llm_ok = check_llm_service()

    # 总结
    print("\n📊 检查结果总结")
    print("=" * 50)
    print(f"环境变量: {'✅ 正常' if env_ok else '❌ 异常'}")
    print(f"数据库配置: {'✅ 正常' if db_ok else '❌ 异常'}")
    print(f"API端点: {'✅ 正常' if api_ok else '❌ 异常'}")
    print(f"LLM服务: {'✅ 正常' if llm_ok else '❌ 异常'}")

    if not (env_ok and db_ok and llm_ok):
        print("\n❌ 发现问题，请按照以下修复指令操作:")
        generate_fix_instructions()
    else:
        print("\n✅ 所有配置检查通过！")
        print("如果仍有问题，请检查服务器日志获取更多信息。")


if __name__ == "__main__":
    main()
