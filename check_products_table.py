#!/usr/bin/env python3
"""
检查products表结构
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

async def check_products_table():
    """检查products表结构"""
    
    # 创建异步引擎
    engine = create_async_engine(settings.ASYNC_DATABASE_URL)
    
    try:
        async with engine.begin() as conn:
            # 检查表是否存在
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'products'
                )
            """))
            table_exists = result.scalar()
            print(f"Products表存在: {table_exists}")
            
            if table_exists:
                # 获取表结构
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'products' 
                    ORDER BY ordinal_position
                """))
                
                print("\n表结构:")
                for row in result.fetchall():
                    print(f"  {row.column_name}: {row.data_type} (nullable: {row.is_nullable}, default: {row.column_default})")
                
                # 检查是否有数据
                result = await conn.execute(text("SELECT COUNT(*) FROM products"))
                count = result.scalar()
                print(f"\n记录数: {count}")
                
                if count > 0:
                    # 获取前几条记录
                    result = await conn.execute(text("SELECT * FROM products LIMIT 3"))
                    print("\n前3条记录:")
                    for row in result.fetchall():
                        print(f"  {row}")
            else:
                print("Products表不存在，需要创建")
    
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_products_table())