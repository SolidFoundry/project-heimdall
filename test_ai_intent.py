#!/usr/bin/env python3
"""
AI意图分析功能演示脚本
测试混合推荐系统的AI意图识别能力
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:8002"
API_BASE = f"{BASE_URL}/api/v1"

async def test_hybrid_recommendations():
    """测试混合推荐功能"""
    print("=== AI意图分析混合推荐系统测试 ===\n")
    
    # 测试用例
    test_cases = [
        {
            "name": "笔记本电脑购买需求",
            "user_input": "我想买一台性价比高的笔记本电脑，主要用来办公，预算在5000元左右",
            "user_id": "user_001",
            "strategy": "hybrid"
        },
        {
            "name": "蓝牙耳机需求",
            "user_input": "推荐一款适合运动的蓝牙耳机，要求降噪效果好，价格不要太贵",
            "user_id": "user_002", 
            "strategy": "intent_based"
        },
        {
            "name": "手机升级需求",
            "user_input": "我想换个新手机，预算在8000左右，喜欢拍照和玩游戏",
            "user_id": "user_003",
            "strategy": "behavior_based"
        },
        {
            "name": "智能手表需求",
            "user_input": "有什么好的智能手表推荐吗？主要用来监测健康和运动",
            "user_id": "user_004",
            "strategy": "hybrid"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"--- 测试用例 {i}: {test_case['name']} ---")
            print(f"用户输入: {test_case['user_input']}")
            print(f"用户ID: {test_case['user_id']}")
            print(f"推荐策略: {test_case['strategy']}")
            
            try:
                # 调用混合推荐API
                async with session.post(
                    f"{API_BASE}/hybrid-recommendations/recommendations",
                    json={
                        "user_id": test_case["user_id"],
                        "user_input": test_case["user_input"],
                        "session_id": f"test_session_{i}",
                        "limit": 5,
                        "strategy": test_case["strategy"]
                    },
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # 显示AI意图分析结果
                        if data.get("intent_analysis"):
                            intent = data["intent_analysis"]
                            print(f"\n[AI] AI意图分析:")
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
                        
                        # 显示用户画像
                        if data.get("behavior_profile"):
                            profile = data["behavior_profile"]
                            print(f"\n[用户] 用户画像:")
                            print(f"  总行为数: {profile.get('total_behaviors', 0)}")
                            
                            if profile.get('category_preferences'):
                                top_categories = list(profile['category_preferences'].items())[:3]
                                print(f"  偏好类别: {', '.join([f'{cat}({score})' for cat, score in top_categories])}")
                            
                            if profile.get('brand_preferences'):
                                top_brands = list(profile['brand_preferences'].items())[:3]
                                print(f"  偏好品牌: {', '.join([f'{brand}({score})' for brand, score in top_brands])}")
                        
                        # 显示推荐结果
                        recommendations = data.get("recommendations", [])
                        if recommendations:
                            print(f"\n[推荐] 推荐结果 (共{len(recommendations)}个):")
                            for j, rec in enumerate(recommendations, 1):
                                print(f"  {j}. {rec['name']} - {rec['brand']}")
                                print(f"     价格: ¥{rec['price']}")
                                print(f"     类别: {rec['category']}")
                                print(f"     推荐分数: {rec['final_score']}")
                                print(f"     推荐理由: {rec['recommendation_reason']}")
                                print()
                        else:
                            print("\n[错误] 暂无推荐结果")
                            
                    else:
                        error_text = await response.text()
                        print(f"[错误] 请求失败: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"[错误] 测试失败: {e}")
            
            print("-" * 60)
            print()

async def test_intent_analysis_only():
    """测试纯意图分析功能"""
    print("=== 纯AI意图分析测试 ===\n")
    
    test_inputs = [
        "我想买一台新的 MacBook Pro",
        "推荐一款适合跑步的无线耳机",
        "我想换个手机，预算3000左右",
        "有什么好的平板电脑推荐吗？",
        "我想买智能手表用来监测健康"
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, user_input in enumerate(test_inputs, 1):
            print(f"--- 意图分析测试 {i} ---")
            print(f"用户输入: {user_input}")
            
            try:
                async with session.post(
                    f"{API_BASE}/hybrid-recommendations/analyze-intent",
                    json={
                        "user_input": user_input,
                        "user_id": f"test_user_{i}",
                        "session_id": f"intent_test_{i}"
                    },
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        intent_analysis = data["intent_analysis"]
                        
                        print(f"[成功] 意图识别结果:")
                        print(f"  意图类型: {intent_analysis.get('intent_type', '未知')}")
                        print(f"  置信度: {(intent_analysis.get('confidence', 0) * 100):.1f}%")
                        print(f"  紧急程度: {(intent_analysis.get('urgency_level', 0) * 100):.1f}%")
                        print(f"  价格偏好: {intent_analysis.get('price_range', '中等')}")
                        
                        if intent_analysis.get('product_categories'):
                            print(f"  偏好类别: {', '.join(intent_analysis['product_categories'])}")
                        
                        if intent_analysis.get('brand_preferences'):
                            print(f"  品牌偏好: {', '.join(intent_analysis['brand_preferences'])}")
                        
                        if intent_analysis.get('keywords'):
                            print(f"  关键词: {', '.join(intent_analysis['keywords'])}")
                        
                        if intent_analysis.get('analysis_summary'):
                            print(f"  分析总结: {intent_analysis['analysis_summary']}")
                            
                    else:
                        error_text = await response.text()
                        print(f"[错误] 请求失败: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"[错误] 测试失败: {e}")
            
            print("-" * 40)
            print()

async def main():
    """主测试函数"""
    print("开始测试AI意图分析混合推荐系统")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务器地址: {BASE_URL}")
    print("=" * 60)
    
    # 测试混合推荐功能
    await test_hybrid_recommendations()
    
    # 测试纯意图分析功能
    await test_intent_analysis_only()
    
    print("所有测试完成！")
    print("\n您可以访问以下URL体验完整功能:")
    print(f"  - 企业级系统: {BASE_URL}/enterprise")
    print(f"  - API文档: {BASE_URL}/docs")
    print(f"  - 健康检查: {BASE_URL}/health")

if __name__ == "__main__":
    asyncio.run(main())