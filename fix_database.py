#!/usr/bin/env python3
"""
数据库修复脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def fix_database():
    # 使用环境变量或默认配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://heimdall:your_secure_database_password_here@localhost:5432/heimdall_db')
    
    print(f"连接数据库: {DATABASE_URL}")
    
    try:
        engine = create_async_engine(DATABASE_URL)
        
        async with engine.begin() as conn:
            # 检查并修复products表
            print("检查products表...")
            
            # 检查products表是否存在
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'products'
                )
            """))
            products_exists = result.scalar()
            
            if not products_exists:
                print("创建products表...")
                await conn.execute(text("""
                    CREATE TABLE products (
                        id SERIAL PRIMARY KEY,
                        product_id VARCHAR(255) UNIQUE NOT NULL,
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
                    )
                """))
                print("✅ products表创建成功")
            else:
                print("✅ products表已存在")
            
            # 检查并修复user_behaviors表
            print("检查user_behaviors表...")
            
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_behaviors'
                )
            """))
            behaviors_exists = result.scalar()
            
            if not behaviors_exists:
                print("创建user_behaviors表...")
                await conn.execute(text("""
                    CREATE TABLE user_behaviors (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        session_id VARCHAR(255) NOT NULL,
                        behavior_type VARCHAR(50) NOT NULL,
                        behavior_data JSONB NOT NULL,
                        product_id VARCHAR(255),
                        category VARCHAR(100),
                        brand VARCHAR(100),
                        product_name VARCHAR(500),
                        price DECIMAL(10, 2),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("✅ user_behaviors表创建成功")
            else:
                print("✅ user_behaviors表已存在")
                
                # 检查是否需要添加缺失的列
                result = await conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'user_behaviors'
                """))
                existing_columns = [row[0] for row in result]
                
                missing_columns = []
                required_columns = ['product_id', 'category', 'brand', 'product_name', 'price', 'timestamp']
                
                for col in required_columns:
                    if col not in existing_columns:
                        missing_columns.append(col)
                
                if missing_columns:
                    print(f"添加缺失的列: {missing_columns}")
                    for col in missing_columns:
                        if col == 'product_id':
                            await conn.execute(text("ALTER TABLE user_behaviors ADD COLUMN product_id VARCHAR(255)"))
                        elif col == 'category':
                            await conn.execute(text("ALTER TABLE user_behaviors ADD COLUMN category VARCHAR(100)"))
                        elif col == 'brand':
                            await conn.execute(text("ALTER TABLE user_behaviors ADD COLUMN brand VARCHAR(100)"))
                        elif col == 'product_name':
                            await conn.execute(text("ALTER TABLE user_behaviors ADD COLUMN product_name VARCHAR(500)"))
                        elif col == 'price':
                            await conn.execute(text("ALTER TABLE user_behaviors ADD COLUMN price DECIMAL(10, 2)"))
                        elif col == 'timestamp':
                            await conn.execute(text("ALTER TABLE user_behaviors ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                    
                    print("✅ 缺失的列已添加")
            
            # 插入示例数据
            print("检查示例数据...")
            result = await conn.execute(text("SELECT COUNT(*) FROM products"))
            product_count = result.scalar()
            
            if product_count == 0:
                print("插入示例产品数据...")
                await conn.execute(text("""
                    INSERT INTO products (product_id, name, category, brand, price, rating, description, image_url, stock_quantity) VALUES
                    ('laptop_001', 'ThinkPad X1 Carbon', '笔记本电脑', '联想', 8999.00, 4.8, '轻薄商务笔记本，搭载Intel i7处理器，16GB内存，512GB固态硬盘', '/images/laptop_001.jpg', 50),
                    ('laptop_002', 'MacBook Air M2', '笔记本电脑', '苹果', 7999.00, 4.9, '全新M2芯片，13.6英寸Liquid Retina显示屏，18小时电池续航', '/images/laptop_002.jpg', 30),
                    ('phone_001', 'iPhone 15 Pro', '智能手机', '苹果', 7999.00, 4.9, 'A17 Pro芯片，48MP主摄，钛金属设计，支持Action Button', '/images/phone_001.jpg', 100),
                    ('phone_002', '华为Mate 60 Pro', '智能手机', '华为', 6999.00, 4.7, '麒麟9000S芯片，50MP三摄，卫星通话，昆仑玻璃', '/images/phone_002.jpg', 80)
                """))
                print("✅ 示例产品数据已插入")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM user_behaviors"))
            behavior_count = result.scalar()
            
            if behavior_count == 0:
                print("插入示例用户行为数据...")
                await conn.execute(text("""
                    INSERT INTO user_behaviors (user_id, session_id, behavior_type, behavior_data, product_id, category, brand, product_name, price) VALUES
                    ('user_001', 'session_001', 'view', '{"action": "view", "duration": 45}', 'laptop_001', '笔记本电脑', '联想', 'ThinkPad X1 Carbon', 8999.00),
                    ('user_001', 'session_001', 'click', '{"action": "click", "element": "specs"}', 'laptop_001', '笔记本电脑', '联想', 'ThinkPad X1 Carbon', 8999.00),
                    ('user_002', 'session_002', 'view', '{"action": "view", "duration": 67}', 'phone_001', '智能手机', '苹果', 'iPhone 15 Pro', 7999.00),
                    ('user_002', 'session_002', 'purchase', '{"action": "purchase", "quantity": 1}', 'phone_001', '智能手机', '苹果', 'iPhone 15 Pro', 7999.00)
                """))
                print("✅ 示例用户行为数据已插入")
        
        await engine.dispose()
        print("✅ 数据库修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库修复失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_database())
    sys.exit(0 if success else 1)
