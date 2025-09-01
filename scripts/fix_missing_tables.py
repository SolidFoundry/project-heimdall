#!/usr/bin/env python3
"""
检查数据库状态并修复缺失的表
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from src.heimdall.core.config import settings

def check_database_status():
    """检查数据库状态"""
    print("检查数据库状态...")
    
    try:
        db_url = settings.ASYNC_DATABASE_URL
        engine = create_engine(db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        with engine.begin() as conn:
            # 检查所有表
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"当前存在的表: {tables}")
            
            # 检查缺失的关键表
            required_tables = ['products', 'user_behaviors', 'user_profiles', 'recommendations', 'ads', 'chat_sessions', 'chat_messages']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"缺失的表: {missing_tables}")
                return False
            else:
                print("所有必需的表都存在")
                return True
                
    except Exception as e:
        print(f"检查数据库状态失败: {e}")
        return False

def create_missing_tables():
    """创建缺失的表"""
    print("创建缺失的表...")
    
    try:
        db_url = settings.ASYNC_DATABASE_URL
        engine = create_engine(db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        with engine.begin() as conn:
            # 创建products表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(500) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    brand VARCHAR(100) NOT NULL,
                    image_url VARCHAR(500),
                    tags TEXT[],
                    attributes JSONB,
                    stock_quantity INTEGER DEFAULT 0,
                    rating DECIMAL(3, 2) DEFAULT 0.00,
                    review_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # 创建user_behaviors表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_behaviors (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_id VARCHAR(255) NOT NULL,
                    behavior_type VARCHAR(50) NOT NULL,
                    product_id INTEGER,
                    category VARCHAR(100),
                    brand VARCHAR(100),
                    product_name VARCHAR(500),
                    price DECIMAL(10, 2),
                    behavior_data JSONB DEFAULT '{}'::jsonb,
                    detected_intent VARCHAR(100),
                    intent_confidence DECIMAL(3, 2) DEFAULT 0.0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
                );
            """))
            
            # 创建user_profiles表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(100) UNIQUE NOT NULL,
                    age INTEGER,
                    gender VARCHAR(20),
                    location VARCHAR(100),
                    interests TEXT[],
                    budget_range VARCHAR(50),
                    preferred_categories INTEGER[],
                    preferred_brands TEXT[],
                    purchase_history JSONB,
                    browsing_history JSONB,
                    behavior_score FLOAT DEFAULT 0.0,
                    profile_data JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # 创建recommendations表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(100) NOT NULL,
                    session_id VARCHAR(100),
                    recommendation_type VARCHAR(50) NOT NULL,
                    product_ids INTEGER[],
                    ad_ids INTEGER[],
                    scores JSONB,
                    context JSONB,
                    is_clicked BOOLEAN DEFAULT false,
                    is_purchased BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # 创建ads表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ads (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    product_id INTEGER REFERENCES products(id),
                    ad_type VARCHAR(50) NOT NULL,
                    image_url VARCHAR(500),
                    target_audience TEXT,
                    budget DECIMAL(12, 2) DEFAULT 0.00,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # 创建chat_sessions表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    system_prompt TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # 创建chat_messages表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
                );
            """))
        
        print("所有缺失的表已创建")
        return True
        
    except Exception as e:
        print(f"创建缺失表失败: {e}")
        return False

if __name__ == "__main__":
    if not check_database_status():
        print("需要创建缺失的表...")
        if create_missing_tables():
            print("表创建完成，重新检查状态...")
            check_database_status()
        else:
            print("创建表失败")
            sys.exit(1)
    else:
        print("数据库状态正常")