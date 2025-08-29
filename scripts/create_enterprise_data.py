#!/usr/bin/env python3
"""
企业级电商数据初始化脚本
创建完整的产品目录、用户行为数据和推荐系统
"""

import asyncio
import sys
import os
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import uuid

# 数据库配置
DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/heimdall_db"

# 企业级产品数据
ENTERPRISE_PRODUCTS = [
    # 电子产品类
    {
        "name": "iPhone 15 Pro Max",
        "description": "苹果旗舰手机，搭载A17 Pro芯片，钛金属设计",
        "price": 9999.0,
        "category_id": 1,
        "brand": "Apple",
        "image_url": "https://example.com/iphone15promax.jpg",
        "tags": ["智能手机", "5G", "拍照", "钛金属", "A17 Pro"],
        "attributes": {
            "storage": "256GB",
            "color": "原色钛金属",
            "camera": "48MP主摄",
            "battery": "4422mAh",
            "display": "6.7英寸OLED"
        },
        "stock_quantity": 150,
        "rating": 4.8,
        "review_count": 2580
    },
    {
        "name": "MacBook Pro 16英寸",
        "description": "专业级笔记本电脑，M3 Max芯片，为专业人士设计",
        "price": 25999.0,
        "category_id": 1,
        "brand": "Apple",
        "image_url": "https://example.com/macbookpro16.jpg",
        "tags": ["笔记本", "M3 Max", "专业", "开发", "设计"],
        "attributes": {
            "memory": "36GB",
            "storage": "1TB SSD",
            "chip": "M3 Max",
            "display": "16.2英寸Liquid Retina XDR",
            "battery": "100Wh"
        },
        "stock_quantity": 75,
        "rating": 4.9,
        "review_count": 1240
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "description": "三星旗舰手机，S Pen内置，AI摄影功能",
        "price": 8999.0,
        "category_id": 1,
        "brand": "Samsung",
        "image_url": "https://example.com/galaxys24ultra.jpg",
        "tags": ["智能手机", "S Pen", "AI摄影", "安卓旗舰"],
        "attributes": {
            "storage": "512GB",
            "color": "钛灰色",
            "camera": "200MP主摄",
            "battery": "5000mAh",
            "display": "6.8英寸Dynamic AMOLED 2X"
        },
        "stock_quantity": 200,
        "rating": 4.7,
        "review_count": 1890
    },
    {
        "name": "AirPods Pro 2",
        "description": "主动降噪无线耳机，空间音频，自适应透明模式",
        "price": 1899.0,
        "category_id": 1,
        "brand": "Apple",
        "image_url": "https://example.com/airpodspro2.jpg",
        "tags": ["无线耳机", "降噪", "空间音频", "蓝牙"],
        "attributes": {
            "battery_life": "6小时(开启降噪)",
            "charging_case": "30小时",
            "noise_cancellation": "主动降噪",
            "connectivity": "蓝牙5.3"
        },
        "stock_quantity": 300,
        "rating": 4.6,
        "review_count": 3200
    },
    {
        "name": "iPad Pro 12.9英寸",
        "description": "专业级平板电脑，M2芯片，Liquid Retina XDR显示屏",
        "price": 8799.0,
        "category_id": 1,
        "brand": "Apple",
        "image_url": "https://example.com/ipadpro129.jpg",
        "tags": ["平板电脑", "M2", "专业", "创作", "设计"],
        "attributes": {
            "storage": "128GB",
            "display": "12.9英寸Liquid Retina XDR",
            "chip": "M2",
            "connectivity": "Wi-Fi 6E + 5G"
        },
        "stock_quantity": 120,
        "rating": 4.8,
        "review_count": 1560
    },
    
    # 服装类
    {
        "name": "Uniqlo Ultra Light Down Jacket",
        "description": "优衣库轻型羽绒服，保暖轻便，多色可选",
        "price": 599.0,
        "category_id": 2,
        "brand": "Uniqlo",
        "image_url": "https://example.com/uniqlojacket.jpg",
        "tags": ["羽绒服", "轻薄", "保暖", "休闲"],
        "attributes": {
            "material": "尼龙100%",
            "filling": "90%白鹅绒",
            "weight": "205g",
            "colors": ["黑色", "藏青", "酒红", "米色"]
        },
        "stock_quantity": 500,
        "rating": 4.4,
        "review_count": 4200
    },
    {
        "name": "Nike Air Jordan 1 Retro",
        "description": "经典篮球鞋复刻版，潮流文化象征",
        "price": 1299.0,
        "category_id": 2,
        "brand": "Nike",
        "image_url": "https://example.com/airjordan1.jpg",
        "tags": ["篮球鞋", "复古", "潮流", "限量版"],
        "attributes": {
            "style": "High Top",
            "material": "皮革",
            "colorway": "Chicago",
            "year": "1985复刻"
        },
        "stock_quantity": 80,
        "rating": 4.7,
        "review_count": 890
    },
    {
        "name": "Zara Professional Suit",
        "description": "Zara专业商务套装，修身剪裁，职场必备",
        "price": 899.0,
        "category_id": 2,
        "brand": "Zara",
        "image_url": "https://example.com/zarasuit.jpg",
        "tags": ["商务套装", "正装", "职场", "修身"],
        "attributes": {
            "material": "羊毛混纺",
            "fit": "修身版型",
            "colors": ["黑色", "深蓝", "灰色"],
            "sizes": ["S", "M", "L", "XL"]
        },
        "stock_quantity": 150,
        "rating": 4.3,
        "review_count": 560
    },
    
    # 家居类
    {
        "name": "IKEA MALM Bed Frame",
        "description": "宜家MALM床架，简约北欧风格，实木质感",
        "price": 799.0,
        "category_id": 3,
        "brand": "IKEA",
        "image_url": "https://example.com/ikeamalm.jpg",
        "tags": ["床架", "北欧风格", "简约", "实木"],
        "attributes": {
            "size": "180x200cm",
            "material": "白蜡木贴面",
            "color": "白色棕褐色",
            "style": "北欧简约"
        },
        "stock_quantity": 60,
        "rating": 4.5,
        "review_count": 1280
    },
    {
        "name": "Dyson V15 Detect Vacuum",
        "description": "戴森无绳吸尘器，激光检测灰尘，强劲吸力",
        "price": 4590.0,
        "category_id": 3,
        "brand": "Dyson",
        "image_url": "https://example.com/dysonv15.jpg",
        "tags": ["吸尘器", "无绳", "激光检测", "智能"],
        "attributes": {
            "battery_life": "60分钟",
            "suction_power": "240AW",
            "weight": "3.0kg",
            "features": ["激光检测", "LCD屏幕", "智能调节"]
        },
        "stock_quantity": 90,
        "rating": 4.8,
        "review_count": 2340
    },
    
    # 运动户外类
    {
        "name": "Adidas Ultraboost 22",
        "description": "阿迪达斯顶级跑鞋，Boost中底，能量回弹",
        "price": 1299.0,
        "category_id": 4,
        "brand": "Adidas",
        "image_url": "https://example.com/ultraboost22.jpg",
        "tags": ["跑鞋", "Boost", "能量回弹", "专业跑步"],
        "attributes": {
            "weight": "340g",
            "drop": "10mm",
            "upper": "Primeknit编织鞋面",
            "technology": "Boost中底"
        },
        "stock_quantity": 180,
        "rating": 4.6,
        "review_count": 1670
    },
    {
        "name": "The North Face Summit Series",
        "description": "北面顶级冲锋衣，防水透气，登山探险",
        "price": 3999.0,
        "category_id": 4,
        "brand": "The North Face",
        "image_url": "https://example.com/summitseries.jpg",
        "tags": ["冲锋衣", "防水", "透气", "登山", "探险"],
        "attributes": {
            "waterproof": "20000mm",
            "breathability": "25000g/m²/24h",
            "material": "Gore-Tex Pro",
            "weight": "450g"
        },
        "stock_quantity": 45,
        "rating": 4.9,
        "review_count": 340
    },
    
    # 美妆护肤类
    {
        "name": "SK-II Facial Treatment Essence",
        "description": "SK-II神仙水，含有Pitera™精华，改善肌肤质地",
        "price": 1540.0,
        "category_id": 5,
        "brand": "SK-II",
        "image_url": "https://example.com/sk2essence.jpg",
        "tags": ["精华液", "Pitera", "保湿", "修复"],
        "attributes": {
            "volume": "230ml",
            "key_ingredient": "Pitera™",
            "skin_type": "所有肤质",
            "effects": ["保湿", "修复", "美白", "抗老"]
        },
        "stock_quantity": 200,
        "rating": 4.7,
        "review_count": 4500
    },
    {
        "name": "Lancôme Advanced Génifique",
        "description": "兰蔻小黑瓶精华，修复肌底，激活年轻基因",
        "price": 1380.0,
        "category_id": 5,
        "brand": "Lancôme",
        "image_url": "https://example.com/genifique.jpg",
        "tags": ["精华液", "修复", "抗老", "肌底激活"],
        "attributes": {
            "volume": "100ml",
            "key_ingredient": "益生元精粹",
            "skin_type": "所有肤质",
            "effects": ["修复", "抗老", "紧致", "提亮"]
        },
        "stock_quantity": 180,
        "rating": 4.6,
        "review_count": 3200
    }
]

