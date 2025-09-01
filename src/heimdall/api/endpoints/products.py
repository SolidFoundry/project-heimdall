"""
产品管理API端点
提供产品CRUD操作和查询功能
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
import logging

from src.heimdall.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["产品管理"])

# Pydantic模型
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    attributes: Optional[dict] = None
    stock_quantity: int = 0
    rating: float = 0.0
    review_count: int = 0
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    attributes: Optional[dict] = None
    stock_quantity: Optional[int] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total_count: int
    page: int
    size: int

# 产品CRUD操作
@router.post("/products", response_model=ProductResponse, summary="创建产品")
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新产品"""
    try:
        # 记录请求数据用于调试
        logger.info(f"创建产品请求数据: {product.dict()}")
        
        # 构建插入语句
        query = text("""
            INSERT INTO products (name, description, price, category, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active)
            VALUES (:name, :description, :price, :category, :brand, :image_url, :tags, :attributes, :stock_quantity, :rating, :review_count, :is_active)
            RETURNING id, name, description, price, category, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active, created_at, updated_at
        """)
        
        result = await db.execute(query, {
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "category": product.category,
            "brand": product.brand,
            "image_url": product.image_url,
            "tags": product.tags,
            "attributes": product.attributes,
            "stock_quantity": product.stock_quantity,
            "rating": product.rating,
            "review_count": product.review_count,
            "is_active": product.is_active
        })
        
        await db.commit()
        
        product_data = result.fetchone()
        return ProductResponse(**dict(product_data._mapping))
        
    except Exception as e:
        await db.rollback()
        logger.error(f"创建产品失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建产品失败: {str(e)}")

@router.get("/products/test", summary="测试产品接口")
async def test_products():
    """测试产品接口"""
    return {"message": "Products API is working", "status": "ok"}

