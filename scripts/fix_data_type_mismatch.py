#!/usr/bin/env python3
"""
修复协同过滤查询中的数据类型不匹配问题
将 user_behaviors.product_id 从 VARCHAR(255) 改为 INTEGER 以匹配 products.id
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

def fix_product_id_data_type():
    """修复 product_id 列的数据类型"""
    print("修复 product_id 列的数据类型...")
    
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        with engine.begin() as conn:
            # 1. 检查当前 product_id 列的数据类型
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user_behaviors' 
                AND column_name = 'product_id';
            """))
            
            column_info = result.fetchone()
            if column_info:
                current_type = column_info[0]
                print(f"当前 product_id 数据类型: {current_type}")
                
                if current_type == 'integer':
                    print("product_id 已经是 INTEGER 类型，无需修复")
                    return True
                elif current_type == 'character varying' or current_type == 'varchar':
                    print("需要将 product_id 从 VARCHAR 转换为 INTEGER")
                    
                    # 2. 检查是否有非数字数据
                    result = conn.execute(text("""
                        SELECT COUNT(*) 
                        FROM user_behaviors 
                        WHERE product_id IS NOT NULL 
                        AND product_id ~ '[^0-9]';
                    """))
                    
                    invalid_count = result.fetchone()[0]
                    print(f"发现 {invalid_count} 条非数字的 product_id 记录")
                    
                    if invalid_count > 0:
                        print("清理非数字的 product_id 记录...")
                        conn.execute(text("""
                            UPDATE user_behaviors 
                            SET product_id = NULL 
                            WHERE product_id IS NOT NULL 
                            AND product_id ~ '[^0-9]';
                        """))
                        print("已清理非数字记录")
                    
                    # 3. 将 NULL 值设置为 0 或其他默认值
                    conn.execute(text("""
                        UPDATE user_behaviors 
                        SET product_id = '0' 
                        WHERE product_id IS NULL;
                    """))
                    print("已设置 NULL 值为默认值")
                    
                    # 4. 创建临时列
                    conn.execute(text("""
                        ALTER TABLE user_behaviors 
                        ADD COLUMN product_id_new INTEGER;
                    """))
                    print("已创建临时列 product_id_new")
                    
                    # 5. 转换数据
                    conn.execute(text("""
                        UPDATE user_behaviors 
                        SET product_id_new = CAST(product_id AS INTEGER);
                    """))
                    print("已转换数据到新列")
                    
                    # 6. 删除旧列
                    conn.execute(text("""
                        ALTER TABLE user_behaviors 
                        DROP COLUMN product_id;
                    """))
                    print("已删除旧列")
                    
                    # 7. 重命名新列
                    conn.execute(text("""
                        ALTER TABLE user_behaviors 
                        RENAME COLUMN product_id_new TO product_id;
                    """))
                    print("已重命名新列")
                    
                    # 8. 添加外键约束
                    conn.execute(text("""
                        ALTER TABLE user_behaviors 
                        ADD CONSTRAINT fk_user_behaviors_product 
                        FOREIGN KEY (product_id) REFERENCES products(id);
                    """))
                    print("已添加外键约束")
                    
                    print("product_id 数据类型修复完成")
                    return True
                else:
                    print(f"不支持的数据类型: {current_type}")
                    return False
            else:
                print("未找到 product_id 列")
                return False
                
    except Exception as e:
        print(f"修复 product_id 数据类型失败: {e}")
        return False

def verify_fix():
    """验证修复结果"""
    print("\n验证修复结果...")
    
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # 检查 product_id 列的数据类型
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user_behaviors' 
                AND column_name = 'product_id';
            """))
            
            column_info = result.fetchone()
            if column_info:
                data_type = column_info[0]
                print(f"product_id 数据类型: {data_type}")
                
                if data_type == 'integer':
                    print("✅ product_id 数据类型修复成功")
                    return True
                else:
                    print("❌ product_id 数据类型修复失败")
                    return False
            else:
                print("❌ 未找到 product_id 列")
                return False
                
    except Exception as e:
        print(f"验证失败: {e}")
        return False

def main():
    """主函数"""
    print("Project Heimdall - 数据类型修复工具")
    print("=" * 50)
    
    # 修复 product_id 数据类型
    if not fix_product_id_data_type():
        print("修复 product_id 数据类型失败")
        return 1
    
    # 验证修复结果
    if not verify_fix():
        print("验证修复结果失败")
        return 1
    
    print("\n🎉 数据类型修复完成！")
    print("现在可以重新启动服务器测试协同过滤功能")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)