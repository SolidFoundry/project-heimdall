"""
企业级推荐引擎
基于用户行为数据进行智能推荐
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func
from collections import defaultdict, Counter
import math

from src.heimdall.core.database import get_db

logger = logging.getLogger("heimdall.recommendation_engine")

class EnterpriseRecommendationEngine:
    """企业级推荐引擎"""
    
    def __init__(self):
        self.behavior_weights = {
            'purchase': 3.0,    # 购买权重最高
            'click': 1.5,       # 点击次之
            'view': 1.0,        # 查看基础权重
            'search': 0.8       # 搜索权重较低
        }
        
        self.decay_factors = {
            'purchase': 0.9,    # 购买行为衰减较慢
            'click': 0.8,       # 点击行为衰减中等
            'view': 0.7,        # 查看行为衰减较快
            'search': 0.6       # 搜索行为衰减最快
        }
    
    async def get_user_profile(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """获取用户画像"""
        try:
            # 从用户画像表获取数据
            query = text("""
                SELECT profile_data FROM user_profiles 
                WHERE user_id = :user_id
            """)
            result = await db.execute(query, {"user_id": user_id})
            profile_data = result.fetchone()
            
            if profile_data:
                return profile_data[0]
            
            # 如果没有画像数据，从行为数据构建
            return await self.build_user_profile(user_id, db)
            
        except Exception as e:
            logger.error(f"获取用户画像失败: {e}")
            return {}
    
    async def build_user_profile(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """基于行为数据构建用户画像"""
        try:
            # 获取用户最近30天的行为数据
            query = text("""
                SELECT behavior_type, behavior_data, created_at 
                FROM user_behaviors 
                WHERE user_id = :user_id 
                AND created_at >= :cutoff_date
                ORDER BY created_at DESC
            """)
            
            cutoff_date = datetime.now() - timedelta(days=30)
            result = await db.execute(query, {
                "user_id": user_id,
                "cutoff_date": cutoff_date
            })
            
            behaviors = result.fetchall()
            
            if not behaviors:
                return {"user_id": user_id, "preferences": {}, "activity_level": 0}
            
            # 分析用户偏好
            category_scores = defaultdict(float)
            brand_scores = defaultdict(float)
            price_range = {"min": float('inf'), "max": 0}
            total_behavior_score = 0
            
            for behavior in behaviors:
                behavior_type = behavior[0]
                behavior_data = behavior[1]
                created_at = behavior[2]
                
                # 计算时间衰减权重
                days_ago = (datetime.now() - created_at).days
                time_decay = math.exp(-days_ago * 0.1)  # 指数衰减
                
                # 基础权重
                weight = self.behavior_weights.get(behavior_type, 1.0) * time_decay
                
                # 分析类别偏好
                if 'category' in behavior_data:
                    category = behavior_data['category']
                    category_scores[category] += weight
                
                # 分析品牌偏好
                if 'brand' in behavior_data:
                    brand = behavior_data['brand']
                    brand_scores[brand] += weight
                
                # 分析价格偏好
                if 'price' in behavior_data:
                    price = behavior_data['price']
                    price_range['min'] = min(price_range['min'], price)
                    price_range['max'] = max(price_range['max'], price)
                
                total_behavior_score += weight
            
            # 构建画像
            profile = {
                "user_id": user_id,
                "category_preferences": dict(category_scores),
                "brand_preferences": dict(brand_scores),
                "price_range": price_range,
                "activity_level": total_behavior_score,
                "last_activity": behaviors[0][2] if behaviors else datetime.now(),
                "behavior_count": len(behaviors)
            }
            
            # 保存用户画像
            await self.save_user_profile(user_id, profile, db)
            
            return profile
            
        except Exception as e:
            logger.error(f"构建用户画像失败: {e}")
            return {}
    
    async def save_user_profile(self, user_id: str, profile: Dict[str, Any], db: AsyncSession):
        """保存用户画像"""
        try:
            query = text("""
                INSERT INTO user_profiles (user_id, profile_data, created_at, updated_at)
                VALUES (:user_id, :profile_data, :created_at, :updated_at)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    profile_data = :profile_data,
                    updated_at = :updated_at
            """)
            
            await db.execute(query, {
                "user_id": user_id,
                "profile_data": json.dumps(profile, ensure_ascii=False, default=str),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"保存用户画像失败: {e}")
            await db.rollback()
    
    async def get_similar_users(self, user_id: str, db: AsyncSession, limit: int = 10) -> List[str]:
        """获取相似用户"""
        try:
            # 获取当前用户的画像
            current_profile = await self.get_user_profile(user_id, db)
            if not current_profile:
                return []
            
            # 获取所有用户画像
            query = text("""
                SELECT user_id, profile_data FROM user_profiles 
                WHERE user_id != :user_id
            """)
            result = await db.execute(query, {"user_id": user_id})
            all_profiles = result.fetchall()
            
            # 计算相似度
            similarities = []
            for profile_row in all_profiles:
                other_user_id = profile_row[0]
                other_profile = profile_row[1]
                
                similarity = self.calculate_similarity(current_profile, other_profile)
                similarities.append((other_user_id, similarity))
            
            # 排序并返回最相似的用户
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [user_id for user_id, _ in similarities[:limit]]
            
        except Exception as e:
            logger.error(f"获取相似用户失败: {e}")
            return []
    
    def calculate_similarity(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> float:
        """计算用户相似度"""
        try:
            # 类别偏好相似度
            categories1 = set(profile1.get('category_preferences', {}).keys())
            categories2 = set(profile2.get('category_preferences', {}).keys())
            
            if not categories1 and not categories2:
                category_similarity = 0.0
            else:
                intersection = categories1.intersection(categories2)
                union = categories1.union(categories2)
                category_similarity = len(intersection) / len(union) if union else 0.0
            
            # 品牌偏好相似度
            brands1 = set(profile1.get('brand_preferences', {}).keys())
            brands2 = set(profile2.get('brand_preferences', {}).keys())
            
            if not brands1 and not brands2:
                brand_similarity = 0.0
            else:
                intersection = brands1.intersection(brands2)
                union = brands1.union(brands2)
                brand_similarity = len(intersection) / len(union) if union else 0.0
            
            # 综合相似度
            return (category_similarity + brand_similarity) / 2.0
            
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.0
    
    async def get_user_behavior_products(self, user_id: str, db: AsyncSession) -> List[int]:
        """获取用户行为相关的产品ID"""
        try:
            # 获取用户查看、点击、购买过的产品
            query = text("""
                SELECT DISTINCT product_id
                FROM user_behaviors 
                WHERE user_id = :user_id 
                AND product_id IS NOT NULL
                AND product_id != 0
                AND behavior_type IN ('view', 'click', 'purchase')
            """)
            
            result = await db.execute(query, {"user_id": user_id})
            product_ids = [row[0] for row in result.fetchall() if row[0]]
            
            return [int(pid) if isinstance(pid, str) and pid.isdigit() else pid for pid in product_ids if pid]
            
        except Exception as e:
            logger.error(f"获取用户行为产品失败: {e}")
            return []
    
    async def recommend_products(
        self, 
        user_id: str, 
        db: AsyncSession, 
        limit: int = 10,
        strategy: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """推荐产品"""
        try:
            # 获取用户画像
            user_profile = await self.get_user_profile(user_id, db)
            
            # 获取用户已经交互过的产品
            interacted_products = await self.get_user_behavior_products(user_id, db)
            
            # 根据策略推荐
            if strategy == "collaborative":
                return await self.collaborative_filtering(user_id, db, limit, interacted_products)
            elif strategy == "content":
                return await self.content_based_filtering(user_profile, db, limit, interacted_products)
            else:  # hybrid
                return await self.hybrid_recommendations(user_id, user_profile, db, limit, interacted_products)
                
        except Exception as e:
            logger.error(f"推荐产品失败: {e}")
            return []
    
    async def collaborative_filtering(
        self, 
        user_id: str, 
        db: AsyncSession, 
        limit: int,
        interacted_products: List[int]
    ) -> List[Dict[str, Any]]:
        """协同过滤推荐"""
        try:
            # 获取相似用户
            similar_users = await self.get_similar_users(user_id, db, limit=20)
            
            if not similar_users:
                return []
            
            # 获取相似用户喜欢的产品
            similar_user_products = set()
            for similar_user in similar_users:
                products = await self.get_user_behavior_products(similar_user, db)
                similar_user_products.update(products)
            
            # 排除用户已经交互过的产品
            candidate_products = similar_user_products - set(interacted_products)
            
            if not candidate_products:
                return []
            
            # 获取产品详情
            query = text("""
                SELECT id, name, description, price, category, brand, image_url, tags, attributes, rating, review_count
                FROM products 
                WHERE id = ANY(:product_ids)
                AND is_active = true
                ORDER BY rating DESC, review_count DESC
                LIMIT :limit
            """)
            
            result = await db.execute(query, {
                "product_ids": list(candidate_products),
                "limit": limit
            })
            
            products = []
            for row in result.fetchall():
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "price": row[3],
                    "category": row[4],
                    "brand": row[5],
                    "image_url": row[6],
                    "tags": row[7],
                    "attributes": row[8],
                    "rating": row[9],
                    "review_count": row[10],
                    "recommendation_reason": "基于相似用户行为推荐",
                    "relevance_score": 0.85  # 默认相关度
                })
            
            return products
            
        except Exception as e:
            logger.error(f"协同过滤推荐失败: {e}")
            return []
    
    async def content_based_filtering(
        self, 
        user_profile: Dict[str, Any], 
        db: AsyncSession, 
        limit: int,
        interacted_products: List[int]
    ) -> List[Dict[str, Any]]:
        """基于内容的推荐"""
        try:
            # 获取用户偏好的类别和品牌
            category_preferences = user_profile.get('category_preferences', {})
            brand_preferences = user_profile.get('brand_preferences', {})
            
            if not category_preferences and not brand_preferences:
                return []
            
            # 构建查询条件
            conditions = []
            params = {"limit": limit}
            
            if category_preferences:
                # 按类别偏好排序
                top_categories = sorted(category_preferences.items(), key=lambda x: x[1], reverse=True)[:3]
                category_ids = [cat_id for cat_id, _ in top_categories]
                conditions.append("category = ANY(:category_ids)")
                params["category_ids"] = category_ids
            
            if brand_preferences:
                # 按品牌偏好排序
                top_brands = sorted(brand_preferences.items(), key=lambda x: x[1], reverse=True)[:3]
                brands = [brand for brand, _ in top_brands]
                conditions.append("brand = ANY(:brands)")
                params["brands"] = brands
            
            # 排除已经交互过的产品
            if interacted_products:
                conditions.append("id != ALL(:interacted_products)")
                params["interacted_products"] = interacted_products
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = text(f"""
                SELECT id, name, description, price, category, brand, image_url, tags, attributes, rating, review_count
                FROM products 
                WHERE {where_clause}
                AND is_active = true
                ORDER BY rating DESC, review_count DESC
                LIMIT :limit
            """)
            
            result = await db.execute(query, params)
            
            products = []
            for row in result.fetchall():
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "price": row[3],
                    "category": row[4],
                    "brand": row[5],
                    "image_url": row[6],
                    "tags": row[7],
                    "attributes": row[8],
                    "rating": row[9],
                    "review_count": row[10],
                    "recommendation_reason": "基于您的偏好推荐",
                    "relevance_score": 0.9  # 基于偏好的相关度更高
                })
            
            return products
            
        except Exception as e:
            logger.error(f"基于内容的推荐失败: {e}")
            return []
    
    async def hybrid_recommendations(
        self, 
        user_id: str, 
        user_profile: Dict[str, Any], 
        db: AsyncSession, 
        limit: int,
        interacted_products: List[int]
    ) -> List[Dict[str, Any]]:
        """混合推荐"""
        try:
            # 获取协同过滤推荐
            cf_recommendations = await self.collaborative_filtering(user_id, db, limit // 2, interacted_products)
            
            # 获取基于内容的推荐
            content_recommendations = await self.content_based_filtering(user_profile, db, limit // 2, interacted_products)
            
            # 合并推荐结果
            all_recommendations = cf_recommendations + content_recommendations
            
            # 去重
            seen_ids = set()
            unique_recommendations = []
            for rec in all_recommendations:
                if rec['id'] not in seen_ids:
                    seen_ids.add(rec['id'])
                    unique_recommendations.append(rec)
            
            # 按评分和推荐理由排序
            unique_recommendations.sort(key=lambda x: (x['rating'], x['review_count']), reverse=True)
            
            return unique_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"混合推荐失败: {e}")
            return []
    
    async def record_recommendation(
        self, 
        user_id: str, 
        session_id: str, 
        recommendations: List[Dict[str, Any]], 
        db: AsyncSession
    ):
        """记录推荐结果"""
        try:
            query = text("""
                INSERT INTO recommendations (user_id, session_id, recommendation_type, recommended_items, recommendation_score, context_data, created_at)
                VALUES (:user_id, :session_id, :recommendation_type, :recommended_items, :recommendation_score, :context_data, :created_at)
            """)
            
            await db.execute(query, {
                "user_id": user_id,
                "session_id": session_id,
                "recommendation_type": "product",
                "recommended_items": recommendations,
                "recommendation_score": sum(rec.get('rating', 0) for rec in recommendations) / len(recommendations) if recommendations else 0.0,
                "context_data": {"strategy": "hybrid", "timestamp": datetime.now().isoformat()},
                "created_at": datetime.now()
            })
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"记录推荐失败: {e}")
            await db.rollback()
    
    async def get_popular_products(self, db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门产品推荐"""
        try:
            query = text("""
                SELECT id, name, description, price, category, brand, image_url, tags, attributes, rating, review_count
                FROM products 
                WHERE is_active = true
                ORDER BY rating DESC, review_count DESC
                LIMIT :limit
            """)
            
            result = await db.execute(query, {"limit": limit})
            
            products = []
            for row in result.fetchall():
                products.append({
                    "product_id": str(row[0]),
                    "title": row[1],
                    "description": row[2],
                    "price": float(row[3]) if row[3] else 0,
                    "category": self._get_category_name(row[4]),
                    "brand": row[5],
                    "image_url": row[6],
                    "rating": float(row[9]) if row[9] else 0,
                    "review_count": row[10] if row[10] else 0,
                    "relevance_score": 0.8,  # 默认相关度
                    "tags": row[7] or [],
                    "attributes": row[8] or {}
                })
            
            return products
            
        except Exception as e:
            logger.error(f"获取热门产品失败: {e}")
            return []
    
    def _get_category_name(self, category: str) -> str:
        """根据类别ID获取类别名称"""
        # 直接返回类别名称
        return category or "其他"

# 全局推荐引擎实例
recommendation_engine = EnterpriseRecommendationEngine()