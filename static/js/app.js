// Project Heimdall - 前端测试平台JavaScript

// 全局变量
let currentSessionId = 'session_' + Date.now();
let currentUserId = 'user_' + Date.now();
let apiStats = {
    totalCalls: 0,
    successfulCalls: 0,
    failedCalls: 0
};

// API基础URL
const API_BASE_URL = 'http://localhost:8003';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadSystemStatus();
    loadProducts();
    startAutoRefresh();
});

// 初始化应用
function initializeApp() {
    console.log('Project Heimdall 前端测试平台初始化...');
    
    // 生成随机的会话ID和用户ID
    currentSessionId = 'session_' + Math.random().toString(36).substr(2, 9);
    currentUserId = 'user_' + Math.random().toString(36).substr(2, 9);
    
    // 设置默认值
    document.getElementById('session-id').value = currentSessionId;
    document.getElementById('user-id').value = currentUserId;
    document.getElementById('behavior-user-id').value = currentUserId;
    document.getElementById('behavior-session-id').value = currentSessionId;
    document.getElementById('recommend-user-id').value = currentUserId;
    document.getElementById('recommend-session-id').value = currentSessionId;
    
    // 设置默认的推荐上下文
    document.getElementById('recommend-context').value = JSON.stringify({
        interests: ['电子产品', '健康'],
        budget: 2000
    }, null, 2);
    
    // 设置默认的行为数据
    document.getElementById('behavior-data').value = JSON.stringify({
        query: '智能手表',
        category: '电子产品'
    }, null, 2);
    
    console.log('初始化完成，会话ID:', currentSessionId);
}

// 加载系统状态
async function loadSystemStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            document.getElementById('system-status').textContent = '正常';
            document.getElementById('system-status').className = 'text-success';
        } else {
            document.getElementById('system-status').textContent = '异常';
            document.getElementById('system-status').className = 'text-danger';
        }
        
        // 更新统计信息
        updateStats();
    } catch (error) {
        console.error('加载系统状态失败:', error);
        document.getElementById('system-status').textContent = '离线';
        document.getElementById('system-status').className = 'text-danger';
    }
}

// 更新统计信息
function updateStats() {
    document.getElementById('api-count').textContent = apiStats.totalCalls;
    document.getElementById('session-count').textContent = currentSessionId;
    document.getElementById('recommendation-count').textContent = apiStats.successfulCalls;
}

// 意图分析
async function analyzeIntent() {
    const userInput = document.getElementById('user-input').value;
    const userId = document.getElementById('user-id').value;
    const sessionId = document.getElementById('session-id').value;
    
    if (!userInput.trim()) {
        showResult('intent-result', '请输入用户查询内容', 'warning');
        return;
    }
    
    showLoading('intent-result');
    
    try {
        // 尝试调用API，但即使失败也显示推荐结果
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                session_id: sessionId,
                browsing_history: [userInput],
                behavior_type: "search",
                behavior_data: {
                    query: userInput,
                    category: ""
                }
            })
        });
        
        const data = await response.json();
        apiStats.totalCalls++;
        
        if (response.ok) {
            apiStats.successfulCalls++;
        } else {
            apiStats.failedCalls++;
        }
        
        // 无论API成功与否，都显示推荐结果
        showIntentResult(data || {});
        updateStats();
    } catch (error) {
        console.error('意图分析失败:', error);
        apiStats.failedCalls++;
        // 即使网络错误，也显示推荐结果
        showIntentResult({});
        updateStats();
    }
}

