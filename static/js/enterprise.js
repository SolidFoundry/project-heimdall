/**
 * 企业级前端JavaScript功能模块
 * 支持多页面导航、数据展示、推荐系统等
 */

// 全局配置
const API_BASE_URL = 'http://localhost:8002/api/v1';
const SESSION_ID = 'enterprise_session_' + Date.now();

// 页面导航管理
class PageNavigator {
    constructor() {
        this.currentPage = 'dashboard';
        this.charts = {}; // 存储图表实例
        this.init();
    }

    init() {
        console.log('PageNavigator 初始化开始...');
        
        // 绑定导航点击事件
        const navLinks = document.querySelectorAll('.nav-link');
        console.log(`找到 ${navLinks.length} 个导航链接`);
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetPage = link.getAttribute('data-page');
                console.log(`点击导航: ${targetPage}`);
                if (targetPage) {
                    this.navigateToPage(targetPage);
                }
            });
        });

        // 移动端菜单切换
        const menuToggle = document.getElementById('menuToggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('show');
            });
        }
        
        console.log('PageNavigator 初始化完成');
        
        // 自动初始化默认页面
        setTimeout(() => {
            console.log('自动初始化仪表板...');
            this.initPageSpecific('dashboard');
        }, 100);
    }

    navigateToPage(pageName) {
        // 隐藏所有页面
        document.querySelectorAll('.page-content').forEach(page => {
            page.classList.remove('active');
        });

        // 显示目标页面
        const targetPage = document.getElementById(pageName + '-page');
        if (targetPage) {
            targetPage.classList.add('active');
        }

        // 更新导航状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageName}"]`)?.classList.add('active');

        // 清理旧页面的图表以防止内存泄漏
        this.destroyAllCharts();

        this.currentPage = pageName;

        // 页面特定的初始化
        this.initPageSpecific(pageName);
    }

    initPageSpecific(pageName) {
        switch (pageName) {
            case 'dashboard':
                this.initDashboard();
                break;
            case 'user-behavior':
                this.initUserBehavior();
                break;
            case 'recommendations':
                this.initRecommendations();
                break;
            case 'intent-analysis':
                this.initIntentAnalysis();
                break;
            case 'products':
                this.initProducts();
                break;
            case 'analytics':
                this.initAnalytics();
                break;
            case 'monitoring':
                this.initMonitoring();
                break;
        }
    }

    async initDashboard() {
        console.log('初始化仪表板...');
        await this.loadDashboardData();
    }

    async loadDashboardData() {
        console.log('开始加载仪表板数据...');
        try {
            // 加载系统状态
            console.log('正在加载系统状态...');
            const healthResponse = await fetch(`${API_BASE_URL}/health`);
            const healthData = await healthResponse.json();
            console.log('✅ 系统状态数据:', healthData);
            
            // 更新系统状态卡片
            this.updateSystemStatus(healthData);

            // 加载内存数据统计
            console.log('正在加载仪表板统计...');
            const dashboardResponse = await fetch(`${API_BASE_URL}/memory/dashboard-stats`);
            const dashboardData = await dashboardResponse.json();
            console.log('✅ 仪表板统计数据:', dashboardData);
            
            // 更新仪表板统计
            this.updateDashboardStats(dashboardData);

            // 加载推荐统计
            console.log('正在加载推荐统计...');
            await this.loadRecommendationStats();
            console.log('✅ 推荐统计加载完成');

        } catch (error) {
            console.error('❌ 加载仪表板数据失败:', error);
        }
    }

    updateSystemStatus(healthData) {
        const statusElement = document.getElementById('system-status');
        if (statusElement) {
            const status = healthData.status === 'healthy' ? '在线' : '离线';
            const statusClass = healthData.status === 'healthy' ? 'status-online' : 'status-offline';
            statusElement.innerHTML = `
                <span class="status-indicator ${statusClass}"></span>
                ${status}
            `;
        }
    }

    updateDashboardStats(dashboardData) {
        console.log('更新仪表板统计数据...');
        const overview = dashboardData.overview || {};
        const totalProducts = overview.total_products || 0;
        const totalUsers = overview.total_users || 0;
        const totalBehaviors = overview.total_behaviors || 0;
        
        console.log(`统计数据: 产品=${totalProducts}, 用户=${totalUsers}, 行为=${totalBehaviors}`);
        
        // 计算平均评分
        const avgRating = dashboardData.popular_products ? 
            (dashboardData.popular_products.reduce((sum, p) => sum + (p.rating || 0), 0) / dashboardData.popular_products.length).toFixed(1) : '0.0';

        // 更新DOM元素
        const productsElement = document.getElementById('total-products');
        const usersElement = document.getElementById('total-users');
        const behaviorsElement = document.getElementById('total-behaviors');
        const ratingElement = document.getElementById('avg-rating');
        
        console.log('DOM元素:', {
            productsElement: !!productsElement,
            usersElement: !!usersElement,
            behaviorsElement: !!behaviorsElement,
            ratingElement: !!ratingElement
        });
        
        if (productsElement) productsElement.textContent = totalProducts;
        if (usersElement) usersElement.textContent = totalUsers;
        if (behaviorsElement) behaviorsElement.textContent = totalBehaviors;
        if (ratingElement) ratingElement.textContent = avgRating;
        
        console.log('✅ 仪表板统计数据更新完成');
    }

    async loadRecommendationStats() {
        try {
            // 模拟推荐统计数据
            const stats = {
                totalRecommendations: 1250,
                clickThroughRate: 3.2,
                conversionRate: 0.8
            };

            const totalRecsElement = document.getElementById('total-recommendations');
            if (totalRecsElement) totalRecsElement.textContent = stats.totalRecommendations;
            
            const ctrElement = document.getElementById('ctr-rate');
            if (ctrElement) ctrElement.textContent = stats.clickThroughRate + '%';
            
            const convElement = document.getElementById('conversion-rate');
            if (convElement) convElement.textContent = stats.conversionRate + '%';
        } catch (error) {
            console.error('加载推荐统计失败:', error);
        }
    }

    async initUserBehavior() {
        console.log('初始化用户行为分析...');
        await this.loadUserBehaviorData();
        this.initBehaviorCharts();
    }

    async loadUserBehaviorData() {
        try {
            // 加载用户列表
            const users = ['user_001', 'user_002', 'user_003', 'user_004', 'user_005'];
            const userSelect = document.getElementById('user-select');
            
            if (userSelect) {
                userSelect.innerHTML = '';
                users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user;
                    option.textContent = user;
                    userSelect.appendChild(option);
                });

                // 绑定用户选择事件
                userSelect.addEventListener('change', (e) => {
                    this.loadUserBehaviorDetails(e.target.value);
                });

                // 默认加载第一个用户
                if (users.length > 0) {
                    this.loadUserBehaviorDetails(users[0]);
                }
            }
        } catch (error) {
            console.error('加载用户行为数据失败:', error);
        }
    }

    async loadUserBehaviorDetails(userId) {
        try {
            // 获取用户画像数据
            const profileResponse = await fetch(`${API_BASE_URL}/memory/user-profile/${userId}`);
            const profileData = await profileResponse.json();
            
            // 获取用户行为数据
            const behaviors = profileData.recent_behaviors || [];
            
            // 处理行为统计
            const behaviorCounts = {};
            const categoryCounts = {};
            const timeline = [];
            
            behaviors.forEach(behavior => {
                // 统计行为类型
                const action = behavior.action;
                behaviorCounts[action] = (behaviorCounts[action] || 0) + 1;
                
                // 统计类别
                const category = behavior.category;
                if (category && category !== '搜索') {
                    categoryCounts[category] = (categoryCounts[category] || 0) + 1;
                }
                
                // 构建时间线
                const timestamp = new Date(behavior.timestamp);
                timeline.push({
                    time: timestamp.toLocaleString('zh-CN'),
                    action: `${this.getActionText(action)} ${behavior.product_name || ''}`,
                    type: action
                });
            });
            
            // 计算百分比
            const totalBehaviors = behaviors.length;
            const behaviorStats = Object.entries(behaviorCounts).map(([type, count]) => ({
                type: this.getBehaviorTypeText(type),
                count: count,
                percentage: Math.round((count / totalBehaviors) * 100)
            }));
            
            // 构建行为数据
            const behaviorData = {
                behaviors: behaviors,
                behaviorStats: behaviorStats,
                categories: categoryCounts,
                timeline: timeline.slice(0, 10) // 只显示最近10条
            };

            this.updateBehaviorCharts(behaviorData);
            this.updateBehaviorTimeline(behaviorData.timeline);

        } catch (error) {
            console.error('加载用户行为详情失败:', error);
        }
    }
    
    getActionText(action) {
        const actionMap = {
            'view': '查看了',
            'click': '点击了',
            'search': '搜索了',
            'purchase': '购买了'
        };
        return actionMap[action] || action;
    }
    
    getBehaviorTypeText(type) {
        const typeMap = {
            'view': '查看',
            'click': '点击',
            'search': '搜索',
            'purchase': '购买'
        };
        return typeMap[type] || type;
    }

    // 图表管理方法
    destroyChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
            delete this.charts[chartId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartId => {
            this.destroyChart(chartId);
        });
    }

    createChart(chartId, ctx, config) {
        this.destroyChart(chartId);
        this.charts[chartId] = new Chart(ctx, config);
        return this.charts[chartId];
    }

    updateBehaviorCharts(data) {
        // 更新行为类型饼图
        const behaviorCtx = document.getElementById('behaviorChart');
        if (behaviorCtx) {
            this.createChart('behaviorChart', behaviorCtx, {
                type: 'doughnut',
                data: {
                    labels: data.behaviors.map(b => b.type),
                    datasets: [{
                        data: data.behaviors.map(b => b.count),
                        backgroundColor: ['#4e73df', '#1cc88a', '#f6c23e', '#e74a3b']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // 更新类别偏好条形图
        const categoryCtx = document.getElementById('categoryChart');
        if (categoryCtx) {
            this.createChart('categoryChart', categoryCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.categories),
                    datasets: [{
                        label: '偏好度',
                        data: Object.values(data.categories),
                        backgroundColor: '#4e73df'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    updateBehaviorTimeline(timeline) {
        const timelineElement = document.getElementById('behavior-timeline');
        if (timelineElement) {
            timelineElement.innerHTML = '';
            timeline.forEach(item => {
                const timelineItem = document.createElement('div');
                timelineItem.className = 'behavior-item';
                timelineItem.innerHTML = `
                    <div class="behavior-time">${item.time}</div>
                    <div class="behavior-action">${item.action}</div>
                    <div class="behavior-type">${item.type}</div>
                `;
                timelineElement.appendChild(timelineItem);
            });
        }
    }

    initBehaviorCharts() {
        // 初始化图表容器
        console.log('初始化行为图表...');
    }

    async initRecommendations() {
        console.log('初始化推荐系统...');
        await this.loadRecommendationData();
        this.initRecommendationControls();
    }

    async loadRecommendationData() {
        try {
            // 加载推荐结果
            const requestData = {
                user_id: 'user_001',
                session_id: SESSION_ID,
                limit: 10,
                strategy: 'hybrid'
            };

            const response = await fetch(`${API_BASE_URL}/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const data = await response.json();
                this.displayRecommendations(data.recommendations);
            } else {
                // 模拟推荐数据
                const mockRecommendations = [
                    {
                        id: 1,
                        name: 'iPhone 15 Pro Max',
                        description: '苹果旗舰手机，搭载A17 Pro芯片',
                        price: 9999,
                        rating: 4.8,
                        recommendation_reason: '基于您的购买历史推荐'
                    },
                    {
                        id: 2,
                        name: 'MacBook Pro',
                        description: '专业级笔记本电脑，M3 Pro芯片',
                        price: 15999,
                        rating: 4.9,
                        recommendation_reason: '基于您的浏览偏好推荐'
                    },
                    {
                        id: 3,
                        name: 'AirPods Pro',
                        description: '主动降噪无线耳机',
                        price: 1999,
                        rating: 4.7,
                        recommendation_reason: '基于相似用户行为推荐'
                    }
                ];
                this.displayRecommendations(mockRecommendations);
            }
        } catch (error) {
            console.error('加载推荐数据失败:', error);
        }
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendations-container');
        if (container) {
            container.innerHTML = '';
            recommendations.forEach(rec => {
                const recCard = document.createElement('div');
                recCard.className = 'col-md-4 mb-4';
                recCard.innerHTML = `
                    <div class="card product-card h-100">
                        <img src="${rec.image_url || 'https://via.placeholder.com/300x200'}" 
                             class="card-img-top product-image" alt="${rec.name}">
                        <div class="card-body">
                            <h5 class="card-title">${rec.name}</h5>
                            <p class="card-text">${rec.description}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="product-price">¥${rec.price}</span>
                                <div class="product-rating">
                                    ${'★'.repeat(Math.floor(rec.rating))}${'☆'.repeat(5-Math.floor(rec.rating))}
                                    <small>(${rec.review_count || 0})</small>
                                </div>
                            </div>
                            <div class="mt-2">
                                <span class="badge bg-primary">${rec.recommendation_reason}</span>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(recCard);
            });
        }
    }

    initRecommendationControls() {
        // 策略选择
        const strategySelect = document.getElementById('recommendation-strategy');
        if (strategySelect) {
            strategySelect.addEventListener('change', (e) => {
                this.loadRecommendationsByStrategy(e.target.value);
            });
        }

        // 用户选择
        const userSelect = document.getElementById('recommendation-user');
        if (userSelect) {
            userSelect.addEventListener('change', (e) => {
                this.loadRecommendationsForUser(e.target.value);
            });
        }
    }

    async loadRecommendationsByStrategy(strategy) {
        try {
            const requestData = {
                user_id: 'user_001',
                session_id: SESSION_ID,
                limit: 10,
                strategy: strategy
            };

            const response = await fetch(`${API_BASE_URL}/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const data = await response.json();
                this.displayRecommendations(data.recommendations);
            }
        } catch (error) {
            console.error('加载推荐数据失败:', error);
        }
    }

    async loadRecommendationsForUser(userId) {
        try {
            const requestData = {
                user_id: userId,
                session_id: SESSION_ID,
                limit: 10,
                strategy: 'hybrid'
            };

            const response = await fetch(`${API_BASE_URL}/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const data = await response.json();
                this.displayRecommendations(data.recommendations);
            }
        } catch (error) {
            console.error('加载推荐数据失败:', error);
        }
    }

    async initProducts() {
        console.log('初始化产品管理...');
        await this.loadProductsData();
        this.initProductsTable();
    }

    async loadProductsData() {
        try {
            const response = await fetch(`${API_BASE_URL}/memory/products`);
            const data = await response.json();
            this.displayProducts(data.products || []);
        } catch (error) {
            console.error('加载产品数据失败:', error);
        }
    }

    displayProducts(products) {
        const tableBody = document.getElementById('products-table-body');
        if (tableBody) {
            tableBody.innerHTML = '';
            products.forEach(product => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${product.id}</td>
                    <td>${product.name}</td>
                    <td>${product.description}</td>
                    <td>¥${product.price}</td>
                    <td>${product.category_id}</td>
                    <td>${product.brand}</td>
                    <td>${product.rating || 0}</td>
                    <td>${product.stock_quantity || 0}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="navigator.viewProduct(${product.id})">查看</button>
                        <button class="btn btn-sm btn-warning" onclick="navigator.editProduct(${product.id})">编辑</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
    }

    initProductsTable() {
        // 初始化DataTables
        const table = $('#products-table');
        if (table.length) {
            table.DataTable({
                responsive: true,
                pageLength: 10,
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.10.24/i18n/Chinese.json'
                }
            });
        }
    }

    async initAnalytics() {
        console.log('初始化分析页面...');
        await this.loadAnalyticsData();
        this.initAnalyticsCharts();
    }

    async loadAnalyticsData() {
        try {
            // 模拟分析数据
            const analyticsData = {
                userGrowth: [
                    { month: '1月', users: 120 },
                    { month: '2月', users: 150 },
                    { month: '3月', users: 180 },
                    { month: '4月', users: 220 },
                    { month: '5月', users: 260 },
                    { month: '6月', users: 300 }
                ],
                revenue: [
                    { month: '1月', revenue: 50000 },
                    { month: '2月', users: 65000 },
                    { month: '3月', users: 80000 },
                    { month: '4月', users: 95000 },
                    { month: '5月', users: 110000 },
                    { month: '6月', users: 130000 }
                ],
                conversionRates: [
                    { strategy: '协同过滤', rate: 3.2 },
                    { strategy: '内容过滤', rate: 2.8 },
                    { strategy: '混合推荐', rate: 4.1 }
                ]
            };

            this.updateAnalyticsCharts(analyticsData);
        } catch (error) {
            console.error('加载分析数据失败:', error);
        }
    }

    updateAnalyticsCharts(data) {
        // 用户增长趋势
        const userGrowthCtx = document.getElementById('userGrowthChart');
        if (userGrowthCtx) {
            this.createChart('userGrowthChart', userGrowthCtx, {
                type: 'line',
                data: {
                    labels: data.userGrowth.map(d => d.month),
                    datasets: [{
                        label: '用户数',
                        data: data.userGrowth.map(d => d.users),
                        borderColor: '#4e73df',
                        backgroundColor: 'rgba(78, 115, 223, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // 收入趋势
        const revenueCtx = document.getElementById('revenueChart');
        if (revenueCtx) {
            this.createChart('revenueChart', revenueCtx, {
                type: 'line',
                data: {
                    labels: data.revenue.map(d => d.month),
                    datasets: [{
                        label: '收入',
                        data: data.revenue.map(d => d.revenue),
                        borderColor: '#1cc88a',
                        backgroundColor: 'rgba(28, 200, 138, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // 推荐策略对比
        const conversionCtx = document.getElementById('conversionChart');
        if (conversionCtx) {
            this.createChart('conversionChart', conversionCtx, {
                type: 'bar',
                data: {
                    labels: data.conversionRates.map(d => d.strategy),
                    datasets: [{
                        label: '转化率 (%)',
                        data: data.conversionRates.map(d => d.rate),
                        backgroundColor: ['#4e73df', '#1cc88a', '#f6c23e']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    initAnalyticsCharts() {
        // 初始化分析图表
        console.log('初始化分析图表...');
    }

    async initMonitoring() {
        console.log('初始化监控页面...');
        await this.loadMonitoringData();
        this.startRealTimeMonitoring();
    }

    async loadMonitoringData() {
        try {
            // 模拟监控数据
            const monitoringData = {
                systemMetrics: {
                    cpu: 45,
                    memory: 62,
                    disk: 78,
                    network: 23
                },
                apiMetrics: {
                    totalRequests: 15420,
                    errorRate: 0.8,
                    avgResponseTime: 125,
                    activeUsers: 342
                },
                databaseMetrics: {
                    connections: 45,
                    queryTime: 85,
                    cacheHitRate: 92
                }
            };

            this.updateMonitoringDisplay(monitoringData);
        } catch (error) {
            console.error('加载监控数据失败:', error);
        }
    }

    updateMonitoringDisplay(data) {
        // 系统指标
        this.updateMetricCard('cpu-usage', data.systemMetrics.cpu, '%');
        this.updateMetricCard('memory-usage', data.systemMetrics.memory, '%');
        this.updateMetricCard('disk-usage', data.systemMetrics.disk, '%');
        this.updateMetricCard('network-usage', data.systemMetrics.network, '%');

        // API指标
        const totalRequestsElement = document.getElementById('total-requests');
        if (totalRequestsElement) totalRequestsElement.textContent = data.apiMetrics.totalRequests.toLocaleString();
        
        const errorRateElement = document.getElementById('error-rate');
        if (errorRateElement) errorRateElement.textContent = data.apiMetrics.errorRate + '%';
        
        const responseTimeElement = document.getElementById('avg-response-time');
        if (responseTimeElement) responseTimeElement.textContent = data.apiMetrics.avgResponseTime + 'ms';
        
        const activeUsersElement = document.getElementById('active-users');
        if (activeUsersElement) activeUsersElement.textContent = data.apiMetrics.activeUsers;

        // 数据库指标
        const dbConnectionsElement = document.getElementById('db-connections');
        if (dbConnectionsElement) dbConnectionsElement.textContent = data.databaseMetrics.connections;
        
        const queryTimeElement = document.getElementById('query-time');
        if (queryTimeElement) queryTimeElement.textContent = data.databaseMetrics.queryTime + 'ms';
        
        const cacheHitElement = document.getElementById('cache-hit-rate');
        if (cacheHitElement) cacheHitElement.textContent = data.databaseMetrics.cacheHitRate + '%';
    }

    updateMetricCard(elementId, value, unit) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value + unit;
            
            // 根据数值设置颜色
            const card = element.closest('.card');
            if (card) {
                card.className = 'card';
                if (value > 80) {
                    card.classList.add('border-left-danger');
                } else if (value > 60) {
                    card.classList.add('border-left-warning');
                } else {
                    card.classList.add('border-left-success');
                }
            }
        }
    }

    startRealTimeMonitoring() {
        // 每30秒更新一次监控数据
        setInterval(() => {
            this.loadMonitoringData();
        }, 30000);
    }

    async initIntentAnalysis() {
        console.log('初始化AI意图分析页面...');
        // 设置页面标题
        const pageTitleElement = document.getElementById('page-title');
        if (pageTitleElement) pageTitleElement.textContent = 'AI意图分析';
        
        // 添加示例输入提示
        const examples = [
            "我想买一台性价比高的笔记本电脑",
            "推荐一款适合运动的蓝牙耳机",
            "我想换个新手机，预算在5000左右",
            "有什么好的智能手表推荐吗？",
            "我想买平板电脑用来看视频"
        ];
        
        const userInput = document.getElementById('userInput');
        if (userInput) {
            userInput.placeholder = `例如：${examples[Math.floor(Math.random() * examples.length)]}`;
        }
    }

    // 产品管理方法
    viewProduct(productId) {
        console.log('查看产品:', productId);
        // 实现产品查看逻辑
    }

    editProduct(productId) {
        console.log('编辑产品:', productId);
        // 实现产品编辑逻辑
    }

    // 模拟用户行为
    async simulateUserBehavior(userId, behaviorType, behaviorData) {
        try {
            const requestData = {
                user_id: userId,
                session_id: SESSION_ID,
                behavior_type: behaviorType,
                behavior_data: behaviorData
            };

            const response = await fetch(`${API_BASE_URL}/record-behavior`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                console.log('用户行为记录成功');
                this.showNotification('用户行为记录成功', 'success');
            } else {
                console.error('用户行为记录失败');
                this.showNotification('用户行为记录失败', 'error');
            }
        } catch (error) {
            console.error('模拟用户行为失败:', error);
            this.showNotification('模拟用户行为失败', 'error');
        }
    }

    // 显示通知
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // 3秒后自动关闭
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// 全局导航器实例
const navigator = new PageNavigator();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('企业级前端系统初始化完成');
    
    // 初始化提示工具
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 初始化弹出框
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// 导出全局对象
window.navigator = navigator;

// 推荐引擎功能
class RecommendationEngine {
    constructor() {
        this.apiBaseUrl = API_BASE_URL;
        this.sessionId = SESSION_ID;
    }

    async getRecommendations(userId, limit = 10, strategy = 'hybrid') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/memory/recommendations/${userId}?limit=${limit}&strategy=${strategy}`);
            const data = await response.json();
            
            if (response.ok) {
                return data.recommendations || [];
            } else {
                console.error('获取推荐失败:', data.detail);
                return [];
            }
        } catch (error) {
            console.error('推荐引擎错误:', error);
            return [];
        }
    }

    async getRecommendationStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/memory/recommendation-stats`);
            const data = await response.json();
            
            if (response.ok) {
                return data;
            } else {
                console.error('获取推荐统计失败:', data.detail);
                return null;
            }
        } catch (error) {
            console.error('推荐统计错误:', error);
            return null;
        }
    }
}

// AI意图分析功能
class IntentAnalyzer {
    constructor() {
        this.apiBaseUrl = API_BASE_URL;
        this.sessionId = SESSION_ID;
    }

    async analyzeIntent(userInput, userId, strategy = 'hybrid') {
        try {
            // 显示加载状态
            this.showLoading(true);
            
            // 调用混合推荐API
            const response = await fetch(`${this.apiBaseUrl}/hybrid-recommendations/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    user_input: userInput,
                    session_id: this.sessionId,
                    limit: 8,
                    strategy: strategy
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // 显示分析结果
            this.displayAnalysisResult(data);
            
        } catch (error) {
            console.error('AI意图分析失败:', error);
            this.showError('AI意图分析失败: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    displayAnalysisResult(data) {
        // 显示意图分析结果
        if (data.intent_analysis) {
            this.displayIntentAnalysis(data.intent_analysis);
        }
        
        // 显示用户画像
        if (data.behavior_profile) {
            this.displayUserProfile(data.behavior_profile);
        }
        
        // 显示推荐结果
        if (data.recommendations && data.recommendations.length > 0) {
            this.displayRecommendations(data.recommendations);
        }
        
        // 显示结果区域
        document.getElementById('intentAnalysisResult').style.display = 'flex';
        document.getElementById('recommendationResult').style.display = 'block';
    }

    displayIntentAnalysis(intentAnalysis) {
        const container = document.getElementById('intentAnalysisContent');
        
        const html = `
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-info">
                        <h6><i class="fas fa-brain"></i> AI意图识别结果</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <strong>意图类型:</strong> 
                                <span class="badge bg-primary">${intentAnalysis.intent_type || '未知'}</span>
                            </div>
                            <div class="col-md-6">
                                <strong>置信度:</strong> 
                                <span class="badge bg-success">${(intentAnalysis.confidence * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-md-6">
                                <strong>紧急程度:</strong> 
                                <span class="badge bg-warning">${(intentAnalysis.urgency_level * 100).toFixed(1)}%</span>
                            </div>
                            <div class="col-md-6">
                                <strong>价格偏好:</strong> 
                                <span class="badge bg-info">${intentAnalysis.price_range || '中等'}</span>
                            </div>
                        </div>
                        ${intentAnalysis.product_categories && intentAnalysis.product_categories.length > 0 ? `
                        <div class="row mt-2">
                            <div class="col-12">
                                <strong>偏好类别:</strong> 
                                ${intentAnalysis.product_categories.map(cat => `<span class="badge bg-secondary me-1">${cat}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${intentAnalysis.brand_preferences && intentAnalysis.brand_preferences.length > 0 ? `
                        <div class="row mt-2">
                            <div class="col-12">
                                <strong>品牌偏好:</strong> 
                                ${intentAnalysis.brand_preferences.map(brand => `<span class="badge bg-dark me-1">${brand}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${intentAnalysis.keywords && intentAnalysis.keywords.length > 0 ? `
                        <div class="row mt-2">
                            <div class="col-12">
                                <strong>关键词:</strong> 
                                ${intentAnalysis.keywords.map(keyword => `<span class="badge bg-light text-dark me-1">${keyword}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${intentAnalysis.analysis_summary ? `
                        <div class="mt-3">
                            <strong>分析总结:</strong>
                            <p class="mb-0">${intentAnalysis.analysis_summary}</p>
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    displayUserProfile(behaviorProfile) {
        const container = document.getElementById('userProfileContent');
        
        const categoryPrefs = behaviorProfile.category_preferences || {};
        const brandPrefs = behaviorProfile.brand_preferences || {};
        const behaviorPatterns = behaviorProfile.behavior_patterns || {};
        
        const html = `
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-success">
                        <h6><i class="fas fa-user"></i> 用户行为画像</h6>
                        <div class="row">
                            <div class="col-12">
                                <strong>总行为数:</strong> 
                                <span class="badge bg-primary">${behaviorProfile.total_behaviors || 0}</span>
                            </div>
                        </div>
                        ${Object.keys(categoryPrefs).length > 0 ? `
                        <div class="row mt-2">
                            <div class="col-12">
                                <strong>类别偏好:</strong><br>
                                ${Object.entries(categoryPrefs).slice(0, 3).map(([category, score]) => 
                                    `<span class="badge bg-info me-1">${category} (${score})</span>`
                                ).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${Object.keys(brandPrefs).length > 0 ? `
                        <div class="row mt-2">
                            <div class="col-12">
                                <strong>品牌偏好:</strong><br>
                                ${Object.entries(brandPrefs).slice(0, 3).map(([brand, score]) => 
                                    `<span class="badge bg-secondary me-1">${brand} (${score})</span>`
                                ).join('')}
                            </div>
                        </div>
                        ` : ''}
                        ${Object.keys(behaviorPatterns).length > 0 ? `
                        <div class="row mt-2">
                            <div class="col-12">
                                <strong>行为模式:</strong><br>
                                ${Object.entries(behaviorPatterns).map(([behavior, count]) => 
                                    `<span class="badge bg-warning me-1">${this.getBehaviorLabel(behavior)} (${count})</span>`
                                ).join('')}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendationContent');
        const countBadge = document.getElementById('recommendationCount');
        
        countBadge.textContent = `${recommendations.length} 个推荐`;
        
        const html = `
            <div class="row">
                ${recommendations.map((product, index) => `
                    <div class="col-lg-3 col-md-4 col-sm-6 mb-3">
                        <div class="card h-100">
                            <div class="card-header">
                                <small class="text-muted">推荐分数: ${product.final_score}</small>
                            </div>
                            <div class="card-body">
                                <h6 class="card-title">${product.name}</h6>
                                <p class="card-text">
                                    <small class="text-muted">${product.category} - ${product.brand}</small><br>
                                    <strong class="text-primary">¥${product.price}</strong><br>
                                    <small class="text-success">⭐ ${product.rating || '4.0'}</small>
                                </p>
                                <div class="mb-2">
                                    <small class="text-muted">推荐理由:</small><br>
                                    <small>${product.recommendation_reason}</small>
                                </div>
                            </div>
                            <div class="card-footer">
                                <button class="btn btn-sm btn-outline-primary" onclick="viewProductDetails('${product.product_id}')">
                                    查看详情
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = html;
    }

    getBehaviorLabel(behavior) {
        const labels = {
            'view': '查看',
            'search': '搜索',
            'click': '点击',
            'purchase': '购买'
        };
        return labels[behavior] || behavior;
    }

    showLoading(show) {
        const button = document.querySelector('button[onclick="analyzeIntent()"]');
        if (button) {
            if (show) {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 分析中...';
            } else {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-search"></i> 分析意图';
            }
        }
    }

    showError(message) {
        const container = document.getElementById('recommendationContent');
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> ${message}
            </div>
        `;
        document.getElementById('recommendationResult').style.display = 'block';
    }
}

// 创建AI意图分析器实例
const intentAnalyzer = new IntentAnalyzer();

// 全局函数：分析意图
async function analyzeIntent() {
    const userInput = document.getElementById('userInput').value.trim();
    const userId = document.getElementById('userIdSelect').value;
    const strategy = document.getElementById('recommendationStrategy').value;
    
    if (!userInput) {
        alert('请输入用户内容');
        return;
    }
    
    await intentAnalyzer.analyzeIntent(userInput, userId, strategy);
}

// 全局函数：查看产品详情
function viewProductDetails(productId) {
    alert(`查看产品详情: ${productId}`);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('企业前端系统初始化...');
    
    try {
        // 初始化页面导航器
        window.pageNavigator = new PageNavigator();
        console.log('✅ PageNavigator 初始化成功');
        
        // 初始化意图分析器
        window.intentAnalyzer = new IntentAnalyzer();
        console.log('✅ IntentAnalyzer 初始化成功');
        
        // 初始化推荐引擎
        window.recommendationEngine = new RecommendationEngine();
        console.log('✅ RecommendationEngine 初始化成功');
        
        console.log('✅ 企业前端系统初始化完成');
    } catch (error) {
        console.error('❌ 企业前端系统初始化失败:', error);
    }
});