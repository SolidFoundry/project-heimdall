-- 修复数据库表结构
-- 检查并创建products表
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 检查并创建user_behaviors表
CREATE TABLE IF NOT EXISTS user_behaviors (
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
);

-- 添加缺失的列到user_behaviors表
DO $$
BEGIN
    -- 检查并添加product_id列
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_behaviors' AND column_name = 'product_id') THEN
        ALTER TABLE user_behaviors ADD COLUMN product_id VARCHAR(255);
    END IF;
    
    -- 检查并添加category列
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_behaviors' AND column_name = 'category') THEN
        ALTER TABLE user_behaviors ADD COLUMN category VARCHAR(100);
    END IF;
    
    -- 检查并添加brand列
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_behaviors' AND column_name = 'brand') THEN
        ALTER TABLE user_behaviors ADD COLUMN brand VARCHAR(100);
    END IF;
    
    -- 检查并添加product_name列
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_behaviors' AND column_name = 'product_name') THEN
        ALTER TABLE user_behaviors ADD COLUMN product_name VARCHAR(500);
    END IF;
    
    -- 检查并添加price列
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_behaviors' AND column_name = 'price') THEN
        ALTER TABLE user_behaviors ADD COLUMN price DECIMAL(10, 2);
    END IF;
    
    -- 检查并添加timestamp列
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_behaviors' AND column_name = 'timestamp') THEN
        ALTER TABLE user_behaviors ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- 插入示例产品数据
INSERT INTO products (product_id, name, category, brand, price, rating, description, image_url, stock_quantity) VALUES
('laptop_001', 'ThinkPad X1 Carbon', '笔记本电脑', '联想', 8999.00, 4.8, '轻薄商务笔记本，搭载Intel i7处理器，16GB内存，512GB固态硬盘', '/images/laptop_001.jpg', 50),
('laptop_002', 'MacBook Air M2', '笔记本电脑', '苹果', 7999.00, 4.9, '全新M2芯片，13.6英寸Liquid Retina显示屏，18小时电池续航', '/images/laptop_002.jpg', 30),
('phone_001', 'iPhone 15 Pro', '智能手机', '苹果', 7999.00, 4.9, 'A17 Pro芯片，48MP主摄，钛金属设计，支持Action Button', '/images/phone_001.jpg', 100),
('phone_002', '华为Mate 60 Pro', '智能手机', '华为', 6999.00, 4.7, '麒麟9000S芯片，50MP三摄，卫星通话，昆仑玻璃', '/images/phone_002.jpg', 80)
ON CONFLICT (product_id) DO NOTHING;

-- 插入示例用户行为数据
INSERT INTO user_behaviors (user_id, session_id, behavior_type, behavior_data, product_id, category, brand, product_name, price) VALUES
('user_001', 'session_001', 'view', '{"action": "view", "duration": 45}', 'laptop_001', '笔记本电脑', '联想', 'ThinkPad X1 Carbon', 8999.00),
('user_001', 'session_001', 'click', '{"action": "click", "element": "specs"}', 'laptop_001', '笔记本电脑', '联想', 'ThinkPad X1 Carbon', 8999.00),
('user_002', 'session_002', 'view', '{"action": "view", "duration": 67}', 'phone_001', '智能手机', '苹果', 'iPhone 15 Pro', 7999.00),
('user_002', 'session_002', 'purchase', '{"action": "purchase", "quantity": 1}', 'phone_001', '智能手机', '苹果', 'iPhone 15 Pro', 7999.00)
ON CONFLICT DO NOTHING;