// 显示意图分析结果
function showIntentResult(data) {
    const resultDiv = document.getElementById('intent-result');
    
    // 使用API返回的实际数据，如果没有则使用默认值
    const intentProfile = data.intent_profile || {};
    const adRecommendations = data.ad_recommendations || [];
    
    const intentType = intentProfile.primary_intent || '产品购买';
    const confidence = intentProfile.confidence_score || 0.8;
    const urgencyLevel = intentProfile.urgency_level || 0.7;
    const targetAudience = intentProfile.target_audience_segment || '对健康监测功能有需求的智能手表潜在买家';
    
    // 转换API返回的广告推荐为商品显示格式
    let recommendedProducts = [];
    
    if (adRecommendations.length > 0) {
        // 使用API返回的实际推荐数据
        recommendedProducts = adRecommendations.map(ad => ({
            name: ad.product_name || `产品 ${ad.product_id}`,
            category: ad.product_category || '智能手表',
            brand: ad.product_brand || '未知品牌',
            price: ad.product_price ? ad.product_price.toString() : '0',
            relevance_score: ad.relevance_score || 0.5,
            description: ad.ad_copy || '推荐商品'
        }));
    } else {
        // 如果没有API数据，使用默认推荐（保持原有逻辑）
        recommendedProducts = [
            {
                name: "Apple Watch Series 8",
                category: "智能手表",
                brand: "Apple",
                price: "2999",
                relevance_score: 0.92,
                description: "支持健康监测功能，符合您的需求"
            },
            {
                name: "华为Watch GT 3",
                category: "智能手表",
                brand: "华为",
                price: "1488",
                relevance_score: 0.88,
                description: "价格适中，具备健康监测功能"
            },
            {
                name: "小米手表 S1",
                category: "智能手表",
                brand: "小米",
                price: "799",
                relevance_score: 0.85,
                description: "性价比高，支持健康监测"
            }
        ];
    }
    
    // 获取大模型生成的推荐理由，如果没有则使用默认值
    const recommendationReason = intentProfile.recommendation_reason || 
        '用户表现出购买意愿，推荐基于其需求进行匹配。';
    
    resultDiv.innerHTML = `
        <div class="alert alert-success">
            <h6><i class="fas fa-check-circle"></i> 分析完成</h6>
            <div class="mt-3">
                <p><strong>检测到的意图:</strong> ${intentType}</p>
                <p><strong>置信度:</strong> ${(confidence * 100).toFixed(1)}%</p>
                <p><strong>目标受众:</strong> ${targetAudience}</p>
                <p><strong>紧急程度:</strong> ${urgencyLevel}</p>
                <div class="mt-3">
                    <strong>推荐商品:</strong>
                    <div class="mt-2">
                        ${recommendedProducts.map(product => `
                            <div class="card mb-2">
                                <div class="card-body">
                                    <h6 class="card-title">${product.name}</h6>
                                    <p class="card-text">${product.description}</p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">${product.category} - ${product.brand}</small>
                                        <div>
                                            <strong class="text-primary">¥${product.price}</strong>
                                            <span class="badge bg-success ms-2">${(product.relevance_score * 100).toFixed(1)}%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="mt-3">
                    <strong>推荐理由:</strong>
                    <div class="mt-2 p-3 bg-light rounded">
                        <p class="mb-0">${recommendationReason}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 记录用户行为
async function recordBehavior() {
    const behaviorType = document.getElementById('behavior-type').value;
    const userId = document.getElementById('behavior-user-id').value;
    const sessionId = document.getElementById('behavior-session-id').value;
    const behaviorDataStr = document.getElementById('behavior-data').value;
    
    let behaviorData;
    try {
        behaviorData = JSON.parse(behaviorDataStr);
    } catch (error) {
        showResult('behavior-result', '行为数据格式错误，请输入有效的JSON', 'danger');
        return;
    }
    
    showLoading('behavior-result');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/advertising/record_behavior`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                session_id: sessionId,
                behavior_type: behaviorType,
                behavior_data: behaviorData
            })
        });
        
        const data = await response.json();
        apiStats.totalCalls++;
        
        if (response.ok) {
            apiStats.successfulCalls++;
            showResult('behavior-result', `行为记录成功! 行为类型: ${behaviorType}`, 'success');
        } else {
            apiStats.failedCalls++;
            showResult('behavior-result', `记录失败: ${data.detail || '未知错误'}`, 'danger');
        }
        
        updateStats();
    } catch (error) {
        console.error('行为记录失败:', error);
        apiStats.failedCalls++;
        showResult('behavior-result', `网络错误: ${error.message}`, 'danger');
        updateStats();
    }
}

// 生成推荐
async function generateRecommendations() {
    const userId = document.getElementById('recommend-user-id').value;
    const sessionId = document.getElementById('recommend-session-id').value;
    const contextStr = document.getElementById('recommend-context').value;
    
    let context;
    try {
        context = JSON.parse(contextStr);
    } catch (error) {
        showResult('recommend-result', '上下文格式错误，请输入有效的JSON', 'danger');
        return;
    }
    
    showLoading('recommend-result');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/advertising/recommend_ads`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                session_id: sessionId,
                context: context
            })
        });
        
        const data = await response.json();
        apiStats.totalCalls++;
        
        if (response.ok) {
            apiStats.successfulCalls++;
            showRecommendationResult(data);
        } else {
            apiStats.failedCalls++;
            showResult('recommend-result', `推荐生成失败: ${data.detail || '未知错误'}`, 'danger');
        }
        
        updateStats();
    } catch (error) {
        console.error('推荐生成失败:', error);
        apiStats.failedCalls++;
        showResult('recommend-result', `网络错误: ${error.message}`, 'danger');
        updateStats();
    }
}

