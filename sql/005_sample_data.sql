-- 创建示例产品数据
INSERT INTO products (product_id, name, category, brand, price, rating, description, image_url, stock_quantity) VALUES
('laptop_001', 'ThinkPad X1 Carbon', '笔记本电脑', '联想', 8999.00, 4.8, '轻薄商务笔记本，搭载Intel i7处理器，16GB内存，512GB固态硬盘', '/images/laptop_001.jpg', 50),
('laptop_002', 'MacBook Air M2', '笔记本电脑', '苹果', 7999.00, 4.9, '全新M2芯片，13.6英寸Liquid Retina显示屏，18小时电池续航', '/images/laptop_002.jpg', 30),
('laptop_003', '小新Pro 16', '笔记本电脑', '联想', 5499.00, 4.5, '16英寸大屏，AMD锐龙7处理器，16GB内存，512GB固态硬盘', '/images/laptop_003.jpg', 80),
('laptop_004', '华硕天选游戏本', '笔记本电脑', '华硕', 6999.00, 4.6, '15.6英寸游戏本，Intel i7处理器，RTX 4060显卡，16GB内存', '/images/laptop_004.jpg', 25),
('laptop_005', '戴尔灵越14', '笔记本电脑', '戴尔', 4599.00, 4.3, '14英寸轻薄本，Intel i5处理器，8GB内存，256GB固态硬盘', '/images/laptop_005.jpg', 60),

('phone_001', 'iPhone 15 Pro', '智能手机', '苹果', 7999.00, 4.9, 'A17 Pro芯片，48MP主摄，钛金属设计，支持Action Button', '/images/phone_001.jpg', 100),
('phone_002', '华为Mate 60 Pro', '智能手机', '华为', 6999.00, 4.7, '麒麟9000S芯片，50MP三摄，卫星通话，昆仑玻璃', '/images/phone_002.jpg', 80),
('phone_003', '小米14', '智能手机', '小米', 3999.00, 4.5, '骁龙8 Gen 3处理器，50MP徕卡三摄，90W快充', '/images/phone_003.jpg', 150),
('phone_004', 'OPPO Find X7', '智能手机', 'OPPO', 4999.00, 4.6, '天玑9300处理器，哈苏影像，100W快充', '/images/phone_004.jpg', 90),
('phone_005', 'vivo X100', '智能手机', 'vivo', 4299.00, 4.4, '天玑9300处理器，蔡司影像，120W快充', '/images/phone_005.jpg', 120),

('tablet_001', 'iPad Pro 12.9', '平板电脑', '苹果', 8999.00, 4.8, 'M2芯片，12.9英寸Liquid Retina XDR显示屏，支持Apple Pencil', '/images/tablet_001.jpg', 40),
('tablet_002', 'Surface Pro 9', '平板电脑', '微软', 7999.00, 4.6, 'Intel i7处理器，13英寸触摸屏，支持Surface Pen，可拆卸键盘', '/images/tablet_002.jpg', 35),
('tablet_003', '华为MatePad Pro', '平板电脑', '华为', 3999.00, 4.5, '麒麟9000E芯片，12.6英寸OLED屏幕，支持M-Pencil', '/images/tablet_003.jpg', 60),
('tablet_004', '小米平板6', '平板电脑', '小米', 1999.00, 4.3, '骁龙870处理器，11英寸2.8K屏幕，144Hz刷新率', '/images/tablet_004.jpg', 100),
('tablet_005', '三星Tab S9', '平板电脑', '三星', 5999.00, 4.7, '骁龙8 Gen 2处理器，11英寸Dynamic AMOLED屏幕，S Pen支持', '/images/tablet_005.jpg', 45),

('headphone_001', 'AirPods Pro 2', '耳机', '苹果', 1899.00, 4.8, '主动降噪，空间音频，自适应透明模式，6小时续航', '/images/headphone_001.jpg', 200),
('headphone_002', '索尼WH-1000XM5', '耳机', '索尼', 2499.00, 4.9, '业界领先降噪，30小时续航，Hi-Res音质，多点连接', '/images/headphone_002.jpg', 80),
('headphone_003', 'Bose QuietComfort 45', '耳机', 'Bose', 2299.00, 4.7, '传奇降噪，24小时续航，舒适佩戴，清晰通话', '/images/headphone_003.jpg', 60),
('headphone_004', '华为FreeBuds Pro 3', '耳机', '华为', 1199.00, 4.5, '智慧动态降噪，高清空间音频，33小时续航', '/images/headphone_004.jpg', 150),
('headphone_005', '小米Buds 4 Pro', '耳机', '小米', 699.00, 4.3, '主动降噪，空间音频，43dB降噪深度，30小时续航', '/images/headphone_005.jpg', 300);

-- 创建示例用户行为数据
INSERT INTO user_behaviors (user_id, session_id, behavior_type, behavior_data, product_id, category, brand, product_name, price) VALUES
('user_001', 'session_001', 'view', '{"action": "view", "duration": 45}', 'laptop_001', '笔记本电脑', '联想', 'ThinkPad X1 Carbon', 8999.00),
('user_001', 'session_001', 'click', '{"action": "click", "element": "specs"}', 'laptop_001', '笔记本电脑', '联想', 'ThinkPad X1 Carbon', 8999.00),
('user_001', 'session_002', 'search', '{"query": "商务笔记本", "results": 12}', NULL, '笔记本电脑', NULL, NULL, NULL),
('user_001', 'session_002', 'view', '{"action": "view", "duration": 32}', 'laptop_003', '笔记本电脑', '联想', '小新Pro 16', 5499.00),
('user_001', 'session_003', 'view', '{"action": "view", "duration": 28}', 'phone_002', '智能手机', '华为', '华为Mate 60 Pro', 6999.00),
('user_001', 'session_003', 'click', '{"action": "click", "element": "camera"}', 'phone_002', '智能手机', '华为', '华为Mate 60 Pro', 6999.00),

