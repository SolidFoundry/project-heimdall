#!/usr/bin/env python3
"""
简化的AI意图分析功能测试脚本
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:8002"
API_BASE = f"{BASE_URL}/api/v1"

async def test_simple_intent_analysis():
    """简单的意图分析测试"""
    print("=== AI意图分析测试 ===\n")
    
    async with aiohttp.ClientSession() as session:
        # 测试用例
        user_input = "我想买一台性价比高的笔记本电脑，主要用来办公，预算在5000元左右"
        
        print(f"用户输入: {user_input}")
        print("正在分析...")
        
        try:
            # 调用混合推荐API
            async with session.post(
                f"{API_BASE}/hybrid-recommendations/recommendations",
                json={
                    "user_id": "user_001",
                    "user_input": user_input,
                    "session_id": "test_session_001",
                    "limit": 3,
                    "strategy": "hybrid"
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # 显示AI意图分析结果
                    if data.get("intent_analysis"):
                        intent = data["intent_analysis"]
                        print("\n[AI] AI意图分析结果:")
                        print(f"  意图类型: {intent.get('intent_type', '未知')}")
                        print(f"  置信度: {(intent.get('confidence', 0) * 100):.1f}%")
                        print(f"  紧急程度: {(intent.get('urgency_level', 0) * 100):.1f}%")
                        print(f"  价格偏好: {intent.get('price_range', '中等')}")
                        
                        if intent.get('product_categories'):
                            print(f"  偏好类别: {', '.join(intent['product_categories'])}")
                        
                        if intent.get('keywords'):
                            print(f"  关键词: {', '.join(intent['keywords'])}")
                        
                        if intent.get('analysis_summary'):
                            print(f"  分析总结: {intent['analysis_summary']}")
                    
                    # 显示推荐结果
                    recommendations = data.get("recommendations", [])
                    if recommendations:
                        print(f"\n[推荐] 推荐结果 (共{len(recommendations)}个):")
                        for j, rec in enumerate(recommendations, 1):
                            print(f"  {j}. {rec['name']} - {rec['brand']}")
                            print(f"     价格: {rec['price']}")
                            print(f"     类别: {rec['category']}")
                            print(f"     推荐分数: {rec['final_score']}")
                            print(f"     推荐理由: {rec['recommendation_reason']}")
                    else:
                        print("\n[信息] 暂无推荐结果")
                        
                else:
                    error_text = await response.text()
                    print(f"[错误] 请求失败: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"[错误] 测试失败: {e}")

async def main():
    """主测试函数"""
    print("开始测试AI意图分析混合推荐系统")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务器地址: {BASE_URL}")
    print("=" * 60)
    
    await test_simple_intent_analysis()
    
    print("\n测试完成！")
    print("\n您可以访问以下URL体验完整功能:")
    print(f"  - 企业级系统: {BASE_URL}/enterprise")
    print(f"  - API文档: {BASE_URL}/docs")
    print(f"  - 健康检查: {BASE_URL}/health")

if __name__ == "__main__":
    asyncio.run(main())