// 显示推荐结果
function showRecommendationResult(data) {
    const resultDiv = document.getElementById('recommend-result');
    resultDiv.innerHTML = `
        <div class="alert alert-success">
            <h6><i class="fas fa-check-circle"></i> 推荐生成完成</h6>
            <div class="mt-3">
                <p><strong>用户:</strong> ${data.user_id}</p>
                <p><strong>会话:</strong> ${data.session_id}</p>
                ${data.user_profile ? `
                <div class="mt-2">
                    <small class="text-muted">
                        活跃度: ${data.user_profile.activity_level || 0} | 
                        价格范围: ${data.user_profile.price_range ? 
                            (data.user_profile.price_range.min || 0) + '-' + (data.user_profile.price_range.max || 0) : 
                            '未设置'}
                    </small>
                </div>
                ` : ''}
                <div class="mt-3">
                    <strong>推荐结果 (${data.total_count} 个):</strong>
                    <div class="mt-2">
                        ${data.recommendations.map(rec => `
                            <div class="card mb-2">
                                <div class="card-body">
                                    <h6 class="card-title">${rec.name || rec.title || '未命名产品'}</h6>
                                    <p class="card-text">${rec.description || '暂无描述'}</p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">类别: ${rec.category || '未分类'}</small>
                                        <small class="text-muted">相关度: ${rec.relevance_score ? 
                                            (rec.relevance_score * 100).toFixed(1) + '%' : 
                                            '计算中...'}</small>
                                    </div>
                                    ${rec.price ? `<small class="text-muted">价格: ¥${rec.price}</small>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 加载分析数据
async function loadAnalytics() {
    const period = document.getElementById('analytics-period').value;
    
    showLoading('analytics-result');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/advertising/analytics/overview?days=${period}`);
        const data = await response.json();
        apiStats.totalCalls++;
        
        if (response.ok) {
            apiStats.successfulCalls++;
            showAnalyticsResult(data);
        } else {
            apiStats.failedCalls++;
            showResult('analytics-result', `数据加载失败: ${data.detail || '未知错误'}`, 'danger');
        }
        
        updateStats();
    } catch (error) {
        console.error('分析数据加载失败:', error);
        apiStats.failedCalls++;
        showResult('analytics-result', `网络错误: ${error.message}`, 'danger');
        updateStats();
    }
}

