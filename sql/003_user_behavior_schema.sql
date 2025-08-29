-- 用户行为数据表
CREATE TABLE IF NOT EXISTS user_behaviors (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    behavior_type VARCHAR(50) NOT NULL, -- search, view, click, purchase
    behavior_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_user_behaviors_user_id (user_id),
    INDEX idx_user_behaviors_session_id (session_id),
    INDEX idx_user_behaviors_type (behavior_type),
    INDEX idx_user_behaviors_created_at (created_at)
);

-- 用户画像表
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    profile_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_user_profiles_user_id (user_id),
    INDEX idx_user_profiles_updated_at (updated_at)
);

-- 推荐记录表
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    recommendation_type VARCHAR(50) NOT NULL, -- product, ad, content
    recommended_items JSONB NOT NULL,
    recommendation_score FLOAT,
    context_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_recommendations_user_id (user_id),
    INDEX idx_recommendations_type (recommendation_type),
    INDEX idx_recommendations_created_at (created_at)
);

-- 广告效果追踪表
CREATE TABLE IF NOT EXISTS ad_performance (
    id SERIAL PRIMARY KEY,
    ad_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- impression, click, conversion
    action_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_ad_performance_ad_id (ad_id),
    INDEX idx_ad_performance_user_id (user_id),
    INDEX idx_ad_performance_action (action_type),
    INDEX idx_ad_performance_created_at (created_at)
);

-- 注释
COMMENT ON TABLE user_behaviors IS '用户行为数据记录表';
COMMENT ON TABLE user_profiles IS '用户画像数据表';
COMMENT ON TABLE recommendations IS '推荐记录表';
COMMENT ON TABLE ad_performance IS '广告效果追踪表';

COMMENT ON COLUMN user_behaviors.behavior_type IS '行为类型: search-搜索, view-查看, click-点击, purchase-购买';
COMMENT ON COLUMN user_behaviors.behavior_data IS '行为数据，JSON格式存储详细信息';
COMMENT ON COLUMN user_profiles.profile_data IS '用户画像数据，包含偏好、兴趣等信息';
COMMENT ON COLUMN recommendations.recommendation_type IS '推荐类型: product-产品, ad-广告, content-内容';
COMMENT ON COLUMN recommendations.recommended_items IS '推荐项目列表，JSON格式';
COMMENT ON COLUMN recommendations.recommendation_score IS '推荐得分';
COMMENT ON COLUMN ad_performance.action_type IS '行为类型: impression-展示, click-点击, conversion-转化';