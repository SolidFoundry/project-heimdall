"""
企业级混合推荐API - 集成AI意图识别
结合AI意图分析和用户行为分析的推荐接口
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from src.heimdall.services.hybrid_recommendation_engine import hybrid_recommendation_engine
from src.heimdall.core.database import get_db
# from src.heimdall.core.structured_logging import get_request_id

logger = logging.getLogger("heimdall.hybrid_recommendations")
router = APIRouter(prefix="/api/v1/hybrid-recommendations", tags=["hybrid-recommendations"])

# 请求模型
class HybridRecommendationRequest(BaseModel):
    """混合推荐请求模型"""
    user_id: str = Field(..., description="用户ID")
    user_input: Optional[str] = Field(None, description="用户输入文本（用于AI意图分析）")
    session_id: Optional[str] = Field(None, description="会话ID")
    limit: int = Field(10, description="推荐数量限制")
    strategy: str = Field("hybrid", description="推荐策略: hybrid, intent_based, behavior_based")

class IntentAnalysisRequest(BaseModel):
    """AI意图分析请求模型"""
    user_input: str = Field(..., description="用户输入内容")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")

# 响应模型
class HybridRecommendationResponse(BaseModel):
    """混合推荐响应模型"""
    request_id: str
    user_id: str
    user_input: Optional[str]
    intent_analysis: Optional[Dict[str, Any]]
    behavior_profile: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    strategy: str
    total_recommendations: int
    session_id: str
    timestamp: str

class IntentAnalysisResponse(BaseModel):
    """AI意图分析响应模型"""
    request_id: str
    user_input: str
    intent_analysis: Dict[str, Any]
    user_id: Optional[str]
    session_id: str
    timestamp: str

@router.post("/recommendations", response_model=HybridRecommendationResponse)
async def get_hybrid_recommendations(
    request: HybridRecommendationRequest,
    http_request: Request,
    db=Depends(get_db)
):
    """
    生成混合推荐结果
    
    结合AI意图分析和用户行为分析，生成个性化推荐
    """
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info(
        f"生成混合推荐: 用户 {request.user_id}, 策略 {request.strategy}",
        extra={"request_id": request_id}
    )
    
    try:
        # 生成会话ID
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # 获取混合推荐
        recommendations = await hybrid_recommendation_engine.get_hybrid_recommendations(
            user_id=request.user_id,
            user_input=request.user_input,
            db=db,
            limit=request.limit,
            strategy=request.strategy
        )
        
        # 获取用户行为画像
        behavior_profile = await hybrid_recommendation_engine.get_user_behavior_profile(
            request.user_id, db
        )
        
        # AI意图分析（如果有用户输入）
        intent_analysis = None
        if request.user_input:
            intent_analysis = await hybrid_recommendation_engine.analyze_user_intent(
                request.user_input, request.user_id
            )
        
        response = HybridRecommendationResponse(
            request_id=request_id,
            user_id=request.user_id,
            user_input=request.user_input,
            intent_analysis=intent_analysis,
            behavior_profile=behavior_profile,
            recommendations=recommendations,
            strategy=request.strategy,
            total_recommendations=len(recommendations),
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(
            f"混合推荐生成完成: {len(recommendations)} 个推荐",
            extra={"request_id": request_id}
        )
        
        return response
        
    except Exception as e:
        logger.error(
            f"混合推荐生成失败: {str(e)}",
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"推荐生成失败: {str(e)}")

@router.post("/analyze-intent", response_model=IntentAnalysisResponse)
async def analyze_user_intent(
    request: IntentAnalysisRequest,
    http_request: Request
):
    """
    AI意图分析
    
    使用大模型分析用户输入，识别购买意图和偏好
    """
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info(
        f"AI意图分析: {request.user_input[:50]}...",
        extra={"request_id": request_id}
    )
    
    try:
        # 生成会话ID
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # 执行AI意图分析
        intent_analysis = await hybrid_recommendation_engine.analyze_user_intent(
            request.user_input, request.user_id
        )
        
        response = IntentAnalysisResponse(
            request_id=request_id,
            user_input=request.user_input,
            intent_analysis=intent_analysis,
            user_id=request.user_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(
            f"AI意图分析完成: {intent_analysis.get('intent_type', '未知')}",
            extra={"request_id": request_id}
        )
        
        return response
        
    except Exception as e:
        logger.error(
            f"AI意图分析失败: {str(e)}",
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"意图分析失败: {str(e)}")

@router.get("/user-profile/{user_id}")
async def get_user_profile(
    user_id: str,
    http_request: Request,
    db=Depends(get_db)
):
    """
    获取用户画像
    
    基于用户行为数据生成用户画像
    """
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info(
        f"获取用户画像: {user_id}",
        extra={"request_id": request_id}
    )
    
    try:
        # 获取用户行为画像
        behavior_profile = await hybrid_recommendation_engine.get_user_behavior_profile(
            user_id, db
        )
        
        return {
            "request_id": request_id,
            "user_id": user_id,
            "profile": behavior_profile,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(
            f"获取用户画像失败: {str(e)}",
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"获取用户画像失败: {str(e)}")

@router.get("/recommendations/comparison")
async def get_recommendation_comparison(
    user_id: str,
    user_input: str,
    http_request: Request,
    db=Depends(get_db),
    limit: int = 5
):
    """
    获取推荐策略对比
    
    对比不同推荐策略的结果
    """
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info(
        f"推荐策略对比: 用户 {user_id}",
        extra={"request_id": request_id}
    )
    
    try:
        strategies = ["hybrid", "intent_based", "behavior_based"]
        comparison_results = {}
        
        for strategy in strategies:
            recommendations = await hybrid_recommendation_engine.get_hybrid_recommendations(
                user_id=user_id,
                user_input=user_input,
                db=db,
                limit=limit,
                strategy=strategy
            )
            
            comparison_results[strategy] = {
                "recommendations": recommendations,
                "count": len(recommendations),
                "avg_score": sum(r.get("final_score", 0) for r in recommendations) / len(recommendations) if recommendations else 0
            }
        
        return {
            "request_id": request_id,
            "user_id": user_id,
            "user_input": user_input,
            "comparison": comparison_results,
            "best_strategy": max(comparison_results.items(), key=lambda x: x[1]["avg_score"])[0],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(
            f"推荐策略对比失败: {str(e)}",
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"策略对比失败: {str(e)}")