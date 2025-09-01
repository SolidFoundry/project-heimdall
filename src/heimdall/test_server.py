#!/usr/bin/env python3
"""
简单的测试服务器
用于验证数据库修复效果
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.heimdall.core.config import settings
from src.heimdall.api.endpoints import products

# 创建FastAPI应用
app = FastAPI(
    title="Project Heimdall Test Server",
    description="测试服务器 - 验证数据库修复效果",
    version="1.0.0"
)

# 包含products路由
app.include_router(products.router)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库会话
engine = create_async_engine(settings.ASYNC_DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@app.get("/")
async def root():
    return {"message": "Project Heimdall Test Server", "status": "running"}

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        async with AsyncSessionLocal() as session:
            # 测试数据库连接
            result = await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.post("/api/v1/recommendations")
async def get_recommendations(request: dict):
    """测试推荐系统API"""
    try:
        user_id = request.get("user_id", "user_001")
        session_id = request.get("session_id", "test_session")
        
        async with AsyncSessionLocal() as session:
            # 1. 获取用户画像
            result = await session.execute(
                text("SELECT profile_data FROM user_profiles WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            profile_data = result.fetchone()
            
            # 2. 获取用户行为
            result = await session.execute(
                text("""
                    SELECT DISTINCT ub.product_id, p.name, p.category, p.brand, p.price
                    FROM user_behaviors ub
                    LEFT JOIN products p ON ub.product_id = p.id
                    WHERE ub.user_id = :user_id
                    AND ub.product_id IS NOT NULL
                """),
                {"user_id": user_id}
            )
            user_behaviors = result.fetchall()
            
            # 3. 获取推荐产品
            result = await session.execute(
                text("""
                    SELECT id, name, category, brand, price, rating
                    FROM products
                    WHERE is_active = true
                    ORDER BY rating DESC
                    LIMIT 5
                """)
            )
            recommended_products = result.fetchall()
            
            # 4. 构建响应
            recommendations = []
            for product in recommended_products:
                recommendations.append({
                    "product_id": product[0],
                    "name": product[1],
                    "category": product[2],
                    "brand": product[3],
                    "price": float(product[4]),
                    "rating": float(product[5]),
                    "recommendation_reason": "基于热门产品和用户偏好"
                })
            
            return {
                "user_id": user_id,
                "session_id": session_id,
                "recommendations": recommendations,
                "user_behavior_count": len(user_behaviors),
                "has_profile": profile_data is not None,
                "status": "success"
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "user_id": user_id,
            "session_id": session_id
        }

@app.get("/api/v1/test/database")
async def test_database():
    """测试数据库连接和查询"""
    try:
        async with AsyncSessionLocal() as session:
            # 测试表结构
            tables = {}
            
            # 测试products表
            result = await session.execute(text("SELECT COUNT(*) FROM products"))
            tables["products"] = result.fetchone()[0]
            
            # 测试user_behaviors表
            result = await session.execute(text("SELECT COUNT(*) FROM user_behaviors"))
            tables["user_behaviors"] = result.fetchone()[0]
            
            # 测试user_profiles表
            result = await session.execute(text("SELECT COUNT(*) FROM user_profiles"))
            tables["user_profiles"] = result.fetchone()[0]
            
            # 测试数据类型一致性
            result = await session.execute(text("""
                SELECT 
                    (SELECT data_type FROM information_schema.columns 
                     WHERE table_name = 'products' AND column_name = 'id') as products_id_type,
                    (SELECT data_type FROM information_schema.columns 
                     WHERE table_name = 'user_behaviors' AND column_name = 'product_id') as behaviors_product_id_type;
            """))
            types = result.fetchone()
            
            return {
                "status": "success",
                "tables": tables,
                "data_types": {
                    "products.id": types[0],
                    "user_behaviors.product_id": types[1],
                    "consistent": types[0] == types[1]
                }
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    print("启动测试服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")