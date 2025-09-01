#!/usr/bin/env python3
"""
数据库迁移脚本
修复 user_behaviors 表结构，添加缺失的列
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from sqlalchemy import text
from heimdall.core.database import engine

async def run_migration():
    """执行数据库迁移"""
    print("开始执行数据库迁移...")
    
    try:
        # 读取修复脚本
        with open("sql/004_fix_database_schema.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        print("连接到数据库...")
        async with engine.begin() as conn:
            # 分割SQL语句并执行
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    print(f"执行第 {i} 条SQL语句...")
                    await conn.execute(text(statement))
                    print(f"✅ 第 {i} 条语句执行成功")
        
        print("🎉 数据库迁移完成！")
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False
    
    return True

async def verify_migration():
    """验证迁移结果"""
    print("\n验证迁移结果...")
    
    try:
        async with engine.begin() as conn:
            # 检查 user_behaviors 表的列
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user_behaviors' 
                AND column_name IN ('product_id', 'category', 'brand', 'product_name', 'price', 'timestamp')
                ORDER BY column_name;
            """))
            
            columns = result.fetchall()
            
            if columns:
                print("✅ 新增列验证成功:")
                for col in columns:
                    print(f"   - {col.column_name}: {col.data_type}")
            else:
                print("❌ 未找到新增的列")
                return False
            
            # 检查 products 表是否存在
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'products';
            """))
            
            if result.fetchone():
                print("✅ products 表存在")
            else:
                print("❌ products 表不存在")
                return False
        
        print("🎉 迁移验证完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移验证失败: {e}")
        return False

async def main():
    """主函数"""
    print("Project Heimdall - 数据库迁移工具")
    print("=" * 50)
    
    # 执行迁移
    if not await run_migration():
        print("迁移失败，请检查错误信息")
        return 1
    
    # 验证迁移
    if not await verify_migration():
        print("迁移验证失败")
        return 1
    
    print("\n🎉 数据库迁移和验证都成功完成！")
    print("现在可以重新启动服务器测试功能")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)