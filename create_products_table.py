#!/usr/bin/env python3
"""
创建简化的产品表迁移脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['PYTHONPATH'] = str(project_root)

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from src.heimdall.core.config import settings

async def create_products_table():
    """创建基础的产品表"""
    
    # 创建异步引擎
    engine = create_async_engine(settings.ASYNC_DATABASE_URL)
    
    print("正在创建产品表...")
    
    # 简化的产品表创建SQL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        category_id INTEGER,
        brand VARCHAR(100),
        image_url VARCHAR(500),
        tags TEXT[],
        attributes JSONB,
        stock_quantity INTEGER DEFAULT 0,
        rating DECIMAL(3, 2) DEFAULT 0.00,
        review_count INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
    CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
    CREATE INDEX IF NOT EXISTS idx_products_tags ON products USING GIN(tags);
    """
    
    # Split SQL into individual statements
    statements = [stmt.strip() for stmt in create_table_sql.split(';') if stmt.strip()]
    
    async with engine.begin() as conn:
        for statement in statements:
            if statement:
                await conn.execute(text(statement + ';'))
    
    print("产品表创建完成！")
    
    # 插入一些示例数据
    sample_data_sql = """
    INSERT INTO products (name, description, price, category_id, brand, tags, attributes, stock_quantity, rating) VALUES
    ('iPhone 15 Pro', '苹果最新旗舰手机，搭载A17 Pro芯片', 7999.00, 1, 'Apple', ARRAY['智能手机', '5G', '拍照'], '{"color": "深空黑", "storage": "256GB", "camera": "48MP"}', 50, 4.8),
    ('MacBook Pro 14"', '专业级笔记本电脑，M3 Pro芯片', 14999.00, 1, 'Apple', ARRAY['笔记本', '办公', '开发'], '{"color": "银色", "storage": "512GB", "memory": "18GB"}', 30, 4.9),
    ('Nike Air Max 270', '经典气垫跑鞋，舒适透气', 899.00, 4, 'Nike', ARRAY['跑鞋', '运动', '气垫'], '{"color": "黑色", "size": "42", "material": "网面"}', 100, 4.6)
    ON CONFLICT DO NOTHING;
    """
    
    async with engine.begin() as conn:
        await conn.execute(text(sample_data_sql))
    
    print("示例数据插入完成！")
    
    # 关闭引擎
    await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(create_products_table())
        print("迁移成功完成")
    except Exception as e:
        print(f"迁移失败: {e}")
        sys.exit(1)