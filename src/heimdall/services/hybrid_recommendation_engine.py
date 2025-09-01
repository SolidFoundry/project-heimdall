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

from src.heimdall.services.llm_service import llm_service
from src.heimdall.core.config import settings

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
            'behavior_based': 0.25,  # 用户行为权重
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
            error_msg = str(e)
            logger.error(f"AI意图分析失败: {error_msg}")
            
            # 检查是否是连接错误
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                logger.warning("AI服务连接失败，使用离线意图分析")
                return self._offline_intent_analysis(user_input)
            
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
    
    def _offline_intent_analysis(self, user_input: str) -> Dict[str, Any]:
        """离线意图分析 - 当AI服务不可用时使用"""
        logger.info(f"执行离线意图分析: {user_input[:50]}...")
        
        # 简单的关键词匹配
        input_lower = user_input.lower()
        
        # 意图类型关键词
        intent_keywords = {
            "产品购买": ["买", "购买", "要", "想买", "订购", "下单", "获取"],
            "价格比较": ["价格", "多少钱", "贵", "便宜", "对比", "比较", "性价比"],
            "信息查询": ["什么", "怎么样", "如何", "介绍", "了解", "说明"],
            "品牌了解": ["品牌", "牌子", "哪个好", "推荐", "评价"],
            "售后服务": ["保修", "售后", "服务", "维修", "退换"]
        }
        
        # 确定意图类型
        intent_type = "信息查询"
        max_matches = 0
        
        for intent, keywords in intent_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in input_lower)
            if matches > max_matches:
                max_matches = matches
                intent_type = intent
        
        # 产品类别关键词
        category_keywords = {
            "手机": ["手机", "iphone", "华为", "小米", "oppo", "vivo"],
            "笔记本": ["笔记本", "电脑", "macbook", "联想", "戴尔", "惠普"],
            "耳机": ["耳机", "airpods", "蓝牙", "音响"],
            "平板": ["平板", "ipad", "tablet"],
            "相机": ["相机", "摄像机", "单反"]
        }
        
        matched_categories = []
        for category, keywords in category_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                matched_categories.append(category)
        
        # 价格范围分析
        price_range = "中"
        if any(word in input_lower for word in ["便宜", "经济", "低价", "预算"]):
            price_range = "低"
        elif any(word in input_lower for word in ["贵", "高端", "旗舰", "最好"]):
            price_range = "高"
        
        # 紧急程度
        urgency_level = 0.5
        if any(word in input_lower for word in ["马上", "立即", "现在", "急"]):
            urgency_level = 0.8
        elif any(word in input_lower for word in ["看看", "了解", "考虑"]):
            urgency_level = 0.3
        
        # 提取关键词
        keywords = []
        for category, category_keys in category_keywords.items():
            for key in category_keys:
                if key in input_lower and key not in keywords:
                    keywords.append(key)
        
        result = {
            "intent_type": intent_type,
            "confidence": min(0.6 + max_matches * 0.1, 0.9),
            "product_categories": matched_categories,
            "price_range": price_range,
            "brand_preferences": [],
            "urgency_level": urgency_level,
            "keywords": keywords[:5],  # 最多5个关键词
            "analysis_summary": f"离线分析识别为{intent_type}意图"
        }
        
        logger.info(f"离线意图分析完成: {intent_type}")
        return result
    
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
                "category_preferences": dict(sorted(category_scores.items(), key=lambda x: float(x[1]), reverse=True)),
                "brand_preferences": dict(sorted(brand_scores.items(), key=lambda x: float(x[1]), reverse=True)),
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
            
            # 确保final_score是数值类型，然后排序
            for rec in recommendations:
                if isinstance(rec["final_score"], str):
                    try:
                        rec["final_score"] = float(rec["final_score"])
                    except (ValueError, TypeError):
                        rec["final_score"] = 0.0
                elif not isinstance(rec["final_score"], (int, float)):
                    rec["final_score"] = 0.0
            
            # 排序并返回结果
            recommendations.sort(key=lambda x: float(x["final_score"]), reverse=True)
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
        if product["category"] in category_prefs:
            try:
                category_score = float(category_prefs[product["category"]])
                if category_score > 5:
                    reasons.append("基于您的浏览历史推荐")
            except (ValueError, TypeError):
                pass
        
        brand_prefs = behavior_profile.get("brand_preferences", {})
        if product["brand"] in brand_prefs:
            try:
                brand_score = float(brand_prefs[product["brand"]])
                if brand_score > 3:
                    reasons.append(f"您对{product['brand']}品牌有偏好")
            except (ValueError, TypeError):
                pass
        
        # 评分因素
        rating = product.get("rating", 0)
        try:
            rating_float = float(rating)
            if rating_float >= 4.5:
                reasons.append("高评分热门产品")
        except (ValueError, TypeError):
            pass
        
        if not reasons:
            reasons.append("基于综合算法推荐")
        
        return "；".join(reasons[:2])  # 最多显示两个理由
    
    async def _get_all_products(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """获取所有产品数据"""
        try:
            query = text("""
                SELECT id, name, category, brand, price, description, rating, image_url 
                FROM products 
                ORDER BY rating DESC
            """)
            result = await db.execute(query)
            products = []
            
            for row in result:
                try:
                    product = {
                        "id": int(row[0]) if row[0] is not None else 0,
                        "name": str(row[1]) if row[1] is not None else "",
                        "category": str(row[2]) if row[2] is not None else "",
                        "brand": str(row[3]) if row[3] is not None else "",
                        "price": float(row[4]) if row[4] is not None else 0.0,
                        "description": str(row[5]) if row[5] is not None else "",
                        "rating": float(row[6]) if row[6] is not None else 0.0,
                        "image_url": str(row[7]) if row[7] is not None else ""
                    }
                    products.append(product)
                except (ValueError, TypeError) as e:
                    logger.warning(f"跳过无效产品数据: {row}, 错误: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"获取产品数据失败: {e}")
            return []

# 创建全局推荐引擎实例
hybrid_recommendation_engine = HybridRecommendationEngine()