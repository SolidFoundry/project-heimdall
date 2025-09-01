#!/usr/bin/env python3
"""
运行数据库迁移脚本
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
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.heimdall.core.config import settings

async def run_migration():
    """运行002产品广告数据表迁移"""
    
    # 创建异步引擎
    engine = create_async_engine(settings.ASYNC_DATABASE_URL)
    
    # 读取迁移文件
    migration_file = project_root / "sql" / "002_product_ads_schema.sql"
    
    print(f"正在读取迁移文件: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print("正在执行迁移...")
    
    # Split SQL into individual statements
    statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
    
    async with engine.begin() as conn:
        for i, statement in enumerate(statements):
            if statement:  # Skip empty statements
                print(f"执行语句 {i+1}/{len(statements)}")
                await conn.execute(text(statement + ';'))
    
    print("迁移执行完成！")
    
    # 关闭引擎
    await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(run_migration())
        print("✅ 迁移成功完成")
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        sys.exit(1)