# 模拟用户行为数据
SIMULATED_USER_BEHAVIORS = [
    {
        "user_id": "user_001",
        "behaviors": [
            {"type": "search", "data": {"query": "iPhone 15 Pro", "category": "电子产品"}, "timestamp": datetime.now() - timedelta(days=5)},
            {"type": "view", "data": {"product_id": 1, "duration": 180}, "timestamp": datetime.now() - timedelta(days=5)},
            {"type": "click", "data": {"product_id": 1, "element": "add_to_cart"}, "timestamp": datetime.now() - timedelta(days=4)},
            {"type": "search", "data": {"query": "无线耳机", "category": "电子产品"}, "timestamp": datetime.now() - timedelta(days=3)},
            {"type": "view", "data": {"product_id": 4, "duration": 120}, "timestamp": datetime.now() - timedelta(days=3)},
            {"type": "purchase", "data": {"product_id": 4, "amount": 1899.0}, "timestamp": datetime.now() - timedelta(days=2)}
        ]
    },
    {
        "user_id": "user_002",
        "behaviors": [
            {"type": "search", "data": {"query": "笔记本电脑", "category": "电子产品"}, "timestamp": datetime.now() - timedelta(days=7)},
            {"type": "view", "data": {"product_id": 2, "duration": 300}, "timestamp": datetime.now() - timedelta(days=7)},
            {"type": "view", "data": {"product_id": 5, "duration": 240}, "timestamp": datetime.now() - timedelta(days=6)},
            {"type": "search", "data": {"query": "商务套装", "category": "服装"}, "timestamp": datetime.now() - timedelta(days=4)},
            {"type": "view", "data": {"product_id": 7, "duration": 90}, "timestamp": datetime.now() - timedelta(days=4)}
        ]
    },
    {
        "user_id": "user_003",
        "behaviors": [
            {"type": "search", "data": {"query": "跑鞋", "category": "运动户外"}, "timestamp": datetime.now() - timedelta(days=6)},
            {"type": "view", "data": {"product_id": 11, "duration": 150}, "timestamp": datetime.now() - timedelta(days=6)},
            {"type": "click", "data": {"product_id": 11, "element": "size_selector"}, "timestamp": datetime.now() - timedelta(days=5)},
            {"type": "search", "data": {"query": "冲锋衣", "category": "运动户外"}, "timestamp": datetime.now() - timedelta(days=3)},
            {"type": "view", "data": {"product_id": 12, "duration": 200}, "timestamp": datetime.now() - timedelta(days=3)}
        ]
    },
    {
        "user_id": "user_004",
        "behaviors": [
            {"type": "search", "data": {"query": "护肤品", "category": "美妆护肤"}, "timestamp": datetime.now() - timedelta(days=8)},
            {"type": "view", "data": {"product_id": 13, "duration": 180}, "timestamp": datetime.now() - timedelta(days=8)},
            {"type": "click", "data": {"product_id": 13, "element": "ingredients"}, "timestamp": datetime.now() - timedelta(days=7)},
            {"type": "view", "data": {"product_id": 14, "duration": 120}, "timestamp": datetime.now() - timedelta(days=6)},
            {"type": "purchase", "data": {"product_id": 13, "amount": 1540.0}, "timestamp": datetime.now() - timedelta(days=1)}
        ]
    },
    {
        "user_id": "user_005",
        "behaviors": [
            {"type": "search", "data": {"query": "家具", "category": "家居"}, "timestamp": datetime.now() - timedelta(days=10)},
            {"type": "view", "data": {"product_id": 9, "duration": 240}, "timestamp": datetime.now() - timedelta(days=10)},
            {"type": "view", "data": {"product_id": 10, "duration": 180}, "timestamp": datetime.now() - timedelta(days=9)},
            {"type": "search", "data": {"query": "羽绒服", "category": "服装"}, "timestamp": datetime.now() - timedelta(days=5)},
            {"type": "view", "data": {"product_id": 6, "duration": 120}, "timestamp": datetime.now() - timedelta(days=5)}
        ]
    }
]

