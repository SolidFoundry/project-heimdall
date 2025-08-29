#!/usr/bin/env python3
"""
前端测试验证脚本
测试所有前端功能是否正常工作
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8002"

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data['status']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_advertising_api():
    """测试广告API"""
    print("\n🔍 测试广告意图分析API...")
    try:
        payload = {
            "user_input": "我想买一个智能手表，预算2000元",
            "user_id": "test_user_001",
            "session_id": "session_test_001"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/advertising/analyze_intent",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 意图分析成功: {data['detected_intent']} (置信度: {data['intent_confidence']})")
            return True
        else:
            print(f"❌ 意图分析失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 意图分析异常: {e}")
        return False

def test_products_api():
    """测试产品API"""
    print("\n🔍 测试产品API...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/products")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 产品API成功: 获取到 {len(data.get('products', []))} 个产品")
            return True
        else:
            print(f"❌ 产品API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 产品API异常: {e}")
        return False

def test_tools_api():
    """测试工具API"""
    print("\n🔍 测试工具API...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tools")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 工具API成功: 获取到 {data['total_count']} 个工具")
            return True
        else:
            print(f"❌ 工具API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 工具API异常: {e}")
        return False

def test_llm_api():
    """测试LLM API"""
    print("\n🔍 测试LLM API...")
    try:
        payload = {
            "messages": [{"role": "user", "content": "你好"}],
            "session_id": "test_session_001"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/test/llm",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LLM API成功: {data['model']}")
            return True
        else:
            print(f"❌ LLM API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LLM API异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始前端功能测试...")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_tools_api,
        test_llm_api,
        test_advertising_api,
        test_products_api
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            failed += 1
        
        time.sleep(1)  # 避免请求过快
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！前端功能正常工作")
        print("\n📖 访问前端界面: http://localhost:8002")
        print("📖 API文档: http://localhost:8002/docs")
    else:
        print("⚠️ 部分测试失败，请检查服务器状态")
    
    return failed == 0

if __name__ == "__main__":
    main()