#!/usr/bin/env python3
"""
从头开始重新初始化数据库
确保使用统一的架构
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from src.heimdall.core.config import settings

def drop_all_tables():
    """删除所有表"""
    print("删除所有现有表...")
    
    try:
        db_url = settings.ASYNC_DATABASE_URL
        engine = create_engine(db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        with engine.begin() as conn:
            # 删除所有表
            conn.execute(text("""
                DROP TABLE IF EXISTS recommendations CASCADE;
                DROP TABLE IF EXISTS ads CASCADE;
                DROP TABLE IF EXISTS user_behaviors CASCADE;
                DROP TABLE IF EXISTS user_profiles CASCADE;
                DROP TABLE IF EXISTS products CASCADE;
                DROP TABLE IF EXISTS chat_messages CASCADE;
                DROP TABLE IF EXISTS chat_sessions CASCADE;
                DROP TABLE IF EXISTS schema_migrations CASCADE;
            """))
        
        print("所有表已删除")
        return True
        
    except Exception as e:
        print(f"删除表失败: {e}")
        return False

def apply_unified_schema():
    """应用统一架构"""
    print("应用统一数据库架构...")
    
    try:
        db_url = settings.ASYNC_DATABASE_URL
        engine = create_engine(db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        # 读取统一架构SQL
        schema_path = Path(__file__).parent.parent / "sql" / "unified_schema_v2.sql"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
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
                        continue
        
        print("统一架构应用完成")
        return True
        
    except Exception as e:
        print(f"应用统一架构失败: {e}")
        return False

def verify_initialization():
    """验证初始化结果"""
    print("验证初始化结果...")
    
    try:
        db_url = settings.ASYNC_DATABASE_URL
        engine = create_engine(db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        with engine.begin() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"存在的表: {tables}")
            
            # 检查关键表结构
            for table in ['products', 'user_behaviors', 'user_profiles']:
                result = conn.execute(text(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position;
                """))
                
                print(f"\n{table} 表结构:")
                for row in result.fetchall():
                    print(f"  {row[0]}: {row[1]}")
            
            # 检查数据类型一致性
            result = conn.execute(text("""
                SELECT 
                    (SELECT data_type FROM information_schema.columns 
                     WHERE table_name = 'products' AND column_name = 'id') as products_id_type,
                    (SELECT data_type FROM information_schema.columns 
                     WHERE table_name = 'user_behaviors' AND column_name = 'product_id') as behaviors_product_id_type;
            """))
            
            row = result.fetchone()
            if row:
                print(f"\n数据类型一致性检查:")
                print(f"  products.id: {row[0]}")
                print(f"  user_behaviors.product_id: {row[1]}")
                if row[0] == row[1]:
                    print("  数据类型一致!")
                else:
                    print("  数据类型不一致!")
        
        print("\n初始化验证完成")
        return True
        
    except Exception as e:
        print(f"验证失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 从头开始重新初始化数据库 ===")
    
    # 1. 删除所有表
    if not drop_all_tables():
        print("删除表失败，退出")
        sys.exit(1)
    
    # 2. 应用统一架构
    if not apply_unified_schema():
        print("应用统一架构失败，退出")
        sys.exit(1)
    
    # 3. 验证初始化
    if not verify_initialization():
        print("验证失败，退出")
        sys.exit(1)
    
    print("\n数据库重新初始化完成！现在可以开始测试了。")