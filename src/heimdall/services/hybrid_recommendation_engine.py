"""
增强版企业推荐引擎 - 集成AI意图分析
结合AI意图识别和用户行为分析的混合推荐系统
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import numpy as np

from heimdall.services.llm_service import llm_service
from heimdall.core.config import settings

logger = logging.getLogger("heimdall.hybrid_recommendation")

class HybridRecommendationEngine:
    """混合推荐引擎 - 结合AI意图分析和用户行为分析"""
    
    def __init__(self):
        # 行为权重配置
        self.behavior_weights = {
            'purchase': 3.0,    # 购买权重最高
            'click': 1.5,       # 点击次之
            'view': 1.0,        # 查看基础权重
            'search': 0.8       # 搜索权重较低
        }
        
        # AI意图权重
        self.intent_weights = {
            '产品购买': 0.9,    # 购买意图权重最高
            '价格比较': 0.8,    # 价格比较意图
            '信息查询': 0.6,    # 信息查询意图
            '品牌了解': 0.5,    # 品牌了解意图
            '售后服务': 0.3     # 售后服务意图
        }
        
        # 推荐策略权重
        self.strategy_weights = {
            'intent_based': 0.4,     # AI意图分析权重
            'collaborative': 0.3,    # 协同过滤权重
            'content_based': 0.2,     # 内容过滤权重
            'popularity': 0.1         # 热门推荐权重
        }
    
    async def analyze_user_intent(self, user_input: str, user_id: str = None) -> Dict[str, Any]:
        """
        使用AI分析用户意图
        """
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
                "analysis_summary": "分析总结"
            }
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # 调用大模型进行意图分析
            model_response = await llm_service.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=messages,
                temperature=0.3
            )
            
            intent_result = model_response.choices[0].message.content
            
            # 解析JSON结果
            try:
                intent_data = json.loads(intent_result)
                logger.info(f"AI意图分析完成: {intent_data.get('intent_type', '未知')}")
                return intent_data
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用简单的文本解析
                return self._parse_intent_text(intent_result)
                
        except Exception as e:
            logger.error(f"AI意图分析失败: {e}")
            # 返回默认意图
            return {
                "intent_type": "信息查询",
                "confidence": 0.5,
                "product_categories": [],
                "price_range": "中",
                "brand_preferences": [],
                "urgency_level": 0.5,
                "keywords": [],
                "analysis_summary": "意图分析失败，使用默认配置"
            }
    
    def _parse_intent_text(self, intent_text: str) -> Dict[str, Any]:
        """文本解析备用方案"""
        lines = intent_text.split('\n')
        intent_data = {
            "intent_type": "信息查询",
            "confidence": 0.5,
            "product_categories": [],
            "price_range": "中",
            "brand_preferences": [],
            "urgency_level": 0.5,
            "keywords": [],
            "analysis_summary": intent_text
        }
        
        for line in lines:
            line = line.strip().lower()
            if "购买" in line:
                intent_data["intent_type"] = "产品购买"
                intent_data["confidence"] = 0.8
            elif "价格" in line:
                intent_data["intent_type"] = "价格比较"
                intent_data["confidence"] = 0.7
            elif "品牌" in line:
                intent_data["intent_type"] = "品牌了解"
                intent_data["confidence"] = 0.6
        
        return intent_data
    
    async def get_user_behavior_profile(self, user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """获取用户行为画像"""
        try:
            # 查询用户最近行为
            query = text("""
                SELECT behavior_type, product_id, category, brand, 
                       COUNT(*) as frequency, MAX(timestamp) as last_action
                FROM user_behaviors 
                WHERE user_id = :user_id 
                AND timestamp > :cutoff_date
                GROUP BY behavior_type, product_id, category, brand
                ORDER BY frequency DESC
                LIMIT 50
            """)
            
            cutoff_date = datetime.now() - timedelta(days=30)
            result = await db.execute(query, {
                "user_id": user_id,
                "cutoff_date": cutoff_date
            })
            
            behaviors = result.fetchall()
            
            # 分析用户偏好
            category_scores = {}
            brand_scores = {}
            behavior_scores = {}
            
            for behavior in behaviors:
                behavior_type = behavior[0]
                product_id = behavior[1]
                category = behavior[2]
                brand = behavior[3]
                frequency = behavior[4]
                
                weight = self.behavior_weights.get(behavior_type, 1.0)
                score = frequency * weight
                
                # 类别偏好
                if category:
                    category_scores[category] = category_scores.get(category, 0) + score
                
                # 品牌偏好
                if brand:
                    brand_scores[brand] = brand_scores.get(brand, 0) + score
                
                # 行为模式
                behavior_scores[behavior_type] = behavior_scores.get(behavior_type, 0) + frequency
            
            return {
                "user_id": user_id,
                "category_preferences": dict(sorted(category_scores.items(), key=lambda x: x[1], reverse=True)),
                "brand_preferences": dict(sorted(brand_scores.items(), key=lambda x: x[1], reverse=True)),
                "behavior_patterns": behavior_scores,
                "total_behaviors": len(behaviors),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取用户行为画像失败: {e}")
            return {
                "user_id": user_id,
                "category_preferences": {},
                "brand_preferences": {},
                "behavior_patterns": {},
                "total_behaviors": 0,
                "analysis_date": datetime.now().isoformat()
            }
    
    async def get_hybrid_recommendations(
        self, 
        user_id: str, 
        user_input: str = None,
        db: AsyncSession = None,
        limit: int = 10,
        strategy: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        生成混合推荐结果
        """
        try:
            # 1. 获取用户行为画像
            behavior_profile = await self.get_user_behavior_profile(user_id, db)
            
            # 2. AI意图分析（如果有用户输入）
            intent_analysis = None
            if user_input:
                intent_analysis = await self.analyze_user_intent(user_input, user_id)
            
            # 3. 获取基础产品数据
            products = await self._get_all_products(db)
            
            # 4. 计算多种推荐分数
            recommendations = []
            
            for product in products:
                # 意图相关分数
                intent_score = 0.0
                if intent_analysis:
                    intent_score = self._calculate_intent_score(product, intent_analysis)
                
                # 行为相关分数
                behavior_score = self._calculate_behavior_score(product, behavior_profile)
                
                # 协同过滤分数
                collaborative_score = await self._calculate_collaborative_score(product, user_id, db)
                
                # 内容过滤分数
                content_score = self._calculate_content_score(product, behavior_profile)
                
                # 热门度分数
                popularity_score = self._calculate_popularity_score(product, db)
                
                # 混合分数计算
                if strategy == "hybrid":
                    final_score = (
                        intent_score * self.strategy_weights['intent_based'] +
                        behavior_score * self.strategy_weights['collaborative'] +
                        content_score * self.strategy_weights['content_based'] +
                        popularity_score * self.strategy_weights['popularity']
                    )
                elif strategy == "intent_based":
                    final_score = intent_score
                elif strategy == "behavior_based":
                    final_score = behavior_score
                else:
                    final_score = (intent_score + behavior_score + content_score) / 3
                
                if final_score > 0.1:  # 只返回有意义的推荐
                    recommendations.append({
                        "product_id": product["id"],
                        "name": product["name"],
                        "category": product["category"],
                        "brand": product["brand"],
                        "price": product["price"],
                        "image_url": product.get("image_url", ""),
                        "final_score": round(final_score, 3),
                        "intent_score": round(intent_score, 3),
                        "behavior_score": round(behavior_score, 3),
                        "collaborative_score": round(collaborative_score, 3),
                        "content_score": round(content_score, 3),
                        "popularity_score": round(popularity_score, 3),
                        "recommendation_reason": self._generate_recommendation_reason(
                            product, intent_analysis, behavior_profile, final_score
                        )
                    })
            
            # 排序并返回结果
            recommendations.sort(key=lambda x: x["final_score"], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"混合推荐生成失败: {e}")
            return []
    
    def _calculate_intent_score(self, product: Dict[str, Any], intent_analysis: Dict[str, Any]) -> float:
        """计算意图相关分数"""
        score = 0.0
        
        # 意图类型权重
        intent_type = intent_analysis.get("intent_type", "信息查询")
        intent_weight = self.intent_weights.get(intent_type, 0.5)
        
        # 类别匹配
        product_categories = [product["category"].lower()]
        preferred_categories = [cat.lower() for cat in intent_analysis.get("product_categories", [])]
        
        if any(cat in preferred_categories for cat in product_categories):
            score += 0.5
        
        # 价格范围匹配
        price_range = intent_analysis.get("price_range", "中")
        if price_range == "低" and product["price"] < 1000:
            score += 0.3
        elif price_range == "中" and 1000 <= product["price"] <= 5000:
            score += 0.3
        elif price_range == "高" and product["price"] > 5000:
            score += 0.3
        
        # 品牌偏好匹配
        brand_preferences = intent_analysis.get("brand_preferences", [])
        if product["brand"] in brand_preferences:
            score += 0.4
        
        # 紧急程度加分
        urgency = intent_analysis.get("urgency_level", 0.5)
        score *= (0.5 + urgency * 0.5)  # 紧急程度调整分数
        
        return score * intent_weight
    
    def _calculate_behavior_score(self, product: Dict[str, Any], behavior_profile: Dict[str, Any]) -> float:
        """计算行为相关分数"""
        score = 0.0
        
        # 类别偏好
        category_prefs = behavior_profile.get("category_preferences", {})
        if product["category"] in category_prefs:
            score += min(category_prefs[product["category"]] / 10, 1.0)
        
        # 品牌偏好
        brand_prefs = behavior_profile.get("brand_preferences", {})
        if product["brand"] in brand_prefs:
            score += min(brand_prefs[product["brand"]] / 5, 1.0)
        
        return min(score, 1.0)
    
    async def _calculate_collaborative_score(self, product: Dict[str, Any], user_id: str, db: AsyncSession) -> float:
        """计算协同过滤分数"""
        try:
            # 查找相似用户对产品的偏好
            query = text("""
                SELECT COUNT(*) as similar_users
                FROM user_behaviors ub1
                JOIN user_behaviors ub2 ON ub1.product_id = ub2.product_id 
                    AND ub1.user_id != ub2.user_id
                WHERE ub1.user_id = :user_id 
                AND ub2.product_id = :product_id
                AND ub1.behavior_type IN ('purchase', 'click')
                AND ub2.behavior_type IN ('purchase', 'click')
            """)
            
            result = await db.execute(query, {
                "user_id": user_id,
                "product_id": product["id"]
            })
            
            similar_users = result.fetchone()[0]
            return min(similar_users / 5, 1.0)  # 归一化分数
            
        except Exception as e:
            logger.error(f"协同过滤计算失败: {e}")
            return 0.0
    
    def _calculate_content_score(self, product: Dict[str, Any], behavior_profile: Dict[str, Any]) -> float:
        """计算内容过滤分数"""
        # 基于产品属性和用户偏好的内容相似度
        score = 0.0
        
        # 如果用户有类别偏好，同类产品得分更高
        category_prefs = behavior_profile.get("category_preferences", {})
        if product["category"] in category_prefs:
            score += 0.5
        
        # 价格合理性（基于用户行为模式）
        behavior_patterns = behavior_profile.get("behavior_patterns", {})
        if behavior_patterns:
            # 根据用户行为调整价格合理性评分
            if behavior_patterns.get('purchase', 0) > 0:
                # 有购买行为的用户，价格敏感度较低
                score += 0.3
            else:
                # 无购买行为的用户，价格敏感度较高
                if product["price"] < 3000:
                    score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_popularity_score(self, product: Dict[str, Any], db: AsyncSession) -> float:
        """计算热门度分数"""
        try:
            # 这里可以添加产品热度计算逻辑
            # 目前使用简单的评分作为热度指标
            rating = product.get("rating", 4.0)
            return rating / 5.0
        except Exception:
            return 0.5
    
    def _generate_recommendation_reason(
        self, 
        product: Dict[str, Any], 
        intent_analysis: Optional[Dict[str, Any]], 
        behavior_profile: Dict[str, Any],
        score: float
    ) -> str:
        """生成推荐理由"""
        reasons = []
        
        if intent_analysis:
            intent_type = intent_analysis.get("intent_type", "信息查询")
            if intent_type == "产品购买":
                reasons.append("符合您的购买意图")
            elif intent_type == "价格比较":
                reasons.append("价格符合您的预算")
            
            # 类别匹配
            preferred_categories = intent_analysis.get("product_categories", [])
            if product["category"] in preferred_categories:
                reasons.append(f"匹配您感兴趣的{product['category']}类别")
        
        # 行为偏好
        category_prefs = behavior_profile.get("category_preferences", {})
        if product["category"] in category_prefs and category_prefs[product["category"]] > 5:
            reasons.append("基于您的浏览历史推荐")
        
        brand_prefs = behavior_profile.get("brand_preferences", {})
        if product["brand"] in brand_prefs and brand_prefs[product["brand"]] > 3:
            reasons.append(f"您对{product['brand']}品牌有偏好")
        
        # 评分因素
        if product.get("rating", 0) >= 4.5:
            reasons.append("高评分热门产品")
        
        if not reasons:
            reasons.append("基于综合算法推荐")
        
        return "；".join(reasons[:2])  # 最多显示两个理由
    
    async def _get_all_products(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """获取所有产品数据"""
        try:
            query = text("SELECT * FROM products ORDER BY rating DESC")
            result = await db.execute(query)
            products = []
            
            for row in result:
                product = {
                    "id": row[0],
                    "name": row[1],
                    "category": row[2],
                    "brand": row[3],
                    "price": row[4],
                    "description": row[5],
                    "rating": row[6],
                    "image_url": row[7] if len(row) > 7 else ""
                }
                products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"获取产品数据失败: {e}")
            return []

# 创建全局推荐引擎实例
hybrid_recommendation_engine = HybridRecommendationEngine()