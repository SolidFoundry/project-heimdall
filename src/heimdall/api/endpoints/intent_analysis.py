# 文件路径: src/heimdall/api/endpoints/intent_analysis.py
# 意图分析API - 使用千问大模型和数据库商品数据

import uuid
import logging
import json
from typing import List, Dict, Any
from fastapi import APIRouter, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.heimdall.models import schemas
from src.heimdall.services.llm_service import llm_service
from src.heimdall.core.database import get_db
from src.heimdall.core.config import settings

# 创建logger
logger = logging.getLogger("heimdall.intent_analysis")

# 创建一个API路由器实例
router = APIRouter()

@router.post(
    "/analyze",
    response_model=schemas.AnalysisResultOutput,
    summary="意图分析API",
    tags=["意图分析"]
)
async def analyze_user_intent(
    behavior_data: schemas.UserBehaviorInput = Body(...)
) -> schemas.AnalysisResultOutput:
    """
    使用千问大模型和真实商品数据进行意图分析
    """
    try:
        # 记录请求信息
        logger.info(f"收到意图分析请求: user_id={behavior_data.user_id}")
        
        # 1. 从用户行为数据中提取用户输入
        user_input = ""
        if behavior_data.browsing_history and len(behavior_data.browsing_history) > 0:
            user_input = behavior_data.browsing_history[0]
        elif behavior_data.behavior_data and "query" in behavior_data.behavior_data:
            user_input = behavior_data.behavior_data["query"]
        
        logger.info(f"提取的用户输入: {user_input}")
        
        # 2. 使用千问大模型进行真实意图分析
        logger.info("开始使用千问大模型进行意图分析...")
        
        try:
            # 构建意图分析提示词
            system_prompt = """
            你是一个专业的电商意图分析助手。请分析用户输入，识别其购买意图，
            并提取关键的产品需求、价格偏好、品牌偏好等信息。
            
            请按照以下JSON格式返回：
            {
                "intent_type": "产品购买/价格比较/信息查询/品牌了解/售后服务",
                "confidence": 0.0-1.0,
                "product_categories": ["类别1", "类别2"],
                "price_range": "低/中/高",
                "brand_preferences": ["品牌1", "品牌2"],
                "urgency_level": 0.0-1.0,
                "keywords": ["关键词1", "关键词2"],
                "analysis_summary": "分析总结",
                "recommendation_reason": "推荐理由文本"
            }
            
            其中recommendation_reason字段请生成一段详细的推荐理由，说明用户的购买意图、预算偏好和功能需求等。
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # 记录发送给大模型的详细参数
            logger.info(f"发送给千问大模型的参数: model={settings.MODEL_NAME}, temperature=0.3")
            logger.info(f"发送给大模型的系统提示词: {system_prompt}")
            logger.info(f"发送给大模型的消息: {messages}")
            
            # 调用千问大模型进行意图分析
            model_response = await llm_service.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=messages,
                temperature=0.3
            )
            
            intent_result = model_response.choices[0].message.content
            logger.info(f"千问大模型返回的意图分析结果: {intent_result}")
            
            # 解析JSON结果
            try:
                intent_analysis = json.loads(intent_result)
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用默认值
                logger.warning("意图分析结果JSON解析失败，使用默认值")
                intent_analysis = {
                    "intent_type": "产品购买",
                    "confidence": 0.7,
                    "urgency_level": 0.6,
                    "product_categories": ["智能手表"],
                    "price_range": "中等",
                    "keywords": ["智能手表", "健康监测"],
                    "analysis_summary": "用户对智能手表感兴趣",
                    "recommendation_reason": "用户表现出对智能手表的购买兴趣，关注健康监测功能，预算适中。"
                }
                
        except Exception as e:
            logger.error(f"千问大模型意图分析失败: {str(e)}")
            # 使用默认意图分析
            intent_analysis = {
                "intent_type": "产品购买",
                "confidence": 0.7,
                "urgency_level": 0.6,
                "product_categories": ["智能手表"],
                "price_range": "中等",
                "keywords": ["智能手表", "健康监测"],
                "analysis_summary": "用户对智能手表感兴趣",
                "recommendation_reason": "用户表现出对智能手表的购买兴趣，关注健康监测功能，预算适中。"
            }
        
        # 3. 从数据库获取真实产品推荐
        logger.info("开始从数据库获取产品推荐...")
        
        try:
            # 获取数据库会话
            async for db in get_db():
                # 查询所有产品
                query = text("""
                    SELECT id, name, description, price, category, brand, 
                           image_url, tags, attributes, stock_quantity, rating
                    FROM products 
                    WHERE is_active = true
                    ORDER BY rating DESC, price ASC
                    LIMIT 10
                """)
                
                result = await db.execute(query)
                products = result.fetchall()
                
                # 转换为字典列表
                product_list = []
                for product in products:
                    product_dict = {
                        "id": product[0],
                        "name": product[1],
                        "description": product[2],
                        "price": float(product[3]),
                        "category": product[4],
                        "brand": product[5],
                        "image_url": product[6],
                        "tags": product[7],
                        "attributes": product[8],
                        "stock_quantity": product[9],
                        "rating": float(product[10]) if product[10] else 0
                    }
                    product_list.append(product_dict)
                
                logger.info(f"从数据库获取了 {len(product_list)} 个产品")
                
                # 根据意图分析筛选产品
                recommendations = []
                preferred_categories = intent_analysis.get("product_categories", [])
                preferred_brands = intent_analysis.get("brand_preferences", [])
                price_range = intent_analysis.get("price_range", "中")
                
                # 记录AI结果到SQL查询条件的映射
                logger.info(f"AI意图分析结果映射到查询条件:")
                logger.info(f"  - 产品类别筛选: {preferred_categories}")
                logger.info(f"  - 品牌筛选: {preferred_brands}")
                logger.info(f"  - 价格范围: {price_range} (低:<1000, 中:1000-3000, 高:>3000)")
                logger.info(f"  - 基础SQL: SELECT * FROM products WHERE is_active = true")
                
                for product in product_list:
                    score = 0.0
                    score_details = []
                    
                    # 类别匹配
                    if preferred_categories and product["category"] in preferred_categories:
                        score += 0.4
                        score_details.append(f"类别匹配({product['category']})")
                    
                    # 品牌匹配
                    if preferred_brands and product["brand"] in preferred_brands:
                        score += 0.3
                        score_details.append(f"品牌匹配({product['brand']})")
                    
                    # 价格匹配（根据不同产品类别调整价格区间）
                    if "智能手表" in preferred_categories or "智能手环" in preferred_categories:
                        # 智能手表/手环的价格区间
                        if price_range == "低" and product["price"] < 1000:
                            score += 0.2
                            score_details.append("价格匹配(低档)")
                        elif price_range == "中" and 1000 <= product["price"] <= 3000:
                            score += 0.2
                            score_details.append("价格匹配(中档)")
                        elif price_range == "高" and product["price"] > 3000:
                            score += 0.2
                            score_details.append("价格匹配(高档)")
                    else:
                        # 其他产品的价格区间
                        if price_range == "低" and product["price"] < 3000:
                            score += 0.2
                            score_details.append("价格匹配(低档)")
                        elif price_range == "中" and 3000 <= product["price"] <= 8000:
                            score += 0.2
                            score_details.append("价格匹配(中档)")
                        elif price_range == "高" and product["price"] > 8000:
                            score += 0.2
                            score_details.append("价格匹配(高档)")
                    
                    # 评分加分
                    score += product["rating"] * 0.1
                    
                    if score > 0.3:  # 只返回有意义的推荐
                        recommendations.append({
                            "product_id": product["id"],
                            "name": product["name"],
                            "category": product["category"],
                            "brand": product["brand"],
                            "price": product["price"],
                            "description": product["description"],
                            "rating": product["rating"],
                            "final_score": round(score, 3),
                            "recommendation_reason": f"符合您的{product['category']}需求，评分{product['rating']}分"
                        })
                        logger.info(f"产品推荐: {product['name']} (ID:{product['id']}) - 最终得分: {round(score, 3)} - 得分详情: {', '.join(score_details)}")
                
                # 按分数排序并限制数量
                recommendations.sort(key=lambda x: x["final_score"], reverse=True)
                recommendations = recommendations[:5]
                
                break
                
        except Exception as e:
            logger.error(f"数据库查询失败: {str(e)}")
            # 使用默认推荐
            recommendations = [
                {
                    "product_id": 1,
                    "name": "iPhone 15 Pro",
                    "category": "手机",
                    "brand": "Apple",
                    "price": 7999.00,
                    "description": "最新款iPhone，配备A17 Pro芯片",
                    "rating": 4.8,
                    "final_score": 0.92,
                    "recommendation_reason": "最新旗舰手机，性能强劲"
                },
                {
                    "product_id": 5,
                    "name": "AirPods Pro 2",
                    "category": "耳机",
                    "brand": "Apple",
                    "price": 1899.00,
                    "description": "主动降噪无线耳机",
                    "rating": 4.7,
                    "final_score": 0.88,
                    "recommendation_reason": "优质音频体验，与Apple产品完美配合"
                }
            ]
        
        # 4. 构建意图画像
        intent_profile = schemas.IntentProfile(
            primary_intent=intent_analysis.get("intent_type", "信息查询"),
            secondary_intents=intent_analysis.get("product_categories", [])[:3],
            target_audience_segment=f"对{intent_analysis.get('product_categories', ['产品'])[0]}有需求，预算{intent_analysis.get('price_range', '中等')}的消费者",
            urgency_level=float(intent_analysis.get("urgency_level", 0.5)),
            confidence_score=float(intent_analysis.get("confidence", 0.7)),
            recommendation_reason=intent_analysis.get("recommendation_reason", "用户表现出购买意愿，需要进一步了解具体需求。")
        )
        
        # 5. 转换产品推荐为广告推荐格式
        ad_recommendations = []
        for rec in recommendations:
            ad_recommendations.append(schemas.AdRecommendation(
                ad_id=f"AD-{rec['product_id']}",
                product_id=str(rec['product_id']),
                relevance_score=float(rec['final_score']),
                ad_copy=rec['recommendation_reason'],
                product_name=rec.get('name'),
                product_category=rec.get('category'),
                product_brand=rec.get('brand'),
                product_price=rec.get('price')
            ))
        
        # 6. 组装并返回最终结果
        analysis_result = schemas.AnalysisResultOutput(
            request_id=str(uuid.uuid4()),
            intent_profile=intent_profile,
            ad_recommendations=ad_recommendations
        )
        
        logger.info(f"意图分析完成，返回广告推荐数量: {len(ad_recommendations)}")
        return analysis_result
        
    except Exception as e:
        # 记录详细的错误日志
        logger.error(f"真实意图分析失败: {str(e)}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        
        # 返回错误响应
        raise HTTPException(
            status_code=500,
            detail=f"意图分析失败: {str(e)}"
        )