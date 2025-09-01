#!/usr/bin/env python3
"""
简单的products API服务器
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from src.heimdall.core.config import settings

# 创建FastAPI应用
app = FastAPI(
    title="Products API Server",
    description="简单的Products API服务器",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic模型
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category: str
    brand: str
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    attributes: Optional[dict] = None
    stock_quantity: int
    rating: float
    review_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total_count: int
    page: int
    size: int

# 创建数据库会话
engine = create_async_engine(settings.ASYNC_DATABASE_URL)

@app.get("/")
async def root():
    return {"message": "Products API Server", "status": "running"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "Products API is running"}

@app.get("/api/v1/products", response_model=ProductListResponse)
async def get_products(
    page: int = 1,
    size: int = 10,
    category: Optional[str] = None,
    brand: Optional[str] = None
):
    """获取产品列表"""
    try:
        async with engine.begin() as conn:
            # 构建查询条件
            where_conditions = []
            params = {}
            
            if category:
                where_conditions.append("category = :category")
                params["category"] = category
            
            if brand:
                where_conditions.append("brand = :brand")
                params["brand"] = brand
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # 获取总数
            count_query = text(f"SELECT COUNT(*) FROM products WHERE {where_clause}")
            count_result = await conn.execute(count_query, params)
            total_count = count_result.scalar()
            
            # 获取分页数据
            offset = (page - 1) * size
            data_query = text(f"""
                SELECT id, name, description, price, category, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active, created_at, updated_at
                FROM products 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT :size OFFSET :offset
            """)
            
            params["size"] = size
            params["offset"] = offset
            
            result = await conn.execute(data_query, params)
            products = [ProductResponse(**dict(row._mapping)) for row in result.fetchall()]
            
            return ProductListResponse(
                products=products,
                total_count=total_count,
                page=page,
                size=size
            )
            
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/v1/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """获取单个产品详情"""
    try:
        async with engine.begin() as conn:
            query = text("""
                SELECT id, name, description, price, category, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active, created_at, updated_at
                FROM products 
                WHERE id = :product_id AND is_active = true
            """)
            
            result = await conn.execute(query, {"product_id": product_id})
            product = result.fetchone()
            
            if not product:
                return {"error": "产品不存在", "status": "error"}
            
            return ProductResponse(**dict(product._mapping))
            
    except Exception as e:
        return {"error": str(e), "status": "error"}

if __name__ == "__main__":
    print("启动Products API服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")