-- Project Heimdall 产品和广告数据表
-- 创建时间：2025-08-29
-- 描述：支持前端测试界面的数据表

-- 1. 产品类别表
CREATE TABLE IF NOT EXISTS product_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER REFERENCES product_categories(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 产品表
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INTEGER REFERENCES product_categories(id),
    brand VARCHAR(100),
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

-- 3. 广告表
CREATE TABLE IF NOT EXISTS ads (
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

-- 4. 用户画像表
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER,
    gender VARCHAR(20),
    location VARCHAR(100),
    interests TEXT[],  -- 兴趣标签
    budget_range VARCHAR(50),  -- 预算范围
    preferred_categories INTEGER[],  -- 偏好类别ID数组
    purchase_history JSONB,  -- 购买历史
    browsing_history JSONB,  -- 浏览历史
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 用户行为记录表（扩展现有表结构）
ALTER TABLE user_behaviors 
ADD COLUMN product_id INTEGER REFERENCES products(id),
ADD COLUMN ad_id INTEGER REFERENCES ads(id),
ADD COLUMN session_id VARCHAR(100),
ADD COLUMN page_url VARCHAR(500),
ADD COLUMN referrer VARCHAR(500),
ADD COLUMN device_info JSONB;

-- 6. 推荐记录表
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100),
    recommendation_type VARCHAR(50) NOT NULL,  -- intent_based, collaborative, content_based等
    product_ids INTEGER[],  -- 推荐产品ID数组
    ad_ids INTEGER[],  -- 推荐广告ID数组
    scores JSONB,  -- 推荐分数
    context JSONB,  -- 推荐上下文
    is_clicked BOOLEAN DEFAULT false,
    is_purchased BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. A/B测试表
CREATE TABLE IF NOT EXISTS ab_tests (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(200) NOT NULL,
    description TEXT,
    variant_a JSONB,  -- A版本配置
    variant_b JSONB,  -- B版本配置
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',  -- active, paused, completed
    metrics JSONB,  -- 测试指标
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 创建索引
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_tags ON products USING GIN(tags);
CREATE INDEX idx_ads_product ON ads(product_id);
CREATE INDEX idx_ads_type ON ads(ad_type);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_interests ON user_profiles USING GIN(interests);
CREATE INDEX idx_recommendations_user ON recommendations(user_id);
CREATE INDEX idx_recommendations_session ON recommendations(session_id);
CREATE INDEX idx_user_behaviors_session ON user_behaviors(session_id);
CREATE INDEX idx_user_behaviors_product ON user_behaviors(product_id);
CREATE INDEX idx_user_behaviors_ad ON user_behaviors(ad_id);

-- 9. 插入示例数据
-- 产品类别
INSERT INTO product_categories (name, description) VALUES
('电子产品', '智能手机、平板、电脑等电子产品'),
('服装', '男装、女装、童装等服装产品'),
('家居', '家具、装饰品等家居用品'),
('运动户外', '运动器材、户外用品等'),
('美妆护肤', '化妆品、护肤品等');

-- 产品示例
INSERT INTO products (name, description, price, category_id, brand, tags, attributes, stock_quantity, rating) VALUES
('iPhone 15 Pro', '苹果最新旗舰手机，搭载A17 Pro芯片', 7999.00, 1, 'Apple', ARRAY['智能手机', '5G', '拍照'], '{"color": "深空黑", "storage": "256GB", "camera": "48MP"}', 50, 4.8),
('MacBook Pro 14"', '专业级笔记本电脑，M3 Pro芯片', 14999.00, 1, 'Apple', ARRAY['笔记本', '办公', '开发'], '{"color": "银色", "storage": "512GB", "memory": "18GB"}', 30, 4.9),
('Nike Air Max 270', '经典气垫跑鞋，舒适透气', 899.00, 4, 'Nike', ARRAY['跑鞋', '运动', '气垫'], '{"color": "黑色", "size": "42", "material": "网面"}', 100, 4.6),
('雅诗兰黛小棕瓶', '经典修护精华，抗衰护肤', 780.00, 5, '雅诗兰黛', ARRAY['精华', '抗衰', '修护'], '{"volume": "30ml", "skin_type": "所有肤质"}', 80, 4.7),
('宜家简约书桌', '北欧风格书桌，简约实用', 599.00, 3, '宜家', ARRAY['家具', '书桌', '简约'], '{"color": "白色", "material": "实木", "size": "120x60cm"}', 25, 4.4);

-- 广告示例
INSERT INTO ads (title, description, product_id, ad_type, image_url, target_audience, budget) VALUES
('iPhone 15 Pro 限时优惠', '最新旗舰手机，现在购买享受12期免息', 1, 'product', '/images/iphone15_ad.jpg', '科技爱好者，追求高性能用户', 50000.00),
('MacBook Pro 专业之选', 'M3 Pro芯片，性能提升40%，专业工作者首选', 2, 'product', '/images/macbook_ad.jpg', '开发者，设计师，专业人士', 80000.00),
('Nike 跑步季特惠', 'Air Max系列全线8折，运动从这里开始', 3, 'product', '/images/nike_ad.jpg', '运动爱好者，健身人群', 30000.00);

-- 用户画像示例
INSERT INTO user_profiles (user_id, age, gender, location, interests, budget_range, preferred_categories) VALUES
('test_user_001', 28, '男', '北京', ARRAY['科技', '运动', '摄影'], '5000-10000', ARRAY[1, 4]),
('test_user_002', 32, '女', '上海', ARRAY['美妆', '时尚', '购物'], '1000-3000', ARRAY[2, 5]),
('test_user_003', 25, '男', '深圳', ARRAY['游戏', '数码', '编程'], '3000-8000', ARRAY[1]);

-- 更新表的时间戳触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ads_updated_at BEFORE UPDATE ON ads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;