async def create_enterprise_data():
    """创建企业级数据"""
    print("开始创建企业级电商数据...")
    
    # 创建数据库引擎
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # 创建会话工厂
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # 创建产品数据
            print("创建产品数据...")
            for product_data in ENTERPRISE_PRODUCTS:
                query = text("""
                    INSERT INTO products (name, description, price, category_id, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active)
                    VALUES (:name, :description, :price, :category_id, :brand, :image_url, :tags, :attributes, :stock_quantity, :rating, :review_count, :is_active)
                    RETURNING id
                """)
                
                result = await session.execute(query, {
                    "name": product_data["name"],
                    "description": product_data["description"],
                    "price": product_data["price"],
                    "category_id": product_data["category_id"],
                    "brand": product_data["brand"],
                    "image_url": product_data["image_url"],
                    "tags": product_data["tags"],
                    "attributes": product_data["attributes"],
                    "stock_quantity": product_data["stock_quantity"],
                    "rating": product_data["rating"],
                    "review_count": product_data["review_count"],
                    "is_active": True
                })
                
                product_id = result.scalar()
                print(f"创建产品: {product_data['name']} (ID: {product_id})")
            
            # 创建用户行为数据
            print("创建用户行为数据...")
            for user_data in SIMULATED_USER_BEHAVIORS:
                user_id = user_data["user_id"]
                
                for behavior in user_data["behaviors"]:
                    query = text("""
                        INSERT INTO user_behaviors (user_id, session_id, behavior_type, behavior_data, created_at)
                        VALUES (:user_id, :session_id, :behavior_type, :behavior_data, :created_at)
                    """)
                    
                    await session.execute(query, {
                        "user_id": user_id,
                        "session_id": f"session_{user_id}",
                        "behavior_type": behavior["type"],
                        "behavior_data": behavior["data"],
                        "created_at": behavior["timestamp"]
                    })
                
                print(f"创建用户行为数据: {user_id} ({len(user_data['behaviors'])} 个行为)")
            
            # 创建用户画像数据
            print("创建用户画像数据...")
            for user_data in SIMULATED_USER_BEHAVIORS:
                user_id = user_data["user_id"]
                
                # 基于行为分析用户偏好
                category_preferences = {}
                brand_preferences = {}
                price_range = {"min": float('inf'), "max": 0}
                
                for behavior in user_data["behaviors"]:
                    if behavior["type"] in ["view", "click", "purchase"]:
                        # 这里简化处理，实际应该根据产品ID查询详细信息
                        category_preferences["电子产品"] = category_preferences.get("电子产品", 0) + 1
                
                user_profile = {
                    "user_id": user_id,
                    "category_preferences": category_preferences,
                    "brand_preferences": brand_preferences,
                    "price_range": price_range,
                    "activity_level": len(user_data["behaviors"]),
                    "last_activity": max(b["timestamp"] for b in user_data["behaviors"])
                }
                
                query = text("""
                    INSERT INTO user_profiles (user_id, profile_data, created_at, updated_at)
                    VALUES (:user_id, :profile_data, :created_at, :updated_at)
                """)
                
                await session.execute(query, {
                    "user_id": user_id,
                    "profile_data": user_profile,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
                
                print(f"创建用户画像: {user_id}")
            
            await session.commit()
            print("企业级数据创建完成!")
            print(f"统计信息:")
            print(f"   - 产品数量: {len(ENTERPRISE_PRODUCTS)}")
            print(f"   - 用户数量: {len(SIMULATED_USER_BEHAVIORS)}")
            print(f"   - 行为数据: {sum(len(u['behaviors']) for u in SIMULATED_USER_BEHAVIORS)}")
            
        except Exception as e:
            await session.rollback()
            print(f"创建数据失败: {e}")
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_enterprise_data())