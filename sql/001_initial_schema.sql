-- Project Heimdall Complete Database Schema
-- Version: 1.0.0
-- Description: Complete database schema for Project Heimdall including all tables

BEGIN;

-- ===================================================================
-- 0. Schema Migrations Table (for tracking applied migrations)
-- ===================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert this migration record
INSERT INTO schema_migrations (version, description) 
VALUES ('001', 'Complete database schema for Project Heimdall')
ON CONFLICT (version) DO NOTHING;

-- ===================================================================
-- 1. Chat Sessions Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    system_prompt TEXT,
    user_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster session lookup
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);

-- ===================================================================
-- 2. Chat Messages Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created ON chat_messages(session_id, created_at DESC);

-- ===================================================================
-- 3. User Profiles Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    email VARCHAR(255),
    age INTEGER,
    gender VARCHAR(20),
    location VARCHAR(255),
    interests TEXT[],
    membership_level VARCHAR(50) DEFAULT 'standard',
    activity_level INTEGER DEFAULT 0,
    price_range_min DECIMAL(10,2) DEFAULT 0,
    price_range_max DECIMAL(10,2) DEFAULT 0,
    preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_membership_level ON user_profiles(membership_level);
CREATE INDEX IF NOT EXISTS idx_user_profiles_activity_level ON user_profiles(activity_level);

