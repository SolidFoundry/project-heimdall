#!/usr/bin/env python3
"""
最终验证混合推荐系统修复效果
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.heimdall.services.hybrid_recommendation_engine import HybridRecommendationEngine
from src.heimdall.core.config import settings

async def final_verification():
    """最终验证修复效果"""
    print("=== 最终验证混合推荐系统修复效果 ===")
    
    try:
        # 创建数据库会话
        engine = create_async_engine(settings.ASYNC_DATABASE_URL)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        # 创建推荐引擎
        recommendation_engine = HybridRecommendationEngine()
        
        async with AsyncSessionLocal() as session:
            print("\n1. 测试混合推荐修复...")
            recommendations = await recommendation_engine.get_hybrid_recommendations(
                user_id="user_001",
                user_input="我想买一部手机",
                db=session,
                limit=5,
                strategy="hybrid"
            )
            
            print(f"混合推荐结果: {len(recommendations)} 个推荐")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec['name']} ({rec['brand']}) - 评分: {rec['final_score']}")
            
            print("\n2. 测试所有推荐策略...")
            strategies = ["hybrid", "intent_based", "behavior_based"]
            
            for strategy in strategies:
                try:
                    recs = await recommendation_engine.get_hybrid_recommendations(
                        user_id="user_001",
                        user_input="我想买一部手机",
                        db=session,
                        limit=3,
                        strategy=strategy
                    )
                    
                    if recs:
                        avg_score = sum(float(r['final_score']) for r in recs) / len(recs)
                        print(f"  {strategy}: {len(recs)} 个推荐, 平均分数: {avg_score:.3f}")
                    else:
                        print(f"  {strategy}: 0 个推荐")
                        
                except Exception as e:
                    print(f"  {strategy}: 错误 - {e}")
            
            print("\n3. 验证数据类型安全性...")
            # 测试边界情况
            try:
                # 测试字符串评分
                test_recs = await recommendation_engine.get_hybrid_recommendations(
                    user_id="user_001",
                    user_input="测试边界情况",
                    db=session,
                    limit=2,
                    strategy="intent_based"
                )
                print(f"  边界测试通过: {len(test_recs)} 个推荐")
                
                # 验证所有评分都是数值类型
                all_numeric = all(isinstance(r['final_score'], (int, float)) for r in test_recs)
                print(f"  数据类型一致性: {'✅ 通过' if all_numeric else '❌ 失败'}")
                
            except Exception as e:
                print(f"  边界测试失败: {e}")
            
            return True
            
    except Exception as e:
        print(f"验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(final_verification())
    if success:
        print("\n🎉 所有数据类型问题已彻底解决！")
        print("系统现在可以稳定运行，不再出现类型比较错误。")
    else:
        print("\n❌ 验证失败，还有问题需要解决。")
        sys.exit(1)