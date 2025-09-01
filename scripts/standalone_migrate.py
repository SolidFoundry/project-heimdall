#!/usr/bin/env python3
"""
独立的数据库迁移脚本
直接使用 psycopg2 连接数据库执行迁移
"""

import psycopg2
import psycopg2.extras
import os
from pathlib import Path
import sys

def load_env_file():
    """加载环境变量"""
    env_file = Path(".env")
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
    
    return env_vars

def get_database_url():
    """构建数据库连接URL"""
    env_vars = load_env_file()
    
    user = env_vars.get('DATABASE_USER', 'heimdall')
    password = env_vars.get('DATABASE_PASSWORD', 'heimdall_password')
    host = env_vars.get('DATABASE_HOST', 'localhost')
    port = env_vars.get('DATABASE_PORT', '5432')
    database = env_vars.get('DATABASE_NAME', 'heimdall_db')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

def run_migration():
    """执行数据库迁移"""
    print("开始执行数据库迁移...")
    
    try:
        # 连接到数据库
        db_url = get_database_url()
        print(f"连接到数据库: {db_url.split('@')[1]}")  # 不显示密码
        
        conn = psycopg2.connect(db_url)
        conn.autocommit = True  # 自动提交事务
        cursor = conn.cursor()
        
        # 读取修复脚本
        with open("sql/004_fix_database_schema.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        # 分割SQL语句并执行
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"执行第 {i} 条SQL语句...")
                try:
                    cursor.execute(statement)
                    print(f"✅ 第 {i} 条语句执行成功")
                except psycopg2.Error as e:
                    # 如果是"已存在"错误，可以忽略
                    if "already exists" in str(e) or "duplicate column" in str(e):
                        print(f"⚠️ 第 {i} 条语句已存在或已应用: {e}")
                    else:
                        raise e
        
        print("🎉 数据库迁移完成！")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

def verify_migration():
    """验证迁移结果"""
    print("\n验证迁移结果...")
    
    try:
        # 连接到数据库
        db_url = get_database_url()
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # 检查 user_behaviors 表的列
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_behaviors' 
            AND column_name IN ('product_id', 'category', 'brand', 'product_name', 'price', 'timestamp')
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        
        if columns:
            print("✅ 新增列验证成功:")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']}")
        else:
            print("❌ 未找到新增的列")
            return False
        
        # 检查 products 表是否存在
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'products';
        """)
        
        if cursor.fetchone():
            print("✅ products 表存在")
        else:
            print("❌ products 表不存在")
            return False
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print("🎉 迁移验证完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移验证失败: {e}")
        return False

def main():
    """主函数"""
    print("Project Heimdall - 数据库迁移工具")
    print("=" * 50)
    
    # 执行迁移
    if not run_migration():
        print("迁移失败，请检查错误信息")
        return 1
    
    # 验证迁移
    if not verify_migration():
        print("迁移验证失败")
        return 1
    
    print("\n🎉 数据库迁移和验证都成功完成！")
    print("现在可以重新启动服务器测试功能")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)