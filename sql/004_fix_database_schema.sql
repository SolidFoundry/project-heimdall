-- 产品表
CREATE TABLE IF NOT EXISTS products (
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_products_category (category),
    INDEX idx_products_brand (brand),
    INDEX idx_products_price (price),
    INDEX idx_products_rating (rating),
    INDEX idx_products_created_at (created_at)
);

-- 修正用户行为表，添加直接访问的列
ALTER TABLE user_behaviors 
ADD COLUMN IF NOT EXISTS product_id INTEGER,
ADD COLUMN IF NOT EXISTS category VARCHAR(100),
ADD COLUMN IF NOT EXISTS brand VARCHAR(100),
ADD COLUMN IF NOT EXISTS product_name VARCHAR(500),
ADD COLUMN IF NOT EXISTS price DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 为用户行为表创建新的索引
CREATE INDEX IF NOT EXISTS idx_user_behaviors_product_id ON user_behaviors(product_id);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_category ON user_behaviors(category);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_brand ON user_behaviors(brand);
CREATE INDEX IF NOT EXISTS idx_user_behaviors_timestamp ON user_behaviors(timestamp);

-- 修正用户画像表，确保profile_data列存在
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS profile_data JSONB DEFAULT '{}'::jsonb;

-- 为用户画像表添加其他常用字段
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS preferred_categories TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS preferred_brands TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS price_range_min DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS price_range_max DECIMAL(10, 2) DEFAULT 999999,
ADD COLUMN IF NOT EXISTS behavior_score FLOAT DEFAULT 0.0;

-- 注释
COMMENT ON TABLE products IS '产品信息表';
COMMENT ON COLUMN products.product_id IS '产品唯一标识';
COMMENT ON COLUMN products.name IS '产品名称';
COMMENT ON COLUMN products.category IS '产品类别';
COMMENT ON COLUMN products.brand IS '品牌';
COMMENT ON COLUMN products.price IS '价格';
COMMENT ON COLUMN products.rating IS '评分';
COMMENT ON COLUMN products.description IS '产品描述';
COMMENT ON COLUMN products.image_url IS '产品图片URL';
COMMENT ON COLUMN products.stock_quantity IS '库存数量';

COMMENT ON COLUMN user_behaviors.product_id IS '产品ID';
COMMENT ON COLUMN user_behaviors.category IS '产品类别';
COMMENT ON COLUMN user_behaviors.brand IS '品牌';
COMMENT ON COLUMN user_behaviors.product_name IS '产品名称';
COMMENT ON COLUMN user_behaviors.price IS '价格';
COMMENT ON COLUMN user_behaviors.timestamp IS '行为时间戳';

COMMENT ON COLUMN user_profiles.preferred_categories IS '偏好类别列表';
COMMENT ON COLUMN user_profiles.preferred_brands IS '偏好品牌列表';
COMMENT ON COLUMN user_profiles.price_range_min IS '价格范围最小值';
COMMENT ON COLUMN user_profiles.price_range_max IS '价格范围最大值';
COMMENT ON COLUMN user_profiles.behavior_score IS '行为评分';