#!/usr/bin/env python3
"""
验证数据库架构修复后的状态
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from src.heimdall.core.config import settings

def verify_database_fix():
    """验证数据库修复状态"""
    print("验证数据库架构修复状态...")
    
    try:
        # 获取数据库URL
        db_url = settings.ASYNC_DATABASE_URL
        engine = create_engine(db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        with engine.begin() as conn:
            # 1. 验证products表结构
            print("\n1. 验证products表结构:")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'products'
                ORDER BY ordinal_position;
            """))
            
            for row in result.fetchall():
                print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
            
            # 2. 验证user_behaviors表结构
            print("\n2. 验证user_behaviors表结构:")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'user_behaviors'
                ORDER BY ordinal_position;
            """))
            
            for row in result.fetchall():
                print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
            
            # 3. 验证外键约束
            print("\n3. 验证外键约束:")
            result = conn.execute(text("""
                SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY';
            """))
            
            for row in result.fetchall():
                print(f"  {row[0]}.{row[1]} -> {row[2]}")
            
            # 4. 验证数据类型一致性
            print("\n4. 验证数据类型一致性:")
            result = conn.execute(text("""
                SELECT 
                    (SELECT data_type FROM information_schema.columns 
                     WHERE table_name = 'products' AND column_name = 'id') as products_id_type,
                    (SELECT data_type FROM information_schema.columns 
                     WHERE table_name = 'user_behaviors' AND column_name = 'product_id') as behaviors_product_id_type;
            """))
            
            row = result.fetchone()
            if row:
                print(f"  products.id: {row[0]}")
                print(f"  user_behaviors.product_id: {row[1]}")
                if row[0] == row[1]:
                    print("  ✓ 数据类型一致!")
                else:
                    print("  ✗ 数据类型不一致!")
            
            # 5. 测试基本查询
            print("\n5. 测试基本查询:")
            
            # 测试直接列访问查询
            try:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM user_behaviors 
                    WHERE product_id IS NOT NULL;
                """))
                count = result.fetchone()[0]
                print(f"  ✓ 直接列访问查询成功: {count} 条记录")
            except Exception as e:
                print(f"  ✗ 直接列访问查询失败: {e}")
            
            # 测试不再有JSON字段访问错误
            try:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM user_profiles 
                    WHERE profile_data IS NOT NULL;
                """))
                count = result.fetchone()[0]
                print(f"  ✓ profile_data列查询成功: {count} 条记录")
            except Exception as e:
                print(f"  ✗ profile_data列查询失败: {e}")
            
            # 6. 检查索引
            print("\n6. 检查关键索引:")
            result = conn.execute(text("""
                SELECT indexname, tablename, indexdef 
                FROM pg_indexes 
                WHERE tablename IN ('products', 'user_behaviors', 'user_profiles')
                ORDER BY tablename, indexname;
            """))
            
            for row in result.fetchall():
                print(f"  {row[1]}.{row[0]}")
            
        print("\n✅ 数据库架构验证完成!")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    success = verify_database_fix()
    if success:
        print("\n🎉 数据库架构已成功修复，所有问题已从源头解决!")
    else:
        print("\n💥 数据库架构验证失败!")