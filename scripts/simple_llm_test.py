#!/usr/bin/env python3
"""
简化版大模型服务测试
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.heimdall.services.llm_service import llm_service
from src.heimdall.core.config import settings

async def test_llm_simple():
    """简单测试大模型服务"""
    print("=== 测试大模型服务 ===")
    
    try:
        # 检查配置
        print(f"API Key存在: {bool(settings.OPENAI_API_KEY)}")
        print(f"API Base: {settings.OPENAI_API_BASE}")
        print(f"Model Name: {settings.MODEL_NAME}")
        
        # 测试简单对话
        messages = [
            {"role": "user", "content": "你好，请简单回答1+1等于多少"}
        ]
        
        response = await llm_service.get_summary_from_tool_results(messages)
        print(f"LLM响应: {response}")
        print("大模型服务测试成功!")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llm_simple())
    print(f"测试结果: {'成功' if success else '失败'}")