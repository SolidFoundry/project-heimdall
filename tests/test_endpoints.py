#!/usr/bin/env python3
# 测试脚本：验证新添加的测试接口

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"

def test_endpoint(url, method="GET", data=None, headers=None):
    """测试API端点"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        print(f"测试 {method} {url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
        
        print("-" * 50)
        return response.status_code == 200
        
    except Exception as e:
        print(f"请求失败: {e}")
        print("-" * 50)
        return False

def main():
    """主测试函数"""
    print("开始测试 Project Heimdall 测试接口")
    print("=" * 50)
    
    # 测试健康检查
    print("1. 测试健康检查...")
    test_endpoint(f"{BASE_URL}/")
    
    # 测试现有的分析接口
    print("2. 测试现有的分析接口...")
    analysis_data = {
        "user_id": "test_user",
        "session_id": "test_session", 
        "browsing_history": ["https://example.com/product/laptop"]
    }
    test_endpoint(f"{BASE_URL}/api/v1/analyze", method="POST", data=analysis_data)
    
    # 测试新的工具列表接口
    print("3. 测试工具列表接口...")
    test_endpoint(f"{BASE_URL}/api/v1/tools")
    
    # 测试大模型测试接口
    print("4. 测试大模型测试接口...")
    llm_data = {
        "prompt": "你好，请介绍一下你自己",
        "system_prompt": "你是一个专业的AI助手",
        "temperature": 0.7
    }
    test_endpoint(f"{BASE_URL}/api/v1/llm-test", method="POST", data=llm_data)
    
    # 测试工具调用接口
    print("5. 测试工具调用接口...")
    tool_data = {
        "tool_name": "calculate",
        "tool_args": {"expression": "2 + 2 * 3"}
    }
    test_endpoint(f"{BASE_URL}/api/v1/tool-test", method="POST", data=tool_data)
    
    # 测试大模型带工具调用接口
    print("6. 测试大模型带工具调用接口...")
    test_endpoint(f"{BASE_URL}/api/v1/llm-with-tools", method="POST", data="请帮我计算 2 的 10 次方是多少？")
    
    # 测试天气查询
    print("7. 测试天气查询...")
    test_endpoint(f"{BASE_URL}/api/v1/llm-with-tools", method="POST", data="北京今天天气怎么样？")
    
    # 测试时间查询
    print("8. 测试时间查询...")
    test_endpoint(f"{BASE_URL}/api/v1/llm-with-tools", method="POST", data="现在几点了？")
    
    print("测试完成！")

if __name__ == "__main__":
    main()