('user_002', 'session_004', 'view', '{"action": "view", "duration": 67}', 'phone_001', '智能手机', '苹果', 'iPhone 15 Pro', 7999.00),
('user_002', 'session_004', 'click', '{"action": "click", "element": "buy"}', 'phone_001', '智能手机', '苹果', 'iPhone 15 Pro', 7999.00),
('user_002', 'session_005', 'purchase', '{"action": "purchase", "quantity": 1}', 'phone_001', '智能手机', '苹果', 'iPhone 15 Pro', 7999.00),
('user_002', 'session_006', 'view', '{"action": "view", "duration": 23}', 'tablet_001', '平板电脑', '苹果', 'iPad Pro 12.9', 8999.00),
('user_002', 'session_006', 'click', '{"action": "click", "element": "specs"}', 'tablet_001', '平板电脑', '苹果', 'iPad Pro 12.9', 8999.00),

('user_003', 'session_007', 'search', '{"query": "降噪耳机", "results": 8}', NULL, '耳机', NULL, NULL, NULL),
('user_003', 'session_007', 'view', '{"action": "view", "duration": 89}', 'headphone_002', '耳机', '索尼', '索尼WH-1000XM5', 2499.00),
('user_003', 'session_007', 'click', '{"action": "click", "element": "features"}', 'headphone_002', '耳机', '索尼', '索尼WH-1000XM5', 2499.00),
('user_003', 'session_008', 'view', '{"action": "view", "duration": 45}', 'headphone_001', '耳机', '苹果', 'AirPods Pro 2', 1899.00),
('user_003', 'session_008', 'click', '{"action": "click", "element": "compare"}', 'headphone_001', '耳机', '苹果', 'AirPods Pro 2', 1899.00),

('user_004', 'session_009', 'view', '{"action": "view", "duration": 34}', 'laptop_002', '笔记本电脑', '苹果', 'MacBook Air M2', 7999.00),
('user_004', 'session_009', 'click', '{"action": "click", "element": "details"}', 'laptop_002', '笔记本电脑', '苹果', 'MacBook Air M2', 7999.00),
('user_004', 'session_010', 'search', '{"query": "游戏本", "results": 15}', NULL, '笔记本电脑', NULL, NULL, NULL),
('user_004', 'session_010', 'view', '{"action": "view", "duration": 56}', 'laptop_004', '笔记本电脑', '华硕', '华硕天选游戏本', 6999.00),
('user_004', 'session_010', 'click', '{"action": "click", "element": "gpu"}', 'laptop_004', '笔记本电脑', '华硕', '华硕天选游戏本', 6999.00),

('user_005', 'session_011', 'view', '{"action": "view", "duration": 29}', 'tablet_003', '平板电脑', '华为', '华为MatePad Pro', 3999.00),
('user_005', 'session_011', 'click', '{"action": "click", "element": "display"}', 'tablet_003', '平板电脑', '华为', '华为MatePad Pro', 3999.00),
('user_005', 'session_012', 'view', '{"action": "view", "duration": 41}', 'phone_003', '智能手机', '小米', '小米14', 3999.00),
('user_005', 'session_012', 'click', '{"action": "click", "element": "camera"}', 'phone_003', '智能手机', '小米', '小米14', 3999.00),
('user_005', 'session_013', 'purchase', '{"action": "purchase", "quantity": 1}', 'phone_003', '智能手机', '小米', '小米14', 3999.00);

-- 创建示例用户画像数据
INSERT INTO user_profiles (user_id, profile_data, preferred_categories, preferred_brands, price_range_min, price_range_max, behavior_score) VALUES
('user_001', '{"preferences": {"price_sensitivity": 0.7, "brand_loyalty": 0.3, "quality_focus": 0.8}, "behavior_pattern": "researcher"}', ARRAY['笔记本电脑', '智能手机'], ARRAY['联想', '华为'], 4000.00, 9000.00, 75.5),
('user_002', '{"preferences": {"price_sensitivity": 0.2, "brand_loyalty": 0.9, "quality_focus": 0.9}, "behavior_pattern": "premium_buyer"}', ARRAY['智能手机', '平板电脑'], ARRAY['苹果'], 6000.00, 12000.00, 92.3),
('user_003', '{"preferences": {"price_sensitivity": 0.5, "brand_loyalty": 0.4, "quality_focus": 0.7}, "behavior_pattern": "audio_enthusiast"}', ARRAY['耳机'], ARRAY['索尼', '苹果'], 1500.00, 3000.00, 68.9),
('user_004', '{"preferences": {"price_sensitivity": 0.6, "brand_loyalty": 0.5, "quality_focus": 0.8}, "behavior_pattern": "gamer"}', ARRAY['笔记本电脑'], ARRAY['华硕', '苹果'], 5000.00, 10000.00, 71.2),
('user_005', '{"preferences": {"price_sensitivity": 0.8, "brand_loyalty": 0.3, "quality_focus": 0.6}, "behavior_pattern": "budget_conscious"}', ARRAY['智能手机', '平板电脑'], ARRAY['小米', '华为'], 2000.00, 6000.00, 58.7);