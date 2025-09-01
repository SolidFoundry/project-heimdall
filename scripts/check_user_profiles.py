#!/usr/bin/env python3
"""
检查user_profiles表结构
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

def check_user_profiles_table():
    """检查user_profiles表结构"""
    print("检查user_profiles表结构...")
    
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_profiles'
                );
            """))
            
            table_exists = result.fetchone()[0]
            print(f"user_profiles表存在: {table_exists}")
            
            if table_exists:
                # 检查列结构
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'user_profiles' 
                    ORDER BY column_name;
                """))
                
                columns = result.fetchall()
                print(f"\nuser_profiles表的列 ({len(columns)} 个):")
                for col in columns:
                    print(f"  - {col.column_name}: {col.data_type}")
                
                # 检查是否有profile_data列
                has_profile_data = any(col.column_name == 'profile_data' for col in columns)
                print(f"\n有profile_data列: {has_profile_data}")
                
                if not has_profile_data:
                    print("需要添加profile_data列")
                
                return True
            else:
                print("user_profiles表不存在，需要创建")
                return False
                
    except Exception as e:
        print(f"检查user_profiles表失败: {e}")
        return False

def fix_user_profiles_table():
    """修复user_profiles表"""
    print("\n修复user_profiles表...")
    
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        with engine.begin() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_profiles'
                );
            """))
            
            table_exists = result.fetchone()[0]
            
            if not table_exists:
                print("创建user_profiles表...")
                conn.execute(text("""
                    CREATE TABLE user_profiles (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(100) UNIQUE NOT NULL,
                        profile_data JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                print("user_profiles表创建成功")
            else:
                # 检查现有列
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'user_profiles';
                """))
                
                existing_columns = [row[0] for row in result.fetchall()]
                print(f"现有列: {existing_columns}")
                
                # 添加缺失的列
                if 'profile_data' not in existing_columns:
                    print("添加profile_data列...")
                    conn.execute(text("""
                        ALTER TABLE user_profiles 
                        ADD COLUMN profile_data JSONB;
                    """))
                    print("profile_data列添加成功")
                
                # 添加其他可能的缺失列
                required_columns = [
                    ('age', 'INTEGER'),
                    ('gender', 'VARCHAR(20)'),
                    ('location', 'VARCHAR(100)'),
                    ('interests', 'TEXT[]'),
                    ('budget_range', 'VARCHAR(50)'),
                    ('preferred_categories', 'INTEGER[]'),
                    ('purchase_history', 'JSONB'),
                    ('browsing_history', 'JSONB')
                ]
                
                for col_name, col_type in required_columns:
                    if col_name not in existing_columns:
                        print(f"添加列: {col_name}")
                        conn.execute(text(f"""
                            ALTER TABLE user_profiles 
                            ADD COLUMN {col_name} {col_type};
                        """))
                
                print("user_profiles表修复完成")
            
            return True
            
    except Exception as e:
        print(f"修复user_profiles表失败: {e}")
        return False

def main():
    """主函数"""
    print("Project Heimdall - user_profiles表检查和修复")
    print("=" * 50)
    
    # 检查当前结构
    if not check_user_profiles_table():
        print("检查user_profiles表失败")
        return 1
    
    # 修复表结构
    if not fix_user_profiles_table():
        print("修复user_profiles表失败")
        return 1
    
    # 验证修复结果
    print("\n验证修复结果...")
    check_user_profiles_table()
    
    print("\n🎉 user_profiles表修复完成！")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)