#!/usr/bin/env python3
"""
修复数据库表结构
分步骤执行，避免事务失败
"""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text

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

def create_products_table():
    """创建products表"""
    print("创建products表...")
    
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        with engine.begin() as conn:
            # 检查表是否已存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'products'
                );
            """))
            
            if result.fetchone()[0]:
                print("products表已存在，跳过创建")
                return True
            
            # 创建products表
            conn.execute(text("""
                CREATE TABLE products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(500) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    brand VARCHAR(100) NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    rating FLOAT DEFAULT 0.0,
                    description TEXT,
                    image_url VARCHAR(500),
                    stock_quantity INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            print("products表创建成功")
            return True
            
    except Exception as e:
        print(f"创建products表失败: {e}")
        return False

def fix_user_behaviors_table():
    """修复user_behaviors表"""
    print("\n修复user_behaviors表...")
    
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        with engine.begin() as conn:
            # 检查当前列
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user_behaviors';
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            print(f"现有列: {existing_columns}")
            
            # 添加缺失的列
            columns_to_add = [
                ('product_id', 'VARCHAR(255)'),
                ('category', 'VARCHAR(100)'),
                ('brand', 'VARCHAR(100)'),
                ('product_name', 'VARCHAR(500)'),
                ('price', 'DECIMAL(10, 2)'),
                ('timestamp', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    print(f"添加列: {col_name}")
                    conn.execute(text(f"""
                        ALTER TABLE user_behaviors 
                        ADD COLUMN {col_name} {col_type};
                    """))
                else:
                    print(f"列 {col_name} 已存在，跳过")
            
            print("user_behaviors表修复完成")
            return True
            
    except Exception as e:
        print(f"修复user_behaviors表失败: {e}")
        return False

def verify_fix():
    """验证修复结果"""
    print("\n验证修复结果...")
    
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # 检查products表
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'products';
            """))
            
            products_columns = [row[0] for row in result.fetchall()]
            print(f"products表列: {products_columns}")
            
            # 检查user_behaviors表
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user_behaviors';
            """))
            
            behaviors_columns = [row[0] for row in result.fetchall()]
            print(f"user_behaviors表列: {behaviors_columns}")
            
            # 检查必需的列
            required_columns = ['product_id', 'category', 'brand', 'product_name', 'price']
            missing_columns = [col for col in required_columns if col not in behaviors_columns]
            
            if missing_columns:
                print(f"仍然缺少的列: {missing_columns}")
                return False
            else:
                print("所有必需的列都已存在")
                return True
                
    except Exception as e:
        print(f"验证失败: {e}")
        return False

def main():
    """主函数"""
    print("Project Heimdall - 数据库修复工具")
    print("=" * 50)
    
    # 步骤1: 创建products表
    if not create_products_table():
        print("创建products表失败")
        return 1
    
    # 步骤2: 修复user_behaviors表
    if not fix_user_behaviors_table():
        print("修复user_behaviors表失败")
        return 1
    
    # 步骤3: 验证修复结果
    if not verify_fix():
        print("验证修复结果失败")
        return 1
    
    print("\n🎉 数据库修复完成！")
    print("现在可以重新启动服务器测试功能")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)