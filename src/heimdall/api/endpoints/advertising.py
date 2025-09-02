"""
广告意图分析路由模块
提供用户意图识别和广告推荐功能
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from src.heimdall.services.llm_service import llm_service
from src.heimdall.services.session_service import session_service
from src.heimdall.tools.registry import tool_registry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.heimdall.core.database import get_db
from src.heimdall.core.config import settings

logger = logging.getLogger("heimdall.advertising")
router = APIRouter(prefix="/api/v1/advertising", tags=["advertising"])

# 请求模型
class IntentAnalysisRequest(BaseModel):
    """意图分析请求模型"""
    user_input: str = Field(..., description="用户输入内容")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    system_prompt: Optional[str] = Field(None, description="自定义系统提示词")

class IntentAnalysisResponse(BaseModel):
    """意图分析响应模型"""
    request_id: str
    user_input: str
    detected_intent: str
    intent_confidence: float
    target_audience: str
    urgency_level: float
    recommended_ads: List[Dict[str, Any]]
    analysis_summary: str
    session_id: str
    timestamp: str

class UserBehaviorRequest(BaseModel):
    """用户行为记录请求模型"""
    user_id: str = Field(..., description="用户ID")
    session_id: str = Field(..., description="会话ID")
    behavior_type: str = Field(..., description="行为类型: view, search, click, purchase")
    behavior_data: Dict[str, Any] = Field(..., description="行为数据")

class AdRecommendationRequest(BaseModel):
    """广告推荐请求模型"""
    user_id: str = Field(..., description="用户ID")
    session_id: str = Field(..., description="会话ID")
    intent_analysis_id: Optional[int] = Field(None, description="意图分析ID")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    limit: int = Field(5, description="推荐数量限制")

@router.post("/analyze_intent", response_model=IntentAnalysisResponse)
async def analyze_user_intent(
    request: IntentAnalysisRequest,
    http_request: Request
):
    """
    分析用户意图并生成广告推荐
    
    该接口使用大模型分析用户输入，识别用户意图，
    并基于意图生成相应的广告推荐。
    """
    request_id = getattr(http_request.state, 'request_id', str(uuid.uuid4()))
    
    logger.info(
        f"开始分析用户意图: {request.user_input}",
        extra={"request_id": request_id, "user_id": request.user_id}
    )
    
    try:
        # 生成或使用提供的会话ID
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # 获取数据库会话
        async for db in get_db():
            # 构建用于意图分析的提示词
            system_prompt = request.system_prompt or """
            你是一个专业的广告意图分析助手。请分析用户输入，识别其真实意图，
            并判断目标受众群体和紧急程度。请按照以下格式返回：

            意图类型: [明确的意图分类]
            目标受众: [具体的受众描述]
            紧急程度: [0.0-1.0之间的数值]
            推荐理由: [简要的推荐理由]
            
            常见意图类型包括：
            - 产品购买
            - 信息查询
            - 服务咨询
            - 价格比较
            - 品牌了解
            - 售后服务
            """
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_input}
            ]
            
            # 调用大模型进行意图分析
            model_response = await llm_service.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=messages,
                temperature=0.3
            )
            
            analysis_result = model_response.choices[0].message.content
            
            # 解析分析结果
            intent_info = parse_intent_analysis(analysis_result)
            
            # 生成广告推荐
            recommended_ads = generate_ad_recommendations(intent_info)
            
            # 构建响应
            response = IntentAnalysisResponse(
                request_id=request_id,
                user_input=request.user_input,
                detected_intent=intent_info["intent"],
                intent_confidence=intent_info["confidence"],
                target_audience=intent_info["target_audience"],
                urgency_level=intent_info["urgency_level"],
                recommended_ads=recommended_ads,
                analysis_summary=intent_info["summary"],
                session_id=session_id,
                timestamp=datetime.now().isoformat()
            )
            
            # 保存对话历史 - 先确保会话存在
            await session_service.get_or_create_session(session_id, db)
            user_message = {"role": "user", "content": request.user_input}
            assistant_message = {"role": "assistant", "content": f"意图分析完成：{intent_info['intent']}"}
            await session_service.update_history(session_id, [user_message, assistant_message], db)
            
            logger.info(
                f"意图分析完成: {intent_info['intent']}",
                extra={"request_id": request_id, "confidence": intent_info["confidence"]}
            )
            
            return response
            
    except Exception as e:
        logger.error(
            f"意图分析失败: {str(e)}",
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"意图分析失败: {str(e)}")

@router.post("/record_behavior")
async def record_user_behavior(
    request: UserBehaviorRequest,
    http_request: Request
):
    """
    记录用户行为数据
    
    用于记录用户的浏览、搜索、点击、购买等行为，
    为后续的广告推荐提供数据支持。
    """
    request_id = getattr(http_request.state, 'request_id', str(uuid.uuid4()))
    
    logger.info(
        f"记录用户行为: {request.behavior_type}",
        extra={"request_id": request_id, "user_id": request.user_id}
    )
    
    try:
        # 这里可以添加数据库存储逻辑
        # 目前只是记录日志
        
        behavior_data = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "behavior_type": request.behavior_type,
            "behavior_data": request.behavior_data,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(
            f"用户行为记录成功",
            extra={"request_id": request_id, "behavior_data": behavior_data}
        )
        
        return {
            "request_id": request_id,
            "message": "用户行为记录成功",
            "behavior_data": behavior_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(
            f"用户行为记录失败: {str(e)}",
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"行为记录失败: {str(e)}")

@router.post("/recommend_ads")
async def recommend_ads(
    request: AdRecommendationRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    基于用户画像和意图分析生成广告推荐
    
    结合用户历史行为、当前意图和上下文信息，
    生成个性化的广告推荐。
    """
    request_id = getattr(http_request.state, 'request_id', str(uuid.uuid4()))
    
    logger.info(
        f"生成广告推荐: 用户 {request.user_id}",
        extra={"request_id": request_id}
    )
    
    try:
        # 导入真实推荐引擎
        from src.heimdall.services.recommendation_engine import EnterpriseRecommendationEngine
        
        # 创建推荐引擎实例
        engine = EnterpriseRecommendationEngine()
        
        # 获取用户画像
        user_profile = await engine.get_user_profile(request.user_id, db)
        
        # 如果没有用户画像，动态构建
        if not user_profile:
            user_profile = await engine.build_user_profile(request.user_id, db)
        
        # 基于用户画像生成推荐
        recommendations = await engine.recommend_products(
            user_id=request.user_id,
            db=db,
            limit=request.limit or 5,
            strategy="hybrid"  # 使用混合推荐策略
        )
        
        # 如果没有推荐结果，返回热门产品
        if not recommendations:
            recommendations = await engine.get_popular_products(db, limit=request.limit or 5)
        
        return {
            "request_id": request_id,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "user_profile": {
                "interests": user_profile.get("interest_tags", []),
                "activity_level": user_profile.get("activity_level", 0),
                "preferred_categories": list(user_profile.get("category_preferences", {}).keys()),
                "preferred_brands": list(user_profile.get("brand_preferences", {}).keys()),
                "price_range": user_profile.get("price_range", {})
            },
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(
            f"广告推荐生成失败: {str(e)}",
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"推荐生成失败: {str(e)}")

@router.get("/analytics/overview")
async def get_analytics_overview(
    http_request: Request,
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """
    获取广告分析概览数据
    
    提供最近指定天数内的广告效果分析数据，
    包括点击率、转化率等关键指标。
    """
    request_id = getattr(http_request.state, 'request_id', str(uuid.uuid4()))
    
    logger.info(
        f"获取分析概览: 最近 {days} 天",
        extra={"request_id": request_id}
    )
    
    try:
        # 查询用户行为统计
        behavior_query = text("""
            SELECT 
                behavior_type,
                COUNT(*) as count
            FROM user_behaviors 
            WHERE created_at >= NOW() - INTERVAL '1 day' * :days
            GROUP BY behavior_type
        """)
        
        result = await db.execute(behavior_query, {"days": days})
        behavior_stats = {row[0]: row[1] for row in result.fetchall()}
        
        # 查询推荐总数
        recommendations_query = text("""
            SELECT COUNT(*) 
            FROM recommendations 
            WHERE created_at >= NOW() - INTERVAL '1 day' * :days
        """)
        
        result = await db.execute(recommendations_query, {"days": days})
        row = result.fetchone()
        total_recommendations = row[0] if row else 0
        
        # 获取意图分析统计
        intent_query = text("""
            SELECT 
                detected_intent,
                COUNT(*) as count
            FROM user_behaviors 
            WHERE created_at >= NOW() - INTERVAL '1 day' * :days
            AND detected_intent IS NOT NULL
            GROUP BY detected_intent
            ORDER BY count DESC
            LIMIT 5
        """)
        
        result = await db.execute(intent_query, {"days": days})
        intent_stats = {row[0]: row[1] for row in result.fetchall()}
        
        # 构建分析数据
        total_behaviors = sum(behavior_stats.values())
        total_clicks = behavior_stats.get('click', 0)
        total_purchases = behavior_stats.get('purchase', 0)
        total_views = behavior_stats.get('view', 0)
        
        # 计算指标
        click_through_rate = (total_clicks / total_recommendations * 100) if total_recommendations > 0 else 0
        conversion_rate = (total_purchases / total_clicks * 100) if total_clicks > 0 else 0
        
        # 获取热门产品统计
        top_products_query = text("""
            SELECT 
                p.id,
                p.name,
                p.category,
                COUNT(ub.id) as click_count
            FROM user_behaviors ub
            JOIN products p ON ub.product_id = p.id
            WHERE ub.behavior_type = 'click'
            AND ub.created_at >= NOW() - INTERVAL '1 day' * :days
            GROUP BY p.id, p.name, p.category
            ORDER BY click_count DESC
            LIMIT 5
        """)
        
        result = await db.execute(top_products_query, {"days": days})
        top_products = [
            {"product_id": row[0], "name": row[1], "category": row[2], "clicks": row[3]}
            for row in result.fetchall()
        ]
        
        overview_data = {
            "period_days": days,
            "total_impressions": total_views,  # 使用浏览量作为展示量
            "total_clicks": total_clicks,
            "click_through_rate": round(click_through_rate, 2),
            "conversions": total_purchases,
            "conversion_rate": round(conversion_rate, 2),
            "revenue": total_purchases * 163,  # 假设平均客单价163元
            "top_performing_products": top_products,
            "intent_distribution": intent_stats or {
                "产品购买": 0,
                "信息查询": 0,
                "价格比较": 0,
                "售后服务": 0
            },
            "behavior_breakdown": behavior_stats
        }
        
        return {
            "request_id": request_id,
            "overview": overview_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(
            f"获取分析概览失败: {str(e)}",
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"获取分析数据失败: {str(e)}")

def parse_intent_analysis(analysis_result: str) -> Dict[str, Any]:
    """
    解析大模型返回的意图分析结果
    """
    lines = analysis_result.split('\n')
    intent_info = {
        "intent": "未知意图",
        "confidence": 0.5,
        "target_audience": "普通用户",
        "urgency_level": 0.5,
        "summary": analysis_result
    }
    
    for line in lines:
        line = line.strip()
        if "意图类型:" in line:
            intent_info["intent"] = line.split("意图类型:")[-1].strip()
        elif "目标受众:" in line:
            intent_info["target_audience"] = line.split("目标受众:")[-1].strip()
        elif "紧急程度:" in line:
            try:
                urgency_str = line.split("紧急程度:")[-1].strip()
                intent_info["urgency_level"] = float(urgency_str)
            except ValueError:
                intent_info["urgency_level"] = 0.5
    
    # 根据意图类型调整置信度
    if intent_info["intent"] != "未知意图":
        intent_info["confidence"] = 0.8
    
    return intent_info

def generate_ad_recommendations(intent_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    基于意图分析生成广告推荐
    """
    recommendations = []
    
    # 根据意图类型生成不同的推荐
    if "产品购买" in intent_info["intent"]:
        recommendations = [
            {
                "ad_id": "prod_buy_001",
                "title": "热门商品推荐",
                "description": "基于您的购买意图推荐的商品",
                "relevance_score": 0.92,
                "call_to_action": "立即购买"
            }
        ]
    elif "信息查询" in intent_info["intent"]:
        recommendations = [
            {
                "ad_id": "info_query_001",
                "title": "产品信息",
                "description": "详细的产品规格和用户评价",
                "relevance_score": 0.85,
                "call_to_action": "了解更多"
            }
        ]
    else:
        recommendations = [
            {
                "ad_id": "general_001",
                "title": "热门推荐",
                "description": "为您推荐的热门商品",
                "relevance_score": 0.75,
                "call_to_action": "查看详情"
            }
        ]
    
    return recommendations