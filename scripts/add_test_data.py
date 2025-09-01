#!/usr/bin/env python3
"""
添加测试数据用于验证系统
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from src.heimdall.core.config import settings

def add_test_data():
    """添加测试数据"""
    print("添加测试数据...")
    
    try:
        db_url = settings.ASYNC_DATABASE_URL
        engine = create_engine(db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        with engine.begin() as conn:
            # 添加测试产品
            print("添加测试产品...")
            conn.execute(text("""
                INSERT INTO products (name, description, price, category, brand, image_url, stock_quantity, rating, is_active) VALUES
                ('iPhone 15 Pro', '最新款iPhone，配备A17 Pro芯片', 7999.00, '手机', 'Apple', 'https://example.com/iphone15.jpg', 100, 4.8, true),
                ('MacBook Pro 14', 'M3 Pro芯片，专业级笔记本电脑', 14999.00, '笔记本', 'Apple', 'https://example.com/macbook.jpg', 50, 4.9, true),
                ('小米14 Ultra', '徕卡影像旗舰手机', 5999.00, '手机', '小米', 'https://example.com/xiaomi14.jpg', 200, 4.6, true),
                ('戴尔XPS 13', '轻薄便携商务笔记本', 8999.00, '笔记本', '戴尔', 'https://example.com/dellxps.jpg', 80, 4.5, true),
                ('AirPods Pro 2', '主动降噪无线耳机', 1899.00, '耳机', 'Apple', 'https://example.com/airpods.jpg', 300, 4.7, true);
            """))
            
            # 添加测试用户行为
            print("添加测试用户行为...")
            conn.execute(text("""
                INSERT INTO user_behaviors (user_id, session_id, behavior_type, product_id, category, brand, product_name, price, detected_intent, intent_confidence) VALUES
                ('user_001', 'session_001', 'view', 1, '手机', 'Apple', 'iPhone 15 Pro', 7999.00, '购买意向', 0.85),
                ('user_001', 'session_001', 'click', 1, '手机', 'Apple', 'iPhone 15 Pro', 7999.00, '购买意向', 0.90),
                ('user_001', 'session_002', 'view', 2, '笔记本', 'Apple', 'MacBook Pro 14', 14999.00, '比较研究', 0.70),
                ('user_001', 'session_002', 'view', 3, '手机', '小米', '小米14 Ultra', 5999.00, '比较研究', 0.65),
                ('user_002', 'session_003', 'view', 4, '笔记本', '戴尔', '戴尔XPS 13', 8999.00, '购买意向', 0.80),
                ('user_002', 'session_003', 'click', 4, '笔记本', '戴尔', '戴尔XPS 13', 8999.00, '购买意向', 0.85),
                ('user_002', 'session_004', 'view', 5, '耳机', 'Apple', 'AirPods Pro 2', 1899.00, '购买意向', 0.75);
            """))
            
            # 添加测试用户画像
            print("添加测试用户画像...")
            conn.execute(text("""
                INSERT INTO user_profiles (user_id, interests, budget_range, preferred_brands, behavior_score, profile_data) VALUES
                ('user_001', ARRAY['电子产品', '手机', '笔记本'], '5000-15000', ARRAY['Apple', '小米'], 0.85, '{"age": 28, "gender": "男", "location": "北京"}'),
                ('user_002', ARRAY['电子产品', '笔记本', '耳机'], '3000-10000', ARRAY['戴尔', 'Apple'], 0.78, '{"age": 32, "gender": "女", "location": "上海"}');
            """))
            
            # 添加测试广告
            print("添加测试广告...")
            conn.execute(text("""
                INSERT INTO ads (title, description, product_id, ad_type, image_url, budget, is_active) VALUES
                ('iPhone 15 Pro 限时优惠', '最新款iPhone，现在购买享受12期免息', 1, 'product', 'https://example.com/iphone_ad.jpg', 10000.00, true),
                ('MacBook Pro 教育优惠', '学生购买享受教育优惠价格', 2, 'product', 'https://example.com/macbook_ad.jpg', 5000.00, true);
            """))
            
            # 添加测试聊天会话
            print("添加测试聊天会话...")
            conn.execute(text("""
                INSERT INTO chat_sessions (session_id, system_prompt) VALUES
                ('test_session_001', '你是一个专业的广告推荐AI助手，专门分析用户行为数据并提供精准的产品推荐。'),
                ('test_session_002', '你是一个专业的广告推荐AI助手，专门分析用户行为数据并提供精准的产品推荐。');
            """))
            
            # 添加测试聊天消息
            print("添加测试聊天消息...")
            conn.execute(text("""
                INSERT INTO chat_messages (session_id, role, content) VALUES
                ('test_session_001', 'user', '我想买一部手机，预算在6000元左右'),
                ('test_session_001', 'assistant', '根据您的预算，我推荐您考虑iPhone 15 Pro或小米14 Ultra。iPhone 15 Pro配备A17 Pro芯片，性能强劲；小米14 Ultra则具有出色的徕卡影像系统。您更看重哪个方面呢？'),
                ('test_session_002', 'user', '我需要一台商务笔记本'),
                ('test_session_002', 'assistant', '对于商务用途，我推荐MacBook Pro 14或戴尔XPS 13。MacBook Pro性能强劲适合专业工作，戴尔XPS 13轻薄便携适合移动办公。您的具体需求是什么？');
            """))
        
        print("测试数据添加完成")
        return True
        
    except Exception as e:
        print(f"添加测试数据失败: {e}")
        return False

def verify_test_data():
    """验证测试数据"""
    print("验证测试数据...")
    
    try:
        db_url = settings.ASYNC_DATABASE_URL
        engine = create_engine(db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        with engine.begin() as conn:
            # 检查产品数据
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            product_count = result.fetchone()[0]
            print(f"产品数量: {product_count}")
            
            # 检查用户行为数据
            result = conn.execute(text("SELECT COUNT(*) FROM user_behaviors"))
            behavior_count = result.fetchone()[0]
            print(f"用户行为数量: {behavior_count}")
            
            # 检查用户画像数据
            result = conn.execute(text("SELECT COUNT(*) FROM user_profiles"))
            profile_count = result.fetchone()[0]
            print(f"用户画像数量: {profile_count}")
            
            # 检查广告数据
            result = conn.execute(text("SELECT COUNT(*) FROM ads"))
            ad_count = result.fetchone()[0]
            print(f"广告数量: {ad_count}")
            
            # 检查聊天会话数据
            result = conn.execute(text("SELECT COUNT(*) FROM chat_sessions"))
            session_count = result.fetchone()[0]
            print(f"聊天会话数量: {session_count}")
            
            # 检查聊天消息数据
            result = conn.execute(text("SELECT COUNT(*) FROM chat_messages"))
            message_count = result.fetchone()[0]
            print(f"聊天消息数量: {message_count}")
            
            # 验证数据类型一致性
            result = conn.execute(text("""
                SELECT 
                    (SELECT data_type FROM information_schema.columns 
                     WHERE table_name = 'products' AND column_name = 'id') as products_id_type,
                    (SELECT data_type FROM information_schema.columns 
                     WHERE table_name = 'user_behaviors' AND column_name = 'product_id') as behaviors_product_id_type;
            """))
            
            row = result.fetchone()
            if row:
                print(f"\n数据类型一致性:")
                print(f"  products.id: {row[0]}")
                print(f"  user_behaviors.product_id: {row[1]}")
                if row[0] == row[1]:
                    print("  ✓ 数据类型一致!")
                else:
                    print("  ✗ 数据类型不一致!")
            
            # 测试查询
            print("\n测试查询:")
            result = conn.execute(text("""
                SELECT ub.user_id, ub.product_id, p.name as product_name, ub.behavior_type
                FROM user_behaviors ub
                LEFT JOIN products p ON ub.product_id = p.id
                WHERE ub.user_id = 'user_001'
                LIMIT 5;
            """))
            
            for row in result.fetchall():
                print(f"  {row[0]} 查看了产品 {row[1]} ({row[2]}) - {row[3]}")
        
        print("\n测试数据验证完成")
        return True
        
    except Exception as e:
        print(f"验证测试数据失败: {e}")
        return False

if __name__ == "__main__":
    if add_test_data():
        if verify_test_data():
            print("\n测试数据准备完成！可以开始API测试了。")
        else:
            print("\n测试数据验证失败")
            sys.exit(1)
    else:
        print("\n测试数据添加失败")
        sys.exit(1)