@router.get("/products", response_model=ProductListResponse, summary="获取产品列表")
async def get_products(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    category: Optional[str] = Query(None, description="类别过滤"),
    brand: Optional[str] = Query(None, description="品牌过滤"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """获取产品列表，支持分页和过滤"""
    try:
        # 构建查询条件
        where_conditions = []
        params = {}
        
        if category:
            where_conditions.append("category = :category")
            params["category"] = category
        
        if brand:
            where_conditions.append("brand = :brand")
            params["brand"] = brand
        
        if min_price is not None:
            where_conditions.append("price >= :min_price")
            params["min_price"] = min_price
        
        if max_price is not None:
            where_conditions.append("price <= :max_price")
            params["max_price"] = max_price
        
        if search:
            where_conditions.append("(name ILIKE :search OR description ILIKE :search)")
            params["search"] = f"%{search}%"
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 获取总数
        count_query = text(f"SELECT COUNT(*) FROM products WHERE {where_clause}")
        count_result = await db.execute(count_query, params)
        total_count = count_result.scalar()
        
        # 获取分页数据
        offset = (page - 1) * size
        # Force cache invalidation with different query structure
        data_query = text(f"""
            SELECT id, name, description, price, category, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active, created_at, updated_at
            FROM products 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :size OFFSET :offset
        """)
        
        params["size"] = size
        params["offset"] = offset
        
        result = await db.execute(data_query, params)
        rows = result.fetchall()
        
        # 调试：打印原始数据
        logger.info(f"Raw data from database: {rows}")
        
        products = []
        for row in rows:
            try:
                row_dict = dict(row._mapping)
                logger.info(f"Processing row: {row_dict}")
                product = ProductResponse(**row_dict)
                products.append(product)
            except Exception as e:
                logger.error(f"Error processing row {row_dict}: {e}")
                raise
        
        return ProductListResponse(
            products=products,
            total_count=total_count,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"获取产品列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取产品列表失败: {str(e)}")

@router.get("/products/{product_id}", response_model=ProductResponse, summary="获取产品详情")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个产品详情"""
    try:
        query = text("""
            SELECT id, name, description, price, category, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active, created_at, updated_at
            FROM products 
            WHERE id = :product_id AND is_active = true
        """)
        
        result = await db.execute(query, {"product_id": product_id})
        product = result.fetchone()
        
        if not product:
            raise HTTPException(status_code=404, detail="产品不存在")
        
        # 提交事务以确保读取操作完成
        await db.commit()
        
        return ProductResponse(**dict(product._mapping))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取产品详情失败: {str(e)}")

@router.put("/products/{product_id}", response_model=ProductResponse, summary="更新产品")
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新产品信息"""
    try:
        # 检查产品是否存在
        check_query = text("SELECT id FROM products WHERE id = :product_id")
        result = await db.execute(check_query, {"product_id": product_id})
        
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="产品不存在")
        
        # 构建更新语句
        update_fields = []
        params = {"product_id": product_id}
        
        for field, value in product_update.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = :{field}")
                params[field] = value
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供更新字段")
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        query = text(f"""
            UPDATE products 
            SET {', '.join(update_fields)}
            WHERE id = :product_id
            RETURNING id, name, description, price, category, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active, created_at, updated_at
        """)
        
        result = await db.execute(query, params)
        await db.commit()
        
        updated_product = result.fetchone()
        return ProductResponse(**dict(updated_product._mapping))
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新产品失败: {str(e)}")

@router.delete("/products/{product_id}", summary="删除产品")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除产品（软删除）"""
    try:
        query = text("UPDATE products SET is_active = false, updated_at = CURRENT_TIMESTAMP WHERE id = :product_id")
        result = await db.execute(query, {"product_id": product_id})
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="产品不存在")
        
        await db.commit()
        
        return {"message": "产品删除成功", "product_id": product_id}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除产品失败: {str(e)}")

@router.get("/categories", summary="获取产品类别")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取所有产品类别"""
    try:
        query = text("SELECT id, name, description, parent_id FROM product_categories ORDER BY id")
        result = await db.execute(query)
        
        categories = []
        for row in result.fetchall():
            categories.append({
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "parent_id": row.parent_id
            })
        
        return {"categories": categories, "total_count": len(categories)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取类别列表失败: {str(e)}")

@router.get("/products/search", summary="搜索产品")
async def search_products(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="返回结果数量"),
    db: AsyncSession = Depends(get_db)
):
    """搜索产品"""
    try:
        query = text("""
            SELECT id, name, description, price, category, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active, created_at, updated_at
            FROM products 
            WHERE is_active = true 
            AND (name ILIKE :search OR description ILIKE :search OR brand ILIKE :search)
            ORDER BY 
                CASE 
                    WHEN name ILIKE :exact_match THEN 1
                    WHEN name ILIKE :starts_with THEN 2
                    ELSE 3
                END,
                rating DESC,
                created_at DESC
            LIMIT :limit
        """)
        
        search_term = f"%{q}%"
        params = {
            "search": search_term,
            "exact_match": q,
            "starts_with": f"{q}%",
            "limit": limit
        }
        
        result = await db.execute(query, params)
        products = [ProductResponse(**dict(row._mapping)) for row in result.fetchall()]
        
        return {
            "products": products,
            "total_count": len(products),
            "search_query": q
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索产品失败: {str(e)}")

@router.get("/products/{product_id}/recommendations", summary="获取相关产品推荐")
async def get_product_recommendations(
    product_id: int,
    limit: int = Query(5, ge=1, le=20, description="推荐数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取相关产品推荐"""
    try:
        # 首先获取产品信息
        product_query = text("SELECT category, brand, tags FROM products WHERE id = :product_id AND is_active = true")
        product_result = await db.execute(product_query, {"product_id": product_id})
        product = product_result.fetchone()
        
        if not product:
            raise HTTPException(status_code=404, detail="产品不存在")
        
        # 获取相关产品
        query = text("""
            SELECT id, name, description, price, category, brand, image_url, tags, attributes, stock_quantity, rating, review_count, is_active, created_at, updated_at
            FROM products 
            WHERE id != :product_id 
            AND is_active = true 
            AND (category = :category OR brand = :brand)
            ORDER BY rating DESC, review_count DESC
            LIMIT :limit
        """)
        
        params = {
            "product_id": product_id,
            "category": product.category,
            "brand": product.brand,
            "limit": limit
        }
        
        result = await db.execute(query, params)
        recommendations = [ProductResponse(**dict(row._mapping)) for row in result.fetchall()]
        
        return {
            "product_id": product_id,
            "recommendations": recommendations,
            "total_count": len(recommendations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取产品推荐失败: {str(e)}")