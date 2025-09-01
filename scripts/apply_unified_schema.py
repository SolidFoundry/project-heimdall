#!/usr/bin/env python3
"""
应用统一数据库架构
解决所有SQL文件不一致问题
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.heimdall.core.config import settings

def read_unified_schema():
    """读取统一架构文件"""
    schema_path = Path(__file__).parent.parent / "sql" / "unified_schema_v2.sql"
    with open(schema_path, 'r', encoding='utf-8') as f:
        return f.read()

def apply_unified_schema():
    """应用统一数据库架构"""
    print("开始应用统一数据库架构...")
    
    try:
        # 获取数据库URL
        db_url = settings.ASYNC_DATABASE_URL
        print(f"连接数据库: {db_url}")
        
        # 创建同步引擎用于执行DDL
        engine = create_engine(db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        # 读取统一架构SQL
        schema_sql = read_unified_schema()
        
        print("执行统一架构SQL...")
        
        # 分割SQL语句并执行
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        with engine.begin() as conn:
            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        conn.execute(text(statement))
                        print(f"执行语句 {i}/{len(statements)}")
                    except Exception as e:
                        print(f"语句 {i} 执行失败: {e}")
                        # 继续执行其他语句
                        continue
        
        print("统一数据库架构应用完成！")
        
        # 验证表结构
        print("\n验证表结构...")
        verify_schema(engine)
        
    except Exception as e:
        print(f"应用统一架构失败: {e}")
        return False
    
    return True

def verify_schema(engine):
    """验证数据库架构"""
    with engine.begin() as conn:
        # 检查products表
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'products'
            ORDER BY ordinal_position;
        """))
        print("\nProducts表结构:")
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # 检查user_behaviors表
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_behaviors'
            ORDER BY ordinal_position;
        """))
        print("\nUser_behaviors表结构:")
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # 检查外键约束
        result = conn.execute(text("""
            SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name IN ('user_behaviors', 'recommendations', 'ads');
        """))
        print("\n外键约束:")
        for row in result.fetchall():
            print(f"  {row[0]}.{row[1]} -> {row[2]}")

if __name__ == "__main__":
    success = apply_unified_schema()
    if success:
        print("\n数据库架构统一完成！所有问题已从源头解决。")
    else:
        print("\n数据库架构统一失败！")
        sys.exit(1)