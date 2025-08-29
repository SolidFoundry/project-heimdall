"""
企业级推荐API端点
基于用户行为数据进行智能推荐
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from heimdall.core.database import get_db
from heimdall.services.recommendation_engine import recommendation_engine
from heimdall.services.memory_data_provider import memory_data_provider

router = APIRouter(prefix="/api/v1", tags=["企业级推荐"])

@router.get("/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "enterprise-recommendations"
    }

# Pydantic模型
class RecommendationRequest(BaseModel):
    user_id: str
    session_id: str
    limit: Optional[int] = 10
    strategy: Optional[str] = "hybrid"  # collaborative, content, hybrid
    context: Optional[Dict[str, Any]] = None

class RecommendationResponse(BaseModel):
    user_id: str
    session_id: str
    recommendations: List[Dict[str, Any]]
    recommendation_metadata: Dict[str, Any]
    timestamp: str

class UserProfileRequest(BaseModel):
    user_id: str
    rebuild: Optional[bool] = False

class UserProfileResponse(BaseModel):
    user_id: str
    profile_data: Dict[str, Any]
    behavior_summary: Dict[str, Any]
    timestamp: str

class UserBehaviorRequest(BaseModel):
    user_id: str
    session_id: str
    behavior_type: str  # search, view, click, purchase
    behavior_data: Dict[str, Any]

class SimilarUsersRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 10

class SimilarUsersResponse(BaseModel):
    user_id: str
    similar_users: List[str]
    similarity_scores: Dict[str, float]
    timestamp: str

@router.post("/recommendations", response_model=RecommendationResponse, summary="基于用户行为推荐产品")
async def get_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """基于用户行为数据推荐产品
    
    根据用户的历史行为、偏好和相似用户行为，智能推荐相关产品。
    支持协同过滤、内容过滤和混合推荐策略。
    """
    try:
        # 获取推荐结果
        recommendations = await recommendation_engine.recommend_products(
            user_id=request.user_id,
            db=db,
            limit=request.limit,
            strategy=request.strategy
        )
        
        # 获取用户画像
        user_profile = await recommendation_engine.get_user_profile(request.user_id, db)
        
        # 记录推荐结果
        await recommendation_engine.record_recommendation(
            user_id=request.user_id,
            session_id=request.session_id,
            recommendations=recommendations,
            db=db
        )
        
        # 构建响应
        response_data = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "recommendations": recommendations,
            "recommendation_metadata": {
                "strategy": request.strategy,
                "recommendation_count": len(recommendations),
                "user_activity_level": user_profile.get("activity_level", 0),
                "user_preferences": {
                    "categories": list(user_profile.get("category_preferences", {}).keys()),
                    "brands": list(user_profile.get("brand_preferences", {}).keys())
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐失败: {str(e)}")

@router.post("/user-profile", response_model=UserProfileResponse, summary="获取用户画像")
async def get_user_profile(
    request: UserProfileRequest,
    db: AsyncSession = Depends(get_db)
):
    """获取用户画像信息
    
    返回用户的偏好、兴趣、行为特征等画像数据。
    如果rebuild为True，则重新构建用户画像。
    """
    try:
        if request.rebuild:
            user_profile = await recommendation_engine.build_user_profile(request.user_id, db)
        else:
            user_profile = await recommendation_engine.get_user_profile(request.user_id, db)
        
        # 获取用户行为摘要
        behavior_summary = await get_user_behavior_summary(request.user_id, db)
        
        return {
            "user_id": request.user_id,
            "profile_data": user_profile,
            "behavior_summary": behavior_summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户画像失败: {str(e)}")

@router.post("/record-behavior", summary="记录用户行为")
async def record_user_behavior(
    request: UserBehaviorRequest,
    db: AsyncSession = Depends(get_db)
):
    """记录用户行为数据
    
    记录用户的搜索、查看、点击、购买等行为，用于后续的推荐分析。
    """
    try:
        # 验证行为类型
        valid_behavior_types = ['search', 'view', 'click', 'purchase']
        if request.behavior_type not in valid_behavior_types:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的行为类型: {request.behavior_type}. 有效类型: {valid_behavior_types}"
            )
        
        # 记录行为
        query = """
            INSERT INTO user_behaviors (user_id, session_id, behavior_type, behavior_data, created_at)
            VALUES (:user_id, :session_id, :behavior_type, :behavior_data, :created_at)
        """
        
        await db.execute(query, {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "behavior_type": request.behavior_type,
            "behavior_data": request.behavior_data,
            "created_at": datetime.now()
        })
        
        await db.commit()
        
        # 异步更新用户画像（不阻塞响应）
        try:
            await recommendation_engine.build_user_profile(request.user_id, db)
        except Exception as e:
            # 不影响主流程，只记录日志
            print(f"更新用户画像失败: {e}")
        
        return {
            "message": "行为记录成功",
            "user_id": request.user_id,
            "behavior_type": request.behavior_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"记录行为失败: {str(e)}")

@router.post("/similar-users", response_model=SimilarUsersResponse, summary="获取相似用户")
async def get_similar_users(
    request: SimilarUsersRequest,
    db: AsyncSession = Depends(get_db)
):
    """获取相似用户
    
    基于用户画像和行为特征，找到与指定用户最相似的其他用户。
    """
    try:
        similar_users = await recommendation_engine.get_similar_users(
            request.user_id, 
            db, 
            request.limit
        )
        
        # 计算相似度分数
        current_profile = await recommendation_engine.get_user_profile(request.user_id, db)
        similarity_scores = {}
        
        for similar_user in similar_users:
            similar_profile = await recommendation_engine.get_user_profile(similar_user, db)
            similarity_score = recommendation_engine.calculate_similarity(current_profile, similar_profile)
            similarity_scores[similar_user] = similarity_score
        
        return {
            "user_id": request.user_id,
            "similar_users": similar_users,
            "similarity_scores": similarity_scores,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取相似用户失败: {str(e)}")

@router.get("/recommendations/trending", summary="获取热门推荐")
async def get_trending_recommendations(
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    category_id: Optional[int] = Query(None, description="类别ID过滤"),
    db: AsyncSession = Depends(get_db)
):
    """获取热门推荐
    
    基于销量、评分、浏览量等指标，获取当前热门的产品推荐。
    """
    try:
        # 构建查询条件
        conditions = ["is_active = true"]
        params = {"limit": limit}
        
        if category_id:
            conditions.append("category_id = :category_id")
            params["category_id"] = category_id
        
        where_clause = " AND ".join(conditions)
        
        query = text(f"""
            SELECT id, name, description, price, category_id, brand, image_url, tags, attributes, rating, review_count
            FROM products 
            WHERE {where_clause}
            ORDER BY rating DESC, review_count DESC, created_at DESC
            LIMIT :limit
        """)
        
        result = await db.execute(query, params)
        
        trending_products = []
        for row in result.fetchall():
            trending_products.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": row[3],
                "category_id": row[4],
                "brand": row[5],
                "image_url": row[6],
                "tags": row[7],
                "attributes": row[8],
                "rating": row[9],
                "review_count": row[10],
                "recommendation_reason": "热门推荐"
            })
        
        return {
            "trending_products": trending_products,
            "count": len(trending_products),
            "category_filter": category_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门推荐失败: {str(e)}")

@router.get("/analytics/user-activity", summary="用户行为分析")
async def get_user_activity_analytics(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="分析天数"),
    db: AsyncSession = Depends(get_db)
):
    """用户行为分析
    
    分析指定用户在最近N天内的行为模式和偏好。
    """
    try:
        # 获取用户行为数据
        query = text("""
            SELECT behavior_type, behavior_data, created_at
            FROM user_behaviors 
            WHERE user_id = :user_id 
            AND created_at >= :cutoff_date
            ORDER BY created_at DESC
        """)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await db.execute(query, {
            "user_id": user_id,
            "cutoff_date": cutoff_date
        })
        
        behaviors = result.fetchall()
        
        # 分析行为统计
        behavior_counts = {}
        category_counts = {}
        brand_counts = {}
        daily_activity = {}
        
        for behavior in behaviors:
            behavior_type = behavior[0]
            behavior_data = behavior[1]
            created_at = behavior[2]
            
            # 行为类型统计
            behavior_counts[behavior_type] = behavior_counts.get(behavior_type, 0) + 1
            
            # 类别统计
            if 'category' in behavior_data:
                category = behavior_data['category']
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # 品牌统计
            if 'brand' in behavior_data:
                brand = behavior_data['brand']
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
            
            # 日活统计
            date_key = created_at.strftime('%Y-%m-%d')
            daily_activity[date_key] = daily_activity.get(date_key, 0) + 1
        
        return {
            "user_id": user_id,
            "analysis_period": f"{days}天",
            "total_behaviors": len(behaviors),
            "behavior_counts": behavior_counts,
            "category_preferences": category_counts,
            "brand_preferences": brand_counts,
            "daily_activity": daily_activity,
            "most_active_day": max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户行为分析失败: {str(e)}")

async def get_user_behavior_summary(user_id: str, db: AsyncSession) -> Dict[str, Any]:
    """获取用户行为摘要"""
    try:
        # 获取最近30天的行为统计
        query = text("""
            SELECT 
                behavior_type,
                COUNT(*) as count,
                MAX(created_at) as last_activity
            FROM user_behaviors 
            WHERE user_id = :user_id 
            AND created_at >= :cutoff_date
            GROUP BY behavior_type
        """)
        
        cutoff_date = datetime.now() - timedelta(days=30)
        result = await db.execute(query, {
            "user_id": user_id,
            "cutoff_date": cutoff_date
        })
        
        behavior_stats = {}
        total_behaviors = 0
        last_activity = None
        
        for row in result.fetchall():
            behavior_type = row[0]
            count = row[1]
            last_behavior = row[2]
            
            behavior_stats[behavior_type] = count
            total_behaviors += count
            
            if last_behavior and (not last_activity or last_behavior > last_activity):
                last_activity = last_behavior
        
        return {
            "total_behaviors_30d": total_behaviors,
            "behavior_stats": behavior_stats,
            "last_activity": last_activity.isoformat() if last_activity else None,
            "activity_level": "high" if total_behaviors > 20 else "medium" if total_behaviors > 5 else "low"
        }
        
    except Exception as e:
        print(f"获取用户行为摘要失败: {e}")

# === 内存数据API端点 - 用于前端演示 ===

@router.get("/memory/products", summary="获取产品列表（内存数据）")
async def get_memory_products(
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    category: str = Query(None, description="产品类别筛选")
):
    """获取产品列表（使用内存数据）"""
    try:
        products = memory_data_provider.get_products(limit=limit, category=category)
        
        return {
            "products": products,
            "total": len(products),
            "categories": list(set(p["category"] for p in memory_data_provider.products)),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取产品列表失败: {str(e)}")

@router.get("/memory/recent-activities", summary="获取最近用户活动（内存数据）")
async def get_memory_recent_activities(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制")
):
    """获取最近用户活动（使用内存数据）"""
    try:
        activities = memory_data_provider.get_recent_activities(limit=limit)
        
        # 格式化活动数据
        formatted_activities = []
        for activity in activities:
            formatted_activities.append({
                "user_id": activity["user_id"],
                "action": activity["behavior_type"],
                "product_name": activity["product_name"] or "搜索",
                "category": activity["category"] or "搜索",
                "timestamp": activity["timestamp"].isoformat(),
                "details": activity["behavior_data"]
            })
        
        return {
            "activities": formatted_activities,
            "total": len(formatted_activities),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最近活动失败: {str(e)}")

@router.get("/memory/popular-products", summary="获取热门产品（内存数据）")
async def get_memory_popular_products(
    limit: int = Query(10, ge=1, le=20, description="返回数量限制")
):
    """获取热门产品（使用内存数据）"""
    try:
        popular_products = memory_data_provider.get_popular_products(limit=limit)
        
        return {
            "popular_products": popular_products,
            "total": len(popular_products),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门产品失败: {str(e)}")

@router.get("/memory/user-profile/{user_id}", summary="获取用户画像（内存数据）")
async def get_memory_user_profile(user_id: str):
    """获取用户画像（使用内存数据）"""
    try:
        profile = memory_data_provider.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
        
        # 获取用户行为
        behaviors = memory_data_provider.get_user_behaviors(user_id, limit=20)
        
        return {
            "user_id": user_id,
            "profile": profile,
            "recent_behaviors": behaviors[:5],
            "behavior_count": len(behaviors),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户画像失败: {str(e)}")

@router.get("/memory/category-stats", summary="获取类别统计（内存数据）")
async def get_memory_category_stats():
    """获取类别统计信息（使用内存数据）"""
    try:
        stats = memory_data_provider.get_category_stats()
        
        return {
            "category_stats": stats,
            "total_categories": len(stats),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取类别统计失败: {str(e)}")

@router.get("/memory/dashboard-stats", summary="获取仪表板统计（内存数据）")
async def get_memory_dashboard_stats():
    """获取仪表板统计数据（使用内存数据）"""
    try:
        # 基本统计
        total_products = len(memory_data_provider.products)
        total_users = len(memory_data_provider.user_profiles)
        total_behaviors = len(memory_data_provider.user_behaviors)
        
        # 类别统计
        category_stats = memory_data_provider.get_category_stats()
        
        # 热门产品
        popular_products = memory_data_provider.get_popular_products(limit=5)
        
        # 最近活动
        recent_activities = memory_data_provider.get_recent_activities(limit=5)
        
        return {
            "overview": {
                "total_products": total_products,
                "total_users": total_users,
                "total_behaviors": total_behaviors,
                "categories": len(category_stats)
            },
            "category_stats": category_stats,
            "popular_products": popular_products[:3],
            "recent_activities": recent_activities[:3],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表板统计失败: {str(e)}")
        return {}