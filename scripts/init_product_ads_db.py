#!/usr/bin/env python3
"""
数据库初始化脚本 - 创建产品和广告相关表
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from heimdall.core.config import settings

async def init_database():
    """初始化数据库，创建产品和广告相关表"""
    
    # 创建异步引擎
    engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=True,
        future=True
    )
    
    # 创建异步会话工厂
    async_session = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    # 读取SQL文件
    sql_file = Path(__file__).parent.parent / 'sql' / '002_product_ads_schema.sql'
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("开始创建产品和广告数据表...")
        
        async with async_session() as session:
            # 分割SQL语句并逐个执行
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        await session.execute(text(statement))
                        await session.commit()
                    except Exception as e:
                        print(f"执行语句时出错: {e}")
                        print(f"语句: {statement[:100]}...")
                        # 回滚并继续下一个语句
                        await session.rollback()
                        continue
            
        print("数据库表创建成功！")
        print("创建的表包括：")
        print("   - product_categories (产品类别)")
        print("   - products (产品)")
        print("   - ads (广告)")
        print("   - user_profiles (用户画像)")
        print("   - recommendations (推荐记录)")
        print("   - ab_tests (A/B测试)")
        print("   - user_behaviors (用户行为，已扩展)")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())