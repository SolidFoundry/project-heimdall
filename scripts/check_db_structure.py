#!/usr/bin/env python3
"""
检查数据库连接和表结构
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def check_database_structure():
    """检查数据库表结构"""
    try:
        # 导入必要的模块
        from sqlalchemy import create_engine, text
        from heimdall.core.config_manager import config_manager
        
        # 获取数据库配置
        config = config_manager.get_config()
        db_url = config.database_url
        
        print(f"数据库URL: {db_url.split('@')[1]}")  # 不显示密码
        
        # 创建引擎
        engine = create_engine(db_url)
        
        # 连接并检查表结构
        with engine.connect() as conn:
            # 检查 user_behaviors 表
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user_behaviors' 
                ORDER BY column_name;
            """))
            
            columns = result.fetchall()
            print(f"\nuser_behaviors 表的列 ({len(columns)} 个):")
            for col in columns:
                print(f"  - {col.column_name}: {col.data_type}")
            
            # 检查是否有必需的列
            required_columns = ['product_id', 'category', 'brand', 'product_name', 'price']
            missing_columns = []
            
            for req_col in required_columns:
                found = any(col.column_name == req_col for col in columns)
                if not found:
                    missing_columns.append(req_col)
            
            if missing_columns:
                print(f"\n❌ 缺少的列: {missing_columns}")
                return False
            else:
                print(f"\n✅ 所有必需的列都存在")
                return True
            
    except Exception as e:
        print(f"❌ 检查数据库结构失败: {e}")
        return False

def apply_fixes():
    """应用数据库修复"""
    try:
        from sqlalchemy import create_engine, text
        from heimdall.core.config_manager import config_manager
        
        # 获取数据库配置
        config = config_manager.get_config()
        db_url = config.database_url
        
        # 创建引擎
        engine = create_engine(db_url)
        
        # 读取修复脚本
        with open("sql/004_fix_database_schema.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        # 执行修复
        with engine.begin() as conn:
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    print(f"执行第 {i} 条SQL语句...")
                    try:
                        conn.execute(text(statement))
                        print(f"  第 {i} 条语句执行成功")
                    except Exception as e:
                        if "already exists" in str(e) or "duplicate column" in str(e):
                            print(f"  第 {i} 条语句已存在或已应用")
                        else:
                            print(f"  第 {i} 条语句执行失败: {e}")
        
        print("数据库修复完成")
        return True
        
    except Exception as e:
        print(f"数据库修复失败: {e}")
        return False

def main():
    """主函数"""
    print("Project Heimdall - 数据库结构检查工具")
    print("=" * 50)
    
    # 检查当前结构
    is_ok = check_database_structure()
    
    if not is_ok:
        print("\n需要应用数据库修复...")
        if apply_fixes():
            print("\n重新检查结构...")
            check_database_structure()
        else:
            print("修复失败")
            return 1
    
    print("\n检查完成")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)