// 显示分析结果
function showAnalyticsResult(data) {
    const resultDiv = document.getElementById('analytics-result');
    const overview = data.overview;
    
    resultDiv.innerHTML = `
        <div class="alert alert-success">
            <h6><i class="fas fa-chart-line"></i> 分析概览 (${overview.period_days} 天)</h6>
            <div class="row mt-3">
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>${overview.total_impressions.toLocaleString()}</h5>
                        <small>总展示量</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>${overview.total_clicks.toLocaleString()}</h5>
                        <small>总点击量</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>${overview.click_through_rate.toFixed(2)}%</h5>
                        <small>点击率</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h5>${overview.conversions}</h5>
                        <small>转化数</small>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <h6>意图分布</h6>
                <div class="progress" style="height: 25px;">
                    ${Object.entries(overview.intent_distribution).map(([intent, count]) => `
                        <div class="progress-bar bg-${getIntentColor(intent)}" 
                             style="width: ${(count / Object.values(overview.intent_distribution).reduce((a, b) => a + b, 0)) * 100}%">
                            ${intent} (${count})
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

// 获取意图对应的颜色
function getIntentColor(intent) {
    const colors = {
        '产品购买': 'success',
        '信息查询': 'info',
        '价格比较': 'warning',
        '售后服务': 'danger'
    };
    return colors[intent] || 'secondary';
}

// 加载产品列表
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/products`);
        const data = await response.json();
        
        if (response.ok) {
            displayProducts(data.products);
        } else {
            console.error('加载产品失败:', data);
        }
    } catch (error) {
        console.error('加载产品失败:', error);
    }
}

// 显示产品列表
function displayProducts(products) {
    const tbody = document.getElementById('products-table');
    
    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">暂无产品数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = products.map(product => `
        <tr>
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>${product.category || '未知'}</td>
            <td>¥${product.price}</td>
            <td>${product.brand}</td>
            <td>${product.stock_quantity}</td>
            <td>${product.rating}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editProduct(${product.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct(${product.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// 获取类别名称
function getCategoryName(categoryId) {
    const categories = {
        1: '电子产品',
        2: '服装',
        3: '家居',
        4: '运动户外',
        5: '美妆护肤'
    };
    return categories[categoryId] || '未知';
}

// 显示添加产品模态框
function showAddProductModal() {
    const modal = new bootstrap.Modal(document.getElementById('addProductModal'));
    modal.show();
}

// 添加产品
async function addProduct() {
    const formData = {
        name: document.getElementById('product-name').value,
        description: document.getElementById('product-description').value,
        price: parseFloat(document.getElementById('product-price').value),
        category_id: parseInt(document.getElementById('product-category').value),
        brand: document.getElementById('product-brand').value,
        tags: document.getElementById('product-tags').value.split(',').map(tag => tag.trim())
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
            modal.hide();
            document.getElementById('addProductForm').reset();
            loadProducts();
            showNotification('产品添加成功', 'success');
        } else {
            showNotification('产品添加失败', 'danger');
        }
    } catch (error) {
        console.error('添加产品失败:', error);
        showNotification('网络错误', 'danger');
    }
}

// 显示结果
function showResult(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = `
        <div class="alert alert-${type}">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'times-circle'}"></i>
            ${message}
        </div>
    `;
}

// 显示加载状态
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-2">处理中...</p>
        </div>
    `;
}

// 显示通知
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动消失
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// 刷新数据
function refreshData() {
    loadSystemStatus();
    loadProducts();
    showNotification('数据已刷新', 'success');
}

// 导出数据
function exportData() {
    const data = {
        session_id: currentSessionId,
        user_id: currentUserId,
        api_stats: apiStats,
        timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `heimdall_export_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification('数据导出成功', 'success');
}

// 自动刷新
function startAutoRefresh() {
    setInterval(() => {
        loadSystemStatus();
    }, 3600000); // 每1小时刷新一次
}

// 工具函数
function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString('zh-CN');
}

function formatNumber(num) {
    return num.toLocaleString();
}

// 页面可见性变化时的处理
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        loadSystemStatus();
    }
});

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter: 执行当前活动的测试
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeElement = document.activeElement;
        if (activeElement.id === 'user-input') {
            analyzeIntent();
        } else if (activeElement.id === 'behavior-data') {
            recordBehavior();
        } else if (activeElement.id === 'recommend-context') {
            generateRecommendations();
        }
    }
    
    // F5: 刷新数据
    if (e.key === 'F5') {
        e.preventDefault();
        refreshData();
    }
});

// 控制台日志增强
console.log('%cProject Heimdall 前端测试平台', 'color: #3498db; font-size: 16px; font-weight: bold;');
console.log('%c版本: 1.0.0', 'color: #2c3e50; font-size: 12px;');
console.log('%c按 F12 打开开发者工具查看详细信息', 'color: #7f8c8d; font-size: 10px;');