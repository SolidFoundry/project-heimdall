-- Project Heimdall 统一数据库架构
-- Version: 2.0.0
-- Description: 统一完整的数据库架构，解决所有表结构不一致问题

BEGIN;

-- ===================================================================
-- 0. Schema Migrations Table
-- ===================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- 记录此统一架构版本
INSERT INTO schema_migrations (version, description) 
VALUES ('unified_2.0', 'Unified database schema with consistent data types and structures')
ON CONFLICT (version) DO NOTHING;

-- ===================================================================
-- 1. 产品表 (Products) - 统一产品定义
-- ===================================================================
DROP TABLE IF EXISTS products CASCADE;
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    image_url VARCHAR(500),
    tags TEXT[],  -- 产品标签数组
    attributes JSONB,  -- 产品属性（颜色、尺寸等）
    stock_quantity INTEGER DEFAULT 0,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 产品表索引
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_tags ON products USING GIN(tags);
CREATE INDEX idx_products_rating ON products(rating);
CREATE INDEX idx_products_active ON products(is_active);

-- ===================================================================
-- 2. 用户行为表 (User Behaviors) - 统一结构
-- ===================================================================
DROP TABLE IF EXISTS user_behaviors CASCADE;
CREATE TABLE user_behaviors (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    behavior_type VARCHAR(50) NOT NULL, -- search, view, click, purchase
    
    -- 直接访问的产品信息列（与products表保持一致）
    product_id INTEGER,  -- 改为INTEGER类型以匹配products.id
    category VARCHAR(100),
    brand VARCHAR(100),
    product_name VARCHAR(500),
    price DECIMAL(10, 2),
    
    -- 原始JSON数据（向后兼容）
    behavior_data JSONB DEFAULT '{}'::jsonb,
    
    -- 意图分析结果
    detected_intent VARCHAR(100),
    intent_confidence DECIMAL(3, 2) DEFAULT 0.0,
    
    -- 时间戳
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- 用户行为表索引
CREATE INDEX idx_user_behaviors_user_id ON user_behaviors(user_id);
CREATE INDEX idx_user_behaviors_session_id ON user_behaviors(session_id);
CREATE INDEX idx_user_behaviors_type ON user_behaviors(behavior_type);
CREATE INDEX idx_user_behaviors_product_id ON user_behaviors(product_id);
CREATE INDEX idx_user_behaviors_category ON user_behaviors(category);
CREATE INDEX idx_user_behaviors_brand ON user_behaviors(brand);
CREATE INDEX idx_user_behaviors_timestamp ON user_behaviors(timestamp);
CREATE INDEX idx_user_behaviors_intent ON user_behaviors(detected_intent);

-- ===================================================================
-- 3. 用户画像表 (User Profiles) - 统一结构
-- ===================================================================
DROP TABLE IF EXISTS user_profiles CASCADE;
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- 基础信息
    age INTEGER,
    gender VARCHAR(20),
    location VARCHAR(100),
    
    -- 偏好信息
    interests TEXT[],  -- 兴趣标签
    budget_range VARCHAR(50),  -- 预算范围
    preferred_categories INTEGER[],  -- 偏好类别ID数组
    preferred_brands TEXT[],  -- 偏好品牌数组
    
    -- 历史数据
    purchase_history JSONB,  -- 购买历史
    browsing_history JSONB,  -- 浏览历史
    
    -- 分析数据
    behavior_score FLOAT DEFAULT 0.0,
    profile_data JSONB DEFAULT '{}'::jsonb,  -- 综合画像数据
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户画像表索引
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_interests ON user_profiles USING GIN(interests);
CREATE INDEX idx_user_profiles_categories ON user_profiles USING GIN(preferred_categories);
CREATE INDEX idx_user_profiles_score ON user_profiles(behavior_score);

-- ===================================================================
-- 4. 推荐记录表 (Recommendations)
-- ===================================================================
DROP TABLE IF EXISTS recommendations CASCADE;
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100),
    recommendation_type VARCHAR(50) NOT NULL, -- intent_based, collaborative, content_based, hybrid
    product_ids INTEGER[],  -- 推荐产品ID数组
    ad_ids INTEGER[],  -- 推荐广告ID数组
    scores JSONB,  -- 推荐分数
    context JSONB,  -- 推荐上下文
    is_clicked BOOLEAN DEFAULT false,
    is_purchased BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 推荐记录表索引
CREATE INDEX idx_recommendations_user ON recommendations(user_id);
CREATE INDEX idx_recommendations_session ON recommendations(session_id);
CREATE INDEX idx_recommendations_type ON recommendations(recommendation_type);
CREATE INDEX idx_recommendations_created ON recommendations(created_at);

-- ===================================================================
-- 5. 广告表 (Advertisements)
-- ===================================================================
DROP TABLE IF EXISTS ads CASCADE;
CREATE TABLE ads (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    product_id INTEGER REFERENCES products(id),
    ad_type VARCHAR(50) NOT NULL,  -- banner, product, recommendation等
    image_url VARCHAR(500),
    target_audience TEXT,  -- 目标受众描述
    budget DECIMAL(12, 2) DEFAULT 0.00,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 广告表索引
CREATE INDEX idx_ads_product ON ads(product_id);
CREATE INDEX idx_ads_type ON ads(ad_type);
CREATE INDEX idx_ads_active ON ads(is_active);
CREATE INDEX idx_ads_dates ON ads(start_date, end_date);

-- ===================================================================
-- 6. 聊天会话表 (Chat Sessions) - 保持原有功能
-- ===================================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    system_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- 7. 聊天消息表 (Chat Messages) - 保持原有功能
-- ===================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
);

-- 聊天消息表索引
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX idx_chat_messages_session_created ON chat_messages(session_id, created_at DESC);

-- ===================================================================
-- 8. 更新时间戳触发器
-- ===================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加更新时间戳触发器
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ads_updated_at BEFORE UPDATE ON ads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- 9. 表注释
-- ===================================================================
COMMENT ON TABLE products IS '产品信息表 - 统一产品数据管理';
COMMENT ON TABLE user_behaviors IS '用户行为记录表 - 支持直接列访问和JSON数据';
COMMENT ON TABLE user_profiles IS '用户画像表 - 综合用户偏好和行为分析';
COMMENT ON TABLE recommendations IS '推荐记录表 - 多种推荐算法结果存储';
COMMENT ON TABLE ads IS '广告信息表 - 广告投放和效果追踪';
COMMENT ON TABLE chat_sessions IS '聊天会话表 - 对话会话管理';
COMMENT ON TABLE chat_messages IS '聊天消息表 - 对话内容存储';

COMMIT;