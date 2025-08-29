"""
内存数据提供者 - 当数据库不可用时使用
提供产品数据、用户行为数据等的内存版本
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random

class MemoryDataProvider:
    """内存数据提供者，用于演示和测试"""
    
    def __init__(self):
        self.products = self._create_sample_products()
        self.user_behaviors = self._create_sample_user_behaviors()
        self.user_profiles = self._create_sample_user_profiles()
        self.recommendations = []
        
    def _create_sample_products(self) -> List[Dict[str, Any]]:
        """创建示例产品数据"""
        return [
            {
                "id": 1,
                "product_id": "laptop_001",
                "name": "ThinkPad X1 Carbon",
                "category": "笔记本电脑",
                "brand": "联想",
                "price": 8999.00,
                "rating": 4.8,
                "description": "轻薄商务笔记本，搭载Intel i7处理器，16GB内存，512GB固态硬盘",
                "image_url": "/images/laptop_001.jpg",
                "stock_quantity": 50,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 2,
                "product_id": "laptop_002",
                "name": "MacBook Air M2",
                "category": "笔记本电脑",
                "brand": "苹果",
                "price": 7999.00,
                "rating": 4.9,
                "description": "全新M2芯片，13.6英寸Liquid Retina显示屏，18小时电池续航",
                "image_url": "/images/laptop_002.jpg",
                "stock_quantity": 30,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 3,
                "product_id": "laptop_003",
                "name": "小新Pro 16",
                "category": "笔记本电脑",
                "brand": "联想",
                "price": 5499.00,
                "rating": 4.5,
                "description": "16英寸大屏，AMD锐龙7处理器，16GB内存，512GB固态硬盘",
                "image_url": "/images/laptop_003.jpg",
                "stock_quantity": 80,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 4,
                "product_id": "laptop_004",
                "name": "华硕天选游戏本",
                "category": "笔记本电脑",
                "brand": "华硕",
                "price": 6999.00,
                "rating": 4.6,
                "description": "15.6英寸游戏本，Intel i7处理器，RTX 4060显卡，16GB内存",
                "image_url": "/images/laptop_004.jpg",
                "stock_quantity": 25,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 5,
                "product_id": "laptop_005",
                "name": "戴尔灵越14",
                "category": "笔记本电脑",
                "brand": "戴尔",
                "price": 4599.00,
                "rating": 4.3,
                "description": "14英寸轻薄本，Intel i5处理器，8GB内存，256GB固态硬盘",
                "image_url": "/images/laptop_005.jpg",
                "stock_quantity": 60,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 6,
                "product_id": "phone_001",
                "name": "iPhone 15 Pro",
                "category": "智能手机",
                "brand": "苹果",
                "price": 7999.00,
                "rating": 4.9,
                "description": "A17 Pro芯片，48MP主摄，钛金属设计，支持Action Button",
                "image_url": "/images/phone_001.jpg",
                "stock_quantity": 100,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 7,
                "product_id": "phone_002",
                "name": "华为Mate 60 Pro",
                "category": "智能手机",
                "brand": "华为",
                "price": 6999.00,
                "rating": 4.7,
                "description": "麒麟9000S芯片，50MP三摄，卫星通话，昆仑玻璃",
                "image_url": "/images/phone_002.jpg",
                "stock_quantity": 80,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 8,
                "product_id": "phone_003",
                "name": "小米14",
                "category": "智能手机",
                "brand": "小米",
                "price": 3999.00,
                "rating": 4.5,
                "description": "骁龙8 Gen 3处理器，50MP徕卡三摄，90W快充",
                "image_url": "/images/phone_003.jpg",
                "stock_quantity": 150,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 9,
                "product_id": "tablet_001",
                "name": "iPad Pro 12.9",
                "category": "平板电脑",
                "brand": "苹果",
                "price": 8999.00,
                "rating": 4.8,
                "description": "M2芯片，12.9英寸Liquid Retina XDR显示屏，支持Apple Pencil",
                "image_url": "/images/tablet_001.jpg",
                "stock_quantity": 40,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 10,
                "product_id": "tablet_002",
                "name": "Surface Pro 9",
                "category": "平板电脑",
                "brand": "微软",
                "price": 7999.00,
                "rating": 4.6,
                "description": "Intel i7处理器，13英寸触摸屏，支持Surface Pen，可拆卸键盘",
                "image_url": "/images/tablet_002.jpg",
                "stock_quantity": 35,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 11,
                "product_id": "headphone_001",
                "name": "AirPods Pro 2",
                "category": "耳机",
                "brand": "苹果",
                "price": 1899.00,
                "rating": 4.8,
                "description": "主动降噪，空间音频，自适应透明模式，6小时续航",
                "image_url": "/images/headphone_001.jpg",
                "stock_quantity": 200,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 12,
                "product_id": "headphone_002",
                "name": "索尼WH-1000XM5",
                "category": "耳机",
                "brand": "索尼",
                "price": 2499.00,
                "rating": 4.9,
                "description": "业界领先降噪，30小时续航，Hi-Res音质，多点连接",
                "image_url": "/images/headphone_002.jpg",
                "stock_quantity": 80,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
    
    def _create_sample_user_behaviors(self) -> List[Dict[str, Any]]:
        """创建示例用户行为数据"""
        base_time = datetime.now() - timedelta(days=30)
        behaviors = []
        
        behavior_data = [
            ("user_001", "session_001", "view", "laptop_001", "笔记本电脑", "联想", "ThinkPad X1 Carbon", 8999.00, {"action": "view", "duration": 45}),
            ("user_001", "session_001", "click", "laptop_001", "笔记本电脑", "联想", "ThinkPad X1 Carbon", 8999.00, {"action": "click", "element": "specs"}),
            ("user_001", "session_002", "search", None, "笔记本电脑", None, None, None, {"query": "商务笔记本", "results": 12}),
            ("user_001", "session_002", "view", "laptop_003", "笔记本电脑", "联想", "小新Pro 16", 5499.00, {"action": "view", "duration": 32}),
            ("user_001", "session_003", "view", "phone_002", "智能手机", "华为", "华为Mate 60 Pro", 6999.00, {"action": "view", "duration": 28}),
            ("user_001", "session_003", "click", "phone_002", "智能手机", "华为", "华为Mate 60 Pro", 6999.00, {"action": "click", "element": "camera"}),
            
            ("user_002", "session_004", "view", "phone_001", "智能手机", "苹果", "iPhone 15 Pro", 7999.00, {"action": "view", "duration": 67}),
            ("user_002", "session_004", "click", "phone_001", "智能手机", "苹果", "iPhone 15 Pro", 7999.00, {"action": "click", "element": "buy"}),
            ("user_002", "session_005", "purchase", "phone_001", "智能手机", "苹果", "iPhone 15 Pro", 7999.00, {"action": "purchase", "quantity": 1}),
            ("user_002", "session_006", "view", "tablet_001", "平板电脑", "苹果", "iPad Pro 12.9", 8999.00, {"action": "view", "duration": 23}),
            ("user_002", "session_006", "click", "tablet_001", "平板电脑", "苹果", "iPad Pro 12.9", 8999.00, {"action": "click", "element": "specs"}),
            
            ("user_003", "session_007", "search", None, "耳机", None, None, None, {"query": "降噪耳机", "results": 8}),
            ("user_003", "session_007", "view", "headphone_002", "耳机", "索尼", "索尼WH-1000XM5", 2499.00, {"action": "view", "duration": 89}),
            ("user_003", "session_007", "click", "headphone_002", "耳机", "索尼", "索尼WH-1000XM5", 2499.00, {"action": "click", "element": "features"}),
            ("user_003", "session_008", "view", "headphone_001", "耳机", "苹果", "AirPods Pro 2", 1899.00, {"action": "view", "duration": 45}),
            ("user_003", "session_008", "click", "headphone_001", "耳机", "苹果", "AirPods Pro 2", 1899.00, {"action": "click", "element": "compare"}),
            
            ("user_004", "session_009", "view", "laptop_002", "笔记本电脑", "苹果", "MacBook Air M2", 7999.00, {"action": "view", "duration": 34}),
            ("user_004", "session_009", "click", "laptop_002", "笔记本电脑", "苹果", "MacBook Air M2", 7999.00, {"action": "click", "element": "details"}),
            ("user_004", "session_010", "search", None, "笔记本电脑", None, None, None, {"query": "游戏本", "results": 15}),
            ("user_004", "session_010", "view", "laptop_004", "笔记本电脑", "华硕", "华硕天选游戏本", 6999.00, {"action": "view", "duration": 56}),
            ("user_004", "session_010", "click", "laptop_004", "笔记本电脑", "华硕", "华硕天选游戏本", 6999.00, {"action": "click", "element": "gpu"}),
            
            ("user_005", "session_011", "view", "tablet_002", "平板电脑", "微软", "Surface Pro 9", 7999.00, {"action": "view", "duration": 29}),
            ("user_005", "session_011", "click", "tablet_002", "平板电脑", "微软", "Surface Pro 9", 7999.00, {"action": "click", "element": "display"}),
            ("user_005", "session_012", "view", "phone_003", "智能手机", "小米", "小米14", 3999.00, {"action": "view", "duration": 41}),
            ("user_005", "session_012", "click", "phone_003", "智能手机", "小米", "小米14", 3999.00, {"action": "click", "element": "camera"}),
            ("user_005", "session_013", "purchase", "phone_003", "智能手机", "小米", "小米14", 3999.00, {"action": "purchase", "quantity": 1})
        ]
        
        for i, (user_id, session_id, behavior_type, product_id, category, brand, product_name, price, data) in enumerate(behavior_data):
            behaviors.append({
                "id": i + 1,
                "user_id": user_id,
                "session_id": session_id,
                "behavior_type": behavior_type,
                "behavior_data": json.dumps(data),
                "product_id": product_id,
                "category": category,
                "brand": brand,
                "product_name": product_name,
                "price": price,
                "timestamp": base_time + timedelta(days=i, hours=random.randint(1, 23)),
                "created_at": base_time + timedelta(days=i, hours=random.randint(1, 23))
            })
        
        return behaviors
    
    def _create_sample_user_profiles(self) -> List[Dict[str, Any]]:
        """创建示例用户画像数据"""
        return [
            {
                "id": 1,
                "user_id": "user_001",
                "profile_data": json.dumps({
                    "preferences": {
                        "price_sensitivity": 0.7,
                        "brand_loyalty": 0.3,
                        "quality_focus": 0.8
                    },
                    "behavior_pattern": "researcher"
                }),
                "preferred_categories": ["笔记本电脑", "智能手机"],
                "preferred_brands": ["联想", "华为"],
                "price_range_min": 4000.00,
                "price_range_max": 9000.00,
                "behavior_score": 75.5,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 2,
                "user_id": "user_002",
                "profile_data": json.dumps({
                    "preferences": {
                        "price_sensitivity": 0.2,
                        "brand_loyalty": 0.9,
                        "quality_focus": 0.9
                    },
                    "behavior_pattern": "premium_buyer"
                }),
                "preferred_categories": ["智能手机", "平板电脑"],
                "preferred_brands": ["苹果"],
                "price_range_min": 6000.00,
                "price_range_max": 12000.00,
                "behavior_score": 92.3,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 3,
                "user_id": "user_003",
                "profile_data": json.dumps({
                    "preferences": {
                        "price_sensitivity": 0.5,
                        "brand_loyalty": 0.4,
                        "quality_focus": 0.7
                    },
                    "behavior_pattern": "audio_enthusiast"
                }),
                "preferred_categories": ["耳机"],
                "preferred_brands": ["索尼", "苹果"],
                "price_range_min": 1500.00,
                "price_range_max": 3000.00,
                "behavior_score": 68.9,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 4,
                "user_id": "user_004",
                "profile_data": json.dumps({
                    "preferences": {
                        "price_sensitivity": 0.6,
                        "brand_loyalty": 0.5,
                        "quality_focus": 0.8
                    },
                    "behavior_pattern": "gamer"
                }),
                "preferred_categories": ["笔记本电脑"],
                "preferred_brands": ["华硕", "苹果"],
                "price_range_min": 5000.00,
                "price_range_max": 10000.00,
                "behavior_score": 71.2,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 5,
                "user_id": "user_005",
                "profile_data": json.dumps({
                    "preferences": {
                        "price_sensitivity": 0.8,
                        "brand_loyalty": 0.3,
                        "quality_focus": 0.6
                    },
                    "behavior_pattern": "budget_conscious"
                }),
                "preferred_categories": ["智能手机", "平板电脑"],
                "preferred_brands": ["小米", "华为"],
                "price_range_min": 2000.00,
                "price_range_max": 6000.00,
                "behavior_score": 58.7,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
    
    def get_products(self, limit: int = 50, category: str = None) -> List[Dict[str, Any]]:
        """获取产品列表"""
        products = self.products
        if category:
            products = [p for p in products if p["category"] == category]
        return products[:limit]
    
    def get_user_behaviors(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户行为数据"""
        behaviors = [b for b in self.user_behaviors if b["user_id"] == user_id]
        return sorted(behaviors, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户画像"""
        profiles = [p for p in self.user_profiles if p["user_id"] == user_id]
        return profiles[0] if profiles else None
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近活动"""
        activities = sorted(self.user_behaviors, key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]
    
    def get_popular_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门产品"""
        # 统计产品被查看的次数
        view_counts = {}
        for behavior in self.user_behaviors:
            if behavior["behavior_type"] == "view" and behavior["product_id"]:
                product_id = behavior["product_id"]
                view_counts[product_id] = view_counts.get(product_id, 0) + 1
        
        # 按查看次数排序
        popular_product_ids = sorted(view_counts.items(), key=lambda x: x[1], reverse=True)
        popular_products = []
        
        for product_id, count in popular_product_ids[:limit]:
            product = next((p for p in self.products if p["product_id"] == product_id), None)
            if product:
                product_copy = product.copy()
                product_copy["view_count"] = count
                popular_products.append(product_copy)
        
        return popular_products
    
    def get_category_stats(self) -> Dict[str, Any]:
        """获取类别统计"""
        stats = {}
        for behavior in self.user_behaviors:
            category = behavior["category"]
            if category:
                if category not in stats:
                    stats[category] = {"views": 0, "clicks": 0, "purchases": 0}
                
                if behavior["behavior_type"] == "view":
                    stats[category]["views"] += 1
                elif behavior["behavior_type"] == "click":
                    stats[category]["clicks"] += 1
                elif behavior["behavior_type"] == "purchase":
                    stats[category]["purchases"] += 1
        
        return stats

# 全局内存数据提供者实例
memory_data_provider = MemoryDataProvider()