-- ===================================================================
-- 4. User Behaviors Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS user_behaviors (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    behavior_type VARCHAR(50) NOT NULL,
    behavior_data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_behaviors_user_id ON user_behaviors(user_id);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_session_id ON user_behaviors(session_id);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_behavior_type ON user_behaviors(behavior_type);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_timestamp ON user_behaviors(timestamp);

-- ===================================================================
-- 5. Product Categories Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS product_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES product_categories(id) ON DELETE SET NULL,
    attributes JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_product_categories_name ON product_categories(name);
CREATE INDEX IF NOT EXISTS idx_product_categories_parent_id ON product_categories(parent_id);

-- ===================================================================
-- 6. Products Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(255),
    category_id INTEGER REFERENCES product_categories(id),
    brand VARCHAR(255),
    image_url VARCHAR(500),
    attributes JSONB,
    tags TEXT[],
    rating DECIMAL(3,2) DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

-- ===================================================================
-- 7. Ads Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS ads (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    target_url VARCHAR(500),
    category VARCHAR(255),
    budget DECIMAL(10,2) DEFAULT 0,
    daily_budget DECIMAL(10,2) DEFAULT 0,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    targeting JSONB,
    attributes JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ads_title ON ads(title);
CREATE INDEX IF NOT EXISTS idx_ads_category ON ads(category);
CREATE INDEX IF NOT EXISTS idx_ads_is_active ON ads(is_active);
CREATE INDEX IF NOT EXISTS idx_ads_dates ON ads(start_date, end_date);

-- ===================================================================
-- 8. Intent Analyses Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS intent_analyses (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    input_text TEXT NOT NULL,
    intent_type VARCHAR(100),
    confidence_score DECIMAL(5,4),
    entities JSONB,
    analysis_result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_intent_analyses_user_id ON intent_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_intent_analyses_session_id ON intent_analyses(session_id);
CREATE INDEX IF NOT EXISTS idx_intent_analyses_intent_type ON intent_analyses(intent_type);
CREATE INDEX IF NOT EXISTS idx_intent_analyses_created_at ON intent_analyses(created_at);

-- ===================================================================
-- 9. Recommendations Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    recommendation_type VARCHAR(50),
    recommended_items JSONB,
    scores JSONB,
    algorithm_used VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_session_id ON recommendations(session_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_type ON recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_at ON recommendations(created_at);

-- ===================================================================
-- 10. Ad Recommendations Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS ad_recommendations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    ad_id INTEGER REFERENCES ads(id) ON DELETE CASCADE,
    score DECIMAL(5,4),
    reason TEXT,
    context JSONB,
    shown BOOLEAN DEFAULT false,
    clicked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ad_recommendations_user_id ON ad_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_ad_recommendations_session_id ON ad_recommendations(session_id);
CREATE INDEX IF NOT EXISTS idx_ad_recommendations_ad_id ON ad_recommendations(ad_id);
CREATE INDEX IF NOT EXISTS idx_ad_recommendations_score ON ad_recommendations(score);

-- ===================================================================
-- 11. User Sessions Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_type VARCHAR(50),
    location VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity);

-- ===================================================================
-- 12. AB Tests Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS ab_tests (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(255) NOT NULL,
    variant VARCHAR(100) NOT NULL,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ab_tests_test_name ON ab_tests(test_name);
CREATE INDEX IF NOT EXISTS idx_ab_tests_variant ON ab_tests(variant);
CREATE INDEX IF NOT EXISTS idx_ab_tests_user_id ON ab_tests(user_id);

-- ===================================================================
-- 13. Updated At Trigger Function
-- ===================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables with updated_at column
CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON chat_sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_categories_updated_at 
    BEFORE UPDATE ON product_categories 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at 
    BEFORE UPDATE ON products 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ads_updated_at 
    BEFORE UPDATE ON ads 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- 14. Sample Data for Testing
-- ===================================================================

-- Insert sample product categories
INSERT INTO product_categories (name, description) VALUES
('电子产品', '包括手机、电脑、平板等电子设备'),
('服装', '男装、女装、童装等各类服装'),
('家居', '家具、家饰、家居用品'),
('运动户外', '运动器材、户外装备'),
('美妆护肤', '化妆品、护肤品'),
('食品饮料', '各类食品和饮料'),
('图书音像', '图书、音乐、影视'),
('母婴用品', '孕妇用品、婴儿用品');

-- Insert sample products
INSERT INTO products (name, description, price, category, brand, image_url, tags, rating, review_count, stock_quantity) VALUES
('iPhone 15 Pro', '苹果最新旗舰手机，配备A17 Pro芯片', 7999.00, '电子产品', 'Apple', '/images/iphone15pro.jpg', ARRAY['手机', '苹果', '5G'], 4.8, 1250, 100),
('MacBook Air M2', '轻薄便携笔记本电脑，M2芯片强劲性能', 8999.00, '电子产品', 'Apple', '/images/macbookair.jpg', ARRAY['笔记本', '苹果', 'M2'], 4.9, 890, 50),
('Nike Air Max 270', '经典气垫跑鞋，舒适透气', 899.00, '运动户外', 'Nike', '/images/airmax270.jpg', ARRAY['运动鞋', '跑步', '气垫'], 4.6, 567, 200),
('戴森V15吸尘器', '无线吸尘器，强劲吸力', 3990.00, '家居', 'Dyson', '/images/dysonv15.jpg', ARRAY['吸尘器', '无线', '清洁'], 4.7, 432, 30),
('雅诗兰黛小棕瓶', '经典抗老精华', 780.00, '美妆护肤', 'Estée Lauder', '/images/brownbottle.jpg', ARRAY['精华', '抗老', '护肤品'], 4.5, 234, 150),
('小米13 Ultra', '徕卡影像旗舰手机', 5999.00, '电子产品', 'Xiaomi', '/images/mi13ultra.jpg', ARRAY['手机', '小米', '徕卡'], 4.7, 891, 80),
('阿迪达斯Ultraboost 22', '能量回弹跑鞋', 1299.00, '运动户外', 'Adidas', '/images/ultraboost.jpg', ARRAY['跑鞋', '运动', '回弹'], 4.5, 445, 120),
('SK-II神仙水', '经典护肤精华', 1540.00, '美妆护肤', 'SK-II', '/images/skii.jpg', ARRAY['精华', '护肤', 'PITERA'], 4.8, 678, 90);

-- Insert sample user profiles
INSERT INTO user_profiles (user_id, username, email, age, gender, location, interests, membership_level, activity_level, price_range_min, price_range_max, preferences) VALUES
('user_english_test', 'John Doe', 'john@example.com', 28, 'male', 'New York', ARRAY['电子产品', '运动'], 'premium', 15, 1000.00, 10000.00, '{"brands": ["Apple", "Nike"], "colors": ["black", "white"]}'),
('user_test_profile', '测试用户', 'test@example.com', 25, 'female', '北京', ARRAY['美妆护肤', '服装'], 'standard', 8, 100.00, 2000.00, '{"brands": ["雅诗兰黛"], "skin_type": "dry"}');

-- Insert sample user behaviors
INSERT INTO user_behaviors (user_id, session_id, behavior_type, behavior_data) VALUES
('user_english_test', 'session_001', 'search', '{"query": "iPhone 15 Pro", "category": "电子产品"}'),
('user_english_test', 'session_001', 'view', '{"product_id": 1, "duration": 120}'),
('user_english_test', 'session_001', 'click', '{"ad_id": 1, "position": 1}'),
('user_test_profile', 'session_002', 'search', '{"query": "雅诗兰黛小棕瓶", "category": "美妆护肤"}'),
('user_test_profile', 'session_002', 'view', '{"product_id": 5, "duration": 180}');

-- Insert sample ads
INSERT INTO ads (title, description, image_url, target_url, category, budget, daily_budget, start_date, targeting, is_active) VALUES
('iPhone 15 Pro 限时优惠', '最新款iPhone，立减500元', '/images/iphone15pro_ad.jpg', '/products/1', '电子产品', 10000.00, 1000.00, NOW() - INTERVAL '30 days', '{"age_range": [25, 45], "gender": ["male", "female"]}', true),
('双11购物狂欢节', '全场商品5折起', '/images/double11.jpg', '/promotions/double11', 'all', 50000.00, 5000.00, NOW() - INTERVAL '15 days', '{"all_users": true}', true),
('小米13 Ultra 新品发布', '徕卡影像，旗舰体验', '/images/mi13ultra_ad.jpg', '/products/6', '电子产品', 8000.00, 800.00, NOW() - INTERVAL '7 days', '{"age_range": [20, 35], "interests": ["电子产品"]}', true);

-- Insert sample intent analyses
INSERT INTO intent_analyses (user_id, session_id, input_text, intent_type, confidence_score, entities, analysis_result) VALUES
('user_english_test', 'session_001', '我想买一个iPhone 15 Pro，预算8000元左右', 'purchase_intent', 0.95, '{"product": "iPhone 15 Pro", "budget": 8000, "currency": "CNY"}', '{"intent_strength": "high", "ready_to_buy": true}'),
('user_test_profile', 'session_002', '有什么好的护肤品推荐吗？', 'recommendation_request', 0.88, '{"category": "护肤品"}', '{"intent_strength": "medium", "needs_recommendation": true}');

-- ===================================================================
-- 15. Table Comments
-- ===================================================================

COMMENT ON TABLE chat_sessions IS 'Stores chat session metadata including system prompts';
COMMENT ON TABLE chat_messages IS 'Stores individual chat messages with session context';
COMMENT ON TABLE user_profiles IS 'User profile information including preferences and behavior patterns';
COMMENT ON TABLE user_behaviors IS 'Tracks user behavior events for analysis and recommendation';
COMMENT ON TABLE product_categories IS 'Product category hierarchy';
COMMENT ON TABLE products IS 'Product catalog with detailed information';
COMMENT ON TABLE ads IS 'Advertisement campaigns and creatives';
COMMENT ON TABLE intent_analyses IS 'Analysis of user intent from input text';
COMMENT ON TABLE recommendations IS 'Generated recommendations for users';
COMMENT ON TABLE ad_recommendations IS 'Specific ad recommendations with tracking';
COMMENT ON TABLE user_sessions IS 'Web session tracking for users';
COMMENT ON TABLE ab_tests IS 'A/B test variant assignments and results';

COMMIT;