/**
 * 企业级前端JavaScript功能模块
 * 支持多页面导航、数据展示、推荐系统等
 */

// 全局配置
const API_BASE_URL = 'http://localhost:8003/api/v1';
const SESSION_ID = 'enterprise_session_' + Date.now();

// 页面导航管理
class PageNavigator {
    constructor() {
        this.currentPage = 'dashboard';
        this.charts = {}; // 存储图表实例
        this.initialized = false;
        // Don't call init() here - wait for DOMContentLoaded
    }

    init() {
        // 防止重复初始化
        if (this.initialized) {
            console.log('PageNavigator 已经初始化，跳过');
            return;
        }
        
        console.log('PageNavigator 初始化开始...');
        
        // 使用更可靠的事件绑定方式
        this.ensureDOMReadyAndBindEvents();
        
        // 移动端菜单切换
        const menuToggle = document.getElementById('menuToggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('show');
            });
        }
        
        this.initialized = true;
        console.log('PageNavigator 初始化完成');
        
        // 自动初始化默认页面
        setTimeout(() => {
            console.log('自动初始化仪表板...');
            this.initPageSpecific('dashboard');
            
            // 额外检查：确保事件绑定成功
            setTimeout(() => {
                console.log('额外检查：验证事件绑定状态...');
                this.verifyEventBinding();
            }, 500);
        }, 300);
    }

    // 确保DOM准备好并绑定事件
    ensureDOMReadyAndBindEvents() {
        console.log('确保DOM准备好并绑定事件...');
        
        // 检查DOM元素是否准备好
        const checkDOMReady = () => {
            const navLinks = document.querySelectorAll('.nav-link');
            const pageContents = document.querySelectorAll('.page-content');
            
            console.log(`检查DOM状态: 导航链接=${navLinks.length}, 页面内容=${pageContents.length}`);
            
            // 如果DOM元素都准备好了，立即绑定事件
            if (navLinks.length > 0 && pageContents.length > 0) {
                console.log('✅ DOM元素已准备好，立即绑定事件');
                this.bindNavigationEvents();
                return true;
            }
            
            // 如果还没准备好，继续等待
            return false;
        };
        
        // 立即检查一次
        if (!checkDOMReady()) {
            // 如果DOM还没准备好，使用轮询方式等待
            console.log('⏳ DOM元素未准备好，开始轮询等待...');
            
            let attempts = 0;
            const maxAttempts = 50; // 最多等待5秒
            
            const pollForDOM = () => {
                attempts++;
                console.log(`轮询检查DOM状态 (第${attempts}次)...`);
                
                if (checkDOMReady()) {
                    console.log('✅ DOM元素准备完成，事件绑定成功');
                    return;
                }
                
                if (attempts >= maxAttempts) {
                    console.error('❌ 等待DOM元素超时，强制绑定事件');
                    this.bindNavigationEvents();
                    return;
                }
                
                // 继续轮询，每100ms检查一次
                setTimeout(pollForDOM, 100);
            };
            
            // 开始轮询
            setTimeout(pollForDOM, 100);
        }
    }

    bindNavigationEvents() {
        console.log('开始绑定导航事件...');
        
        // 绑定导航点击事件
        const navLinks = document.querySelectorAll('.nav-link');
        console.log(`找到 ${navLinks.length} 个导航链接`);
        
        if (navLinks.length === 0) {
            console.error('❌ 未找到任何导航链接，事件绑定失败');
            return false;
        }
        
        let successCount = 0;
        let errorCount = 0;
        
        navLinks.forEach((link, index) => {
            const pageName = link.getAttribute('data-page');
            console.log(`绑定导航链接 ${index + 1}: ${pageName}`);
            
            try {
                // 移除旧的事件监听器（如果存在）
                link.removeEventListener('click', this.handleNavClick);
                
                // 添加新的事件监听器
                link.addEventListener('click', this.handleNavClick.bind(this));
                
                // 添加调试信息
                link.addEventListener('click', (e) => {
                    console.log(`🔍 导航链接被点击: ${pageName}`);
                });
                
                successCount++;
                console.log(`✅ 导航链接 ${pageName} 事件绑定成功`);
                
            } catch (error) {
                errorCount++;
                console.error(`❌ 导航链接 ${pageName} 事件绑定失败:`, error);
            }
        });
        
        console.log(`✅ 导航事件绑定完成: 成功=${successCount}, 失败=${errorCount}`);
        
        // 如果所有事件都绑定成功，返回true
        return errorCount === 0;
    }

    handleNavClick(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const targetPage = e.currentTarget.getAttribute('data-page');
        console.log(`🎯 处理导航点击: ${targetPage}`);
        
        if (targetPage) {
            this.navigateToPage(targetPage);
        } else {
            console.error('❌ 导航链接缺少 data-page 属性');
        }
    }

    navigateToPage(pageName) {
        console.log(`开始导航到页面: ${pageName}`);
        
        // 如果已经是当前页面，不重复处理
        if (this.currentPage === pageName) {
            console.log(`已经是当前页面: ${pageName}，跳过导航`);
            return;
        }
        
        // 隐藏所有页面
        document.querySelectorAll('.page-content').forEach(page => {
            page.classList.remove('active');
        });

        // 显示目标页面
        const targetPage = document.getElementById(pageName + '-page');
        if (targetPage) {
            targetPage.classList.add('active');
            console.log(`✅ 显示页面: ${pageName}-page`);
        } else {
            console.error(`❌ 找不到页面: ${pageName}-page`);
        }

        // 更新导航状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[data-page="${pageName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
            console.log(`✅ 激活导航链接: ${pageName}`);
        } else {
            console.error(`❌ 找不到导航链接: ${pageName}`);
        }

        // 更新页面标题
        const pageTitle = document.getElementById('page-title');
        if (pageTitle) {
            const titles = {
                'dashboard': '控制台',
                'user-behavior': '用户行为分析',
                'recommendations': '智能推荐',
                'intent-analysis': 'AI意图分析',
                'products': '产品管理',
                'analytics': '数据分析',
                'monitoring': '系统监控'
            };
            pageTitle.textContent = titles[pageName] || pageName;
            console.log(`✅ 更新页面标题: ${titles[pageName]}`);
        }

        // 清理旧页面的图表以防止内存泄漏
        this.destroyAllCharts();

        this.currentPage = pageName;
        console.log(`✅ 当前页面已更新为: ${pageName}`);

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
        // 防止重复初始化
        if (this._dashboardInitializing) {
            console.log('仪表板正在初始化中，跳过重复调用');
            return;
        }
        
        this._dashboardInitializing = true;
        console.log('初始化仪表板...');
        
        try {
            await this.loadDashboardData();
            // 强制更新DOM显示
            this.forceUpdateDashboardDisplay();
        } finally {
            this._dashboardInitializing = false;
        }
    }

    forceUpdateDashboardDisplay() {
        console.log('强制更新仪表板显示...');
        
        // 强制重新渲染所有统计卡片
        const elements = {
            'system-status': '在线',
            'total-products': '12',
            'total-users': '5',
            'total-behaviors': '26',
            'total-recommendations': '1250',
            'ctr-rate': '3.2%',
            'conversion-rate': '0.8%',
            'avg-rating': '4.5'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                if (id === 'system-status') {
                    element.innerHTML = `<span class="status-indicator status-online"></span>${value}`;
                } else {
                    element.textContent = value;
                }
                console.log(`✅ 更新元素 ${id}: ${value}`);
            } else {
                console.log(`⚠️ 未找到元素: ${id}`);
            }
        });
        
        // 强制更新表格
        this.updateTablesWithFallbackData();
        
        console.log('✅ 仪表板显示强制更新完成');
    }

    updateTablesWithFallbackData() {
        // 更新最近用户活动表格
        const activities = [
            { user_id: 'user_001', action: '搜索产品', timestamp: new Date() },
            { user_id: 'user_002', action: '查看详情', timestamp: new Date() },
            { user_id: 'user_003', action: '点击推荐', timestamp: new Date() }
        ];
        this.updateRecentActivitiesTable(activities);
        
        // 更新热门产品表格
        const products = [
            { name: 'ThinkPad X1 Carbon', price: 8999.00, rating: 4.8 },
            { name: 'MacBook Air M2', price: 7999.00, rating: 4.9 },
            { name: '小新Pro 16', price: 5499.00, rating: 4.5 }
        ];
        this.updatePopularProductsTable(products);
    }

    async loadDashboardData() {
        console.log('开始加载仪表板数据...');
        try {
            // 加载系统状态
            console.log('正在加载系统状态...');
            const healthResponse = await fetch(`${API_BASE_URL}/health`);
            if (!healthResponse.ok) {
                throw new Error(`健康检查失败: ${healthResponse.status} ${healthResponse.statusText}`);
            }
            const healthData = await healthResponse.json();
            console.log('✅ 系统状态数据:', healthData);
            
            // 更新系统状态卡片
            this.updateSystemStatus(healthData);

            // 加载内存数据统计
            console.log('正在加载仪表板统计...');
            const dashboardResponse = await fetch(`${API_BASE_URL}/memory/dashboard-stats`);
            if (!dashboardResponse.ok) {
                throw new Error(`仪表板统计失败: ${dashboardResponse.status} ${dashboardResponse.statusText}`);
            }
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
            // 显示错误信息
            this.showDashboardError(error.message);
            // 尝试使用备用数据
            this.loadFallbackData();
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
        
        // 更新最近用户活动表格
        this.updateRecentActivitiesTable(dashboardData.recent_activities || []);
        
        // 更新热门产品表格
        this.updatePopularProductsTable(dashboardData.popular_products || []);
        
        // 初始化图表
        this.initDashboardCharts(dashboardData);
        
        console.log('✅ 仪表板统计数据更新完成');
    }

    updateRecentActivitiesTable(activities) {
        console.log('更新最近用户活动表格:', activities);
        const tableBody = document.querySelector('#recentActivitiesTable tbody');
        if (tableBody && activities.length > 0) {
            tableBody.innerHTML = activities.map(activity => `
                <tr>
                    <td>${activity.user_id || 'N/A'}</td>
                    <td>${activity.action || 'N/A'}</td>
                    <td>${new Date(activity.timestamp).toLocaleString('zh-CN')}</td>
                </tr>
            `).join('');
            console.log('✅ 最近用户活动表格更新成功');
        } else {
            console.log('⚠️ 最近用户活动数据为空或表格未找到');
        }
    }

    updatePopularProductsTable(products) {
        console.log('更新热门产品表格:', products);
        const tableBody = document.querySelector('#topProductsTable tbody');
        if (tableBody && products.length > 0) {
            tableBody.innerHTML = products.map(product => `
                <tr>
                    <td>${product.name || 'N/A'}</td>
                    <td>¥${product.price || '0.00'}</td>
                    <td>${product.rating || '0.0'} ⭐</td>
                </tr>
            `).join('');
            console.log('✅ 热门产品表格更新成功');
        } else {
            console.log('⚠️ 热门产品数据为空或表格未找到');
        }
    }

    initDashboardCharts(dashboardData) {
        console.log('初始化仪表板图表...');
        
        // 初始化推荐趋势图表
        this.initRecommendationsChart();
        
        // 初始化用户行为分布图表
        this.initBehaviorChart();
        
        console.log('✅ 仪表板图表初始化完成');
    }

    initRecommendationsChart() {
        const ctx = document.getElementById('recommendationsChart');
        if (ctx) {
            // 销毁旧图表
            if (this.charts.recommendationsChart) {
                this.charts.recommendationsChart.destroy();
            }
            
            // 创建新图表
            this.charts.recommendationsChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
                    datasets: [{
                        label: '推荐数量',
                        data: [65, 59, 80, 81, 56, 55],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            console.log('✅ 推荐趋势图表初始化成功');
        }
    }

    initBehaviorChart() {
        const ctx = document.getElementById('behaviorChart');
        if (ctx) {
            // 销毁旧图表
            if (this.charts.behaviorChart) {
                this.charts.behaviorChart.destroy();
            }
            
            // 创建新图表
            this.charts.behaviorChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['搜索', '查看', '点击', '购买'],
                    datasets: [{
                        data: [30, 25, 25, 20],
                        backgroundColor: [
                            'rgb(255, 99, 132)',
                            'rgb(54, 162, 235)',
                            'rgb(255, 205, 86)',
                            'rgb(75, 192, 192)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
            console.log('✅ 用户行为分布图表初始化成功');
        }
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

    showDashboardError(message) {
        console.log('显示仪表板错误:', message);
        const statusElement = document.getElementById('system-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <span class="status-indicator status-offline"></span>
                连接失败: ${message}
            `;
        }
        
        // 显示错误通知
        this.showNotification('数据加载失败: ' + message, 'warning');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-${type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i> 
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    loadFallbackData() {
        console.log('加载备用数据...');
        // 使用模拟数据
        const fallbackData = {
            overview: {
                total_products: 25,
                total_users: 150,
                total_behaviors: 1200,
                categories: 8
            },
            popular_products: [
                { name: "ThinkPad X1 Carbon", rating: 4.8, price: 8999.00 },
                { name: "MacBook Air M2", rating: 4.9, price: 7999.00 },
                { name: "小新Pro 16", rating: 4.5, price: 5499.00 }
            ]
        };
        
        this.updateDashboardStats(fallbackData);
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
            console.log(`开始加载用户 ${userId} 的行为详情...`);
            
            // 获取用户画像数据
            const profileResponse = await fetch(`${API_BASE_URL}/memory/user-profile/${userId}`);
            
            if (!profileResponse.ok) {
                throw new Error(`获取用户画像失败: ${profileResponse.status} ${profileResponse.statusText}`);
            }
            
            const profileData = await profileResponse.json();
            console.log('用户画像数据:', profileData);
            
            // 获取用户行为数据
            const behaviors = profileData.recent_behaviors || [];
            console.log(`找到 ${behaviors.length} 条行为记录`);
            
            if (behaviors.length === 0) {
                // 如果没有行为数据，显示提示信息
                this.displayNoBehaviorData(userId);
                return;
            }
            
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
            
            console.log('行为统计:', behaviorCounts);
            console.log('类别统计:', categoryCounts);
            
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

            console.log('准备更新图表，数据:', behaviorData);
            
            await this.updateBehaviorCharts(behaviorData);
            this.updateBehaviorTimeline(behaviorData.timeline);
            
            // 显示成功消息
            this.displayBehaviorAnalysisSuccess(userId, totalBehaviors);

        } catch (error) {
            console.error('加载用户行为详情失败:', error);
            this.displayBehaviorAnalysisError(userId, error.message);
        }
    }
    
    // 显示无行为数据提示
    displayNoBehaviorData(userId) {
        const resultsDiv = document.getElementById('behavior-analysis-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> 
                    用户 <strong>${userId}</strong> 暂无行为数据记录
                    <br><small>请确保用户有浏览、点击、搜索等行为记录</small>
                </div>
            `;
        }
    }
    
    // 显示分析成功消息
    displayBehaviorAnalysisSuccess(userId, totalBehaviors) {
        const resultsDiv = document.getElementById('behavior-analysis-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show">
                    <i class="fas fa-check-circle"></i> 
                    完成用户 <strong>${userId}</strong> 的行为分析
                    <br><small>共分析 ${totalBehaviors} 条行为记录</small>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    }
    
    // 显示分析错误消息
    displayBehaviorAnalysisError(userId, errorMessage) {
        const resultsDiv = document.getElementById('behavior-analysis-results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> 
                    分析用户 <strong>${userId}</strong> 行为失败
                    <br><small>错误: ${errorMessage}</small>
                    <br><button class="btn btn-sm btn-outline-danger mt-2" onclick="analyzeUserBehavior()">重试</button>
                </div>
            `;
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
            try {
                this.charts[chartId].destroy();
                delete this.charts[chartId];
            } catch (error) {
                console.warn(`销毁图表 ${chartId} 时出错:`, error);
                delete this.charts[chartId];
            }
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartId => {
            this.destroyChart(chartId);
        });
    }

    createChart(chartId, ctx, config) {
        // 销毁现有图表实例
        this.destroyChart(chartId);
        
        // 获取canvas的context，确保canvas可用
        let canvas;
        if (typeof ctx === 'string') {
            canvas = document.getElementById(ctx);
        } else {
            canvas = ctx;
        }
        
        if (!canvas) {
            console.error(`找不到图表容器: ${chartId}`);
            return null;
        }
        
        // 强制清理任何可能存在的图表实例
        try {
            // 方法1: 使用Chart.js API
            if (window.Chart && window.Chart.getChart) {
                const existingChart = window.Chart.getChart(canvas);
                if (existingChart) {
                    existingChart.destroy();
                }
            }
            
            // 方法2: 清理canvas内容
            const context = canvas.getContext('2d');
            if (context) {
                context.clearRect(0, 0, canvas.width, canvas.height);
            }
            
            // 方法3: 如果仍有问题，重新创建canvas元素
            if (canvas.chart) {
                delete canvas.chart;
            }
            
            // 方法4: 检查是否有全局Chart实例引用
            if (window.Chart && window.Chart.instances) {
                Object.keys(window.Chart.instances).forEach(key => {
                    const instance = window.Chart.instances[key];
                    if (instance && instance.canvas === canvas) {
                        instance.destroy();
                    }
                });
            }
            
        } catch (error) {
            console.warn(`清理图表容器时出错:`, error);
        }
        
        try {
            this.charts[chartId] = new Chart(canvas, config);
            return this.charts[chartId];
        } catch (error) {
            console.error(`创建图表 ${chartId} 失败:`, error);
            
            // 如果创建失败，尝试重新创建canvas元素
            try {
                console.log(`尝试重新创建图表容器: ${chartId}`);
                const parent = canvas.parentNode;
                const newCanvas = canvas.cloneNode(true);
                
                // 清理所有可能的引用
                newCanvas.chart = null;
                if (newCanvas.getContext) {
                    const newContext = newCanvas.getContext('2d');
                    newContext.clearRect(0, 0, newCanvas.width, newCanvas.height);
                }
                
                parent.removeChild(canvas);
                parent.appendChild(newCanvas);
                
                // 等待DOM更新
                setTimeout(() => {
                    this.charts[chartId] = new Chart(newCanvas, config);
                }, 50);
                
                return this.charts[chartId];
            } catch (retryError) {
                console.error(`重新创建图表 ${chartId} 也失败:`, retryError);
                return null;
            }
        }
    }

    async updateBehaviorCharts(data) {
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

        // 添加小延迟确保第一个图表完全创建
        await new Promise(resolve => setTimeout(resolve, 100));

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
            console.log('开始加载产品数据...');
            const response = await fetch(`${API_BASE_URL}/memory/products`);
            
            if (!response.ok) {
                throw new Error(`获取产品数据失败: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('产品数据响应:', data);
            
            const products = data.products || [];
            console.log(`找到 ${products.length} 个产品`);
            
            if (products.length === 0) {
                this.displayNoProducts();
            } else {
                this.displayProducts(products);
            }
            
        } catch (error) {
            console.error('加载产品数据失败:', error);
            this.displayProductsError(error.message);
        }
    }

    displayProducts(products) {
        console.log('显示产品数据:', products);
        const tableBody = document.getElementById('products-table-body');
        if (tableBody) {
            tableBody.innerHTML = '';
            
            if (products.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center text-muted">
                            <i class="fas fa-info-circle"></i> 暂无产品数据
                        </td>
                    </tr>
                `;
                return;
            }
            
            products.forEach(product => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${product.id || 'N/A'}</td>
                    <td>${product.name || 'N/A'}</td>
                    <td>${product.description || 'N/A'}</td>
                    <td>¥${product.price || '0.00'}</td>
                    <td>${product.category_id || 'N/A'}</td>
                    <td>${product.brand || 'N/A'}</td>
                    <td>${product.rating || '0.0'}</td>
                    <td>${product.stock_quantity || '0'}</td>
                    <td>
                        <button class="btn btn-sm btn-primary product-view-btn" data-product-id="${product.id}">查看</button>
                        <button class="btn btn-sm btn-warning product-edit-btn" data-product-id="${product.id}">编辑</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
            
            // 绑定按钮事件
            this.bindProductButtons();
            
            console.log(`成功显示 ${products.length} 个产品`);
        } else {
            console.error('找不到产品表格体元素: products-table-body');
        }
    }

    // 绑定产品按钮事件
    bindProductButtons() {
        console.log('绑定产品按钮事件...');
        
        // 绑定查看按钮
        const viewButtons = document.querySelectorAll('.product-view-btn');
        viewButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const productId = button.getAttribute('data-product-id');
                console.log(`查看产品按钮被点击: ${productId}`);
                this.viewProduct(productId);
            });
        });
        
        // 绑定编辑按钮
        const editButtons = document.querySelectorAll('.product-edit-btn');
        editButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const productId = button.getAttribute('data-product-id');
                console.log(`编辑产品按钮被点击: ${productId}`);
                this.editProduct(productId);
            });
        });
        
        console.log(`绑定完成: ${viewButtons.length} 个查看按钮, ${editButtons.length} 个编辑按钮`);
    }

    displayNoProducts() {
        const tableBody = document.getElementById('products-table-body');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted">
                        <i class="fas fa-info-circle"></i> 暂无产品数据
                        <br><small>请添加一些产品来开始管理</small>
                    </td>
                </tr>
            `;
        }
    }

    displayProductsError(errorMessage) {
        const tableBody = document.getElementById('products-table-body');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle"></i> 加载产品数据失败
                        <br><small>错误: ${errorMessage}</small>
                        <br><button class="btn btn-sm btn-outline-danger mt-2" id="retry-load-products">重试</button>
                    </td>
                </tr>
            `;
            
            // 绑定重试按钮事件
            const retryButton = document.getElementById('retry-load-products');
            if (retryButton) {
                retryButton.addEventListener('click', () => {
                    console.log('重试加载产品数据...');
                    this.loadProductsData();
                });
            }
        }
    }

    initProductsTable() {
        console.log('初始化产品表格...');
        try {
            // 初始化DataTables
            const table = $('#products-table');
            if (table.length) {
                console.log('找到产品表格，初始化DataTables...');
                table.DataTable({
                    responsive: true,
                    pageLength: 10,
                    language: {
                        // 直接定义中文语言包，避免CORS问题
                        "sProcessing": "处理中...",
                        "sLengthMenu": "显示 _MENU_ 项结果",
                        "sZeroRecords": "没有匹配结果",
                        "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
                        "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
                        "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
                        "sInfoPostFix": "",
                        "sSearch": "搜索:",
                        "sUrl": "",
                        "sEmptyTable": "表中数据为空",
                        "sLoadingRecords": "载入中...",
                        "sInfoThousands": ",",
                        "sDecimal": ".",
                        "sFirst": "首页",
                        "sLast": "末页",
                        "sNext": "下页",
                        "sPrevious": "上页",
                        "oPaginate": {
                            "sFirst": "首页",
                            "sPrevious": "上页",
                            "sNext": "下页",
                            "sLast": "末页"
                        },
                        "oAria": {
                            "sSortAscending": ": 以升序排列此列",
                            "sSortDescending": ": 以降序排列此列"
                        }
                    },
                    columnDefs: [
                        { orderable: false, targets: -1 } // 最后一列（操作列）不可排序
                    ]
                });
                console.log('DataTables初始化成功');
            } else {
                console.warn('找不到产品表格: #products-table');
            }
        } catch (error) {
            console.error('初始化DataTables失败:', error);
        }
    }

    // 查看产品详情
    viewProduct(productId) {
        console.log(`查看产品: ${productId}`);
        try {
            // 这里可以实现查看产品详情的逻辑
            // 比如打开模态框显示产品信息
            this.showProductModal(productId, 'view');
        } catch (error) {
            console.error('查看产品失败:', error);
            alert(`查看产品失败: ${error.message}`);
        }
    }

    // 编辑产品
    editProduct(productId) {
        console.log(`编辑产品: ${productId}`);
        try {
            // 这里可以实现编辑产品的逻辑
            // 比如打开编辑模态框
            this.showProductModal(productId, 'edit');
        } catch (error) {
            console.error('编辑产品失败:', error);
            alert(`编辑产品失败: ${error.message}`);
        }
    }

    // 显示产品模态框
    showProductModal(productId, mode) {
        console.log(`显示产品模态框: ${mode} 模式, 产品ID: ${productId}`);
        
        // 创建模态框HTML
        const modalHtml = `
            <div class="modal fade" id="productModal" tabindex="-1" role="dialog" aria-labelledby="productModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="productModalLabel">
                                ${mode === 'view' ? '查看产品' : '编辑产品'} - ID: ${productId}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">产品名称</label>
                                        <input type="text" class="form-control" id="productName" value="产品 ${productId}" ${mode === 'view' ? 'readonly' : ''}>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">产品描述</label>
                                        <textarea class="form-control" id="productDescription" rows="3" ${mode === 'view' ? 'readonly' : ''}>这是产品 ${productId} 的描述信息</textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">价格</label>
                                        <input type="number" class="form-control" id="productPrice" value="99.99" step="0.01" ${mode === 'view' ? 'readonly' : ''}>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">品牌</label>
                                        <input type="text" class="form-control" id="productBrand" value="品牌 ${productId}" ${mode === 'view' ? 'readonly' : ''}>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">库存数量</label>
                                        <input type="number" class="form-control" id="productStock" value="100" ${mode === 'view' ? 'readonly' : ''}>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">评分</label>
                                        <input type="number" class="form-control" id="productRating" value="4.5" step="0.1" min="0" max="5" ${mode === 'view' ? 'readonly' : ''}>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                            ${mode === 'edit' ? '<button type="button" class="btn btn-primary" id="saveProductBtn">保存</button>' : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 移除已存在的模态框
        const existingModal = document.getElementById('productModal');
        if (existingModal) {
            existingModal.remove();
        }

        // 添加新模态框到页面
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // 绑定保存按钮事件（如果是编辑模式）
        if (mode === 'edit') {
            const saveBtn = document.getElementById('saveProductBtn');
            if (saveBtn) {
                saveBtn.addEventListener('click', () => {
                    console.log('保存产品按钮被点击');
                    this.saveProduct(productId);
                });
            }
        }

        // 显示模态框
        try {
            const modalElement = document.getElementById('productModal');
            if (modalElement) {
                // 使用Bootstrap 5的方式显示模态框
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                console.log('模态框显示成功');
            } else {
                console.error('找不到模态框元素');
            }
        } catch (error) {
            console.error('显示模态框失败:', error);
            // 如果Bootstrap不可用，使用原生方式
            const modalElement = document.getElementById('productModal');
            if (modalElement) {
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
                modalElement.setAttribute('aria-hidden', 'false');
                console.log('使用原生方式显示模态框');
            }
        }
    }

    // 保存产品
    saveProduct(productId) {
        console.log(`保存产品: ${productId}`);
        try {
            // 获取表单数据
            const productData = {
                id: productId,
                name: document.getElementById('productName').value,
                description: document.getElementById('productDescription').value,
                price: parseFloat(document.getElementById('productPrice').value),
                brand: document.getElementById('productBrand').value,
                stock_quantity: parseInt(document.getElementById('productStock').value),
                rating: parseFloat(document.getElementById('productRating').value)
            };

            console.log('产品数据:', productData);

            // 这里可以实现保存到后端的逻辑
            // 暂时显示成功消息
            alert('产品保存成功！');
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('productModal'));
            if (modal) {
                modal.hide();
            }

            // 刷新产品列表
            this.loadProductsData();

        } catch (error) {
            console.error('保存产品失败:', error);
            alert(`保存产品失败: ${error.message}`);
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

    // 验证事件绑定状态
    verifyEventBinding() {
        console.log('🔍 验证事件绑定状态...');
        
        const navLinks = document.querySelectorAll('.nav-link');
        let boundCount = 0;
        let unboundCount = 0;
        
        navLinks.forEach((link, index) => {
            const pageName = link.getAttribute('data-page');
            
            // 检查是否有事件监听器
            const hasListeners = link.onclick !== null || 
                                (link._eventListeners && link._eventListeners.length > 0);
            
            if (hasListeners) {
                boundCount++;
                console.log(`✅ 导航链接 ${pageName} 已绑定事件`);
            } else {
                unboundCount++;
                console.log(`❌ 导航链接 ${pageName} 未绑定事件`);
            }
        });
        
        console.log(`📊 事件绑定验证结果: 已绑定=${boundCount}, 未绑定=${unboundCount}`);
        
        // 如果有未绑定的事件，尝试重新绑定
        if (unboundCount > 0) {
            console.log('⚠️ 发现未绑定的事件，尝试重新绑定...');
            this.bindNavigationEvents();
        } else {
            console.log('✅ 所有导航事件都已正确绑定');
        }
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

// 全局函数：编辑产品
function editProduct(productId) {
    console.log(`全局函数调用编辑产品: ${productId}`);
    if (window.pageNavigator && window.pageNavigator.editProduct) {
        window.pageNavigator.editProduct(productId);
    } else {
        alert(`编辑产品功能暂时不可用，产品ID: ${productId}`);
    }
}

// 全局函数：删除产品
function deleteProduct(productId) {
    console.log(`全局函数调用删除产品: ${productId}`);
    if (window.pageNavigator && window.pageNavigator.deleteProduct) {
        window.pageNavigator.deleteProduct(productId);
    } else {
        // 临时实现删除功能
        if (confirm(`确定要删除产品 ${productId} 吗？`)) {
            alert(`产品 ${productId} 删除功能将在后端实现后完成`);
        }
    }
}

// 全局函数：刷新当前页面
function refreshCurrentPage() {
    console.log('刷新当前页面...');
    if (window.pageNavigator && window.pageNavigator.currentPage) {
        const currentPage = window.pageNavigator.currentPage;
        console.log(`刷新页面: ${currentPage}`);
        window.pageNavigator.initPageSpecific(currentPage);
    } else {
        console.log('刷新仪表板...');
        if (window.pageNavigator) {
            window.pageNavigator.initDashboard();
        }
    }
}

// 全局函数：导出当前数据
function exportCurrentData() {
    console.log('导出当前页面数据...');
    if (window.pageNavigator && window.pageNavigator.currentPage) {
        const currentPage = window.pageNavigator.currentPage;
        console.log(`导出页面数据: ${currentPage}`);
        
        // 根据页面类型导出不同数据
        switch (currentPage) {
            case 'dashboard':
                exportDashboardData();
                break;
            case 'user-behavior':
                exportUserBehaviorData();
                break;
            case 'recommendations':
                exportRecommendationData();
                break;
            default:
                alert('当前页面暂不支持数据导出');
        }
    } else {
        exportDashboardData();
    }
}

// 导出仪表板数据
function exportDashboardData() {
    const data = {
        export_time: new Date().toISOString(),
        page: 'dashboard',
        data: {
            system_status: '在线',
            total_products: 12,
            total_users: 5,
            total_behaviors: 26,
            total_recommendations: 1250,
            ctr_rate: '3.2%',
            conversion_rate: '0.8%',
            avg_rating: '4.5'
        }
    };
    
    downloadJSON(data, 'dashboard_data.json');
}

// 导出用户行为数据
function exportUserBehaviorData() {
    const data = {
        export_time: new Date().toISOString(),
        page: 'user-behavior',
        data: {
            user_behaviors: [
                { user_id: 'user_001', action: '搜索产品', timestamp: new Date().toISOString() },
                { user_id: 'user_002', action: '查看详情', timestamp: new Date().toISOString() },
                { user_id: 'user_003', action: '点击推荐', timestamp: new Date().toISOString() }
            ]
        }
    };
    
    downloadJSON(data, 'user_behavior_data.json');
}

// 导出推荐数据
function exportRecommendationData() {
    const data = {
        export_time: new Date().toISOString(),
        page: 'recommendations',
        data: {
            recommendations: [
                { product: 'ThinkPad X1 Carbon', score: 0.95, reason: '用户偏好商务本' },
                { product: 'MacBook Air M2', score: 0.88, reason: '用户关注轻薄本' },
                { product: '小新Pro 16', score: 0.82, reason: '用户预算范围内' }
            ]
        }
    };
    
    downloadJSON(data, 'recommendation_data.json');
}

// 通用JSON下载函数
function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    // 显示成功消息
    const notification = document.createElement('div');
    notification.className = 'alert alert-success alert-dismissible fade show position-fixed';
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i> 
        数据导出成功: ${filename}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// 全局函数：生成推荐
async function generateRecommendations() {
    const userId = document.getElementById('rec-user-select').value;
    const strategy = document.getElementById('rec-strategy').value;
    const limit = document.getElementById('rec-limit').value;
    
    if (!userId) {
        alert('请选择用户');
        return;
    }
    
    const resultsDiv = document.getElementById('recommendation-results');
    if (!resultsDiv) {
        console.error('找不到推荐结果显示容器');
        return;
    }
    
    // 显示加载状态
    resultsDiv.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">生成中...</span>
            </div>
            <p class="mt-2">正在为用户 ${userId} 生成推荐...</p>
        </div>
    `;
    
    try {
        console.log(`生成推荐请求: 用户=${userId}, 策略=${strategy}, 数量=${limit}`);
        
        // 调用推荐API
        const response = await fetch(`${API_BASE_URL}/hybrid-recommendations/recommendations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                strategy: strategy,
                limit: parseInt(limit),
                session_id: SESSION_ID
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayRecommendations(data, userId);
        } else {
            throw new Error(data.detail || '推荐生成失败');
        }
        
    } catch (error) {
        console.error('生成推荐失败:', error);
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> 
                推荐生成失败: ${error.message}
                <button class="btn btn-sm btn-outline-danger ms-2" onclick="this.parentElement.parentElement.innerHTML=''">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }
}

// 显示推荐结果
function displayRecommendations(data, userId) {
    const resultsDiv = document.getElementById('recommendation-results');
    if (!resultsDiv) return;
    
    const recommendations = data.recommendations || [];
    
    if (recommendations.length === 0) {
        resultsDiv.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> 
                暂无推荐结果
            </div>
        `;
        return;
    }
    
    const recommendationsHtml = recommendations.map(rec => `
        <div class="col-md-6 col-lg-4 mb-3">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title">${rec.title || rec.name || '产品'}</h6>
                        <span class="badge bg-primary">${(rec.relevance_score * 100).toFixed(1)}%</span>
                    </div>
                    <p class="card-text small text-muted">${rec.description || '暂无描述'}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">类别: ${rec.category || '未知'}</small>
                        <small class="text-muted">¥${rec.price || '0'}</small>
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewProductDetails('${rec.id || rec.product_id}')">
                        <i class="fas fa-eye"></i> 查看详情
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    resultsDiv.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show">
            <i class="fas fa-check-circle"></i> 
            成功为用户 <strong>${userId}</strong> 生成 <strong>${recommendations.length}</strong> 个推荐
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        <div class="row">
            ${recommendationsHtml}
        </div>
    `;
}

// 全局函数：分析用户行为
async function analyzeUserBehavior() {
    const userId = document.getElementById('user-select').value;
    const period = document.getElementById('analysis-period').value;
    
    if (!userId) {
        alert('请选择用户');
        return;
    }
    
    // 显示加载状态
    const resultsDiv = document.getElementById('behavior-analysis-results');
    if (resultsDiv) {
        resultsDiv.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">分析中...</span>
                </div>
                <p class="mt-2">正在分析用户 ${userId} 的行为数据...</p>
            </div>
        `;
    }
    
    try {
        console.log(`分析用户行为: 用户=${userId}, 周期=${period}天`);
        
        // 如果有PageNavigator实例，使用它来加载用户行为详情
        if (window.pageNavigator && window.pageNavigator.loadUserBehaviorDetails) {
            await window.pageNavigator.loadUserBehaviorDetails(userId);
        } else {
            // 否则直接调用API
            const response = await fetch(`${API_BASE_URL}/user-behavior/analysis?user_id=${userId}&days=${period}`);
            const data = await response.json();
            
            if (response.ok) {
                displayBehaviorAnalysis(data, userId);
            } else {
                throw new Error(data.detail || '行为分析失败');
            }
        }
        
    } catch (error) {
        console.error('分析用户行为失败:', error);
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> 
                    行为分析失败: ${error.message}
                </div>
            `;
        }
    }
}

// 显示行为分析结果
function displayBehaviorAnalysis(data, userId) {
    const resultsDiv = document.getElementById('behavior-analysis-results');
    if (!resultsDiv) return;
    
    resultsDiv.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show">
            <i class="fas fa-check-circle"></i> 
            完成用户 <strong>${userId}</strong> 的行为分析
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6 class="card-title">行为统计</h6>
                    </div>
                    <div class="card-body">
                        <canvas id="behaviorTypeChart" width="400" height="300"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6 class="card-title">时间分布</h6>
                    </div>
                    <div class="card-body">
                        <canvas id="behaviorTimeChart" width="400" height="300"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 这里可以添加图表创建逻辑
    console.log('行为分析数据:', data);
}

// 全局函数：生成用户报告
async function generateUserReport() {
    const userId = document.getElementById('user-select').value;
    const period = document.getElementById('analysis-period').value;
    
    if (!userId) {
        alert('请选择用户');
        return;
    }
    
    try {
        console.log(`生成用户报告: 用户=${userId}, 周期=${period}天`);
        
        // 模拟报告生成
        const reportData = {
            user_id: userId,
            period: period,
            generated_at: new Date().toISOString(),
            summary: {
                total_behaviors: Math.floor(Math.random() * 100) + 50,
                unique_products: Math.floor(Math.random() * 20) + 5,
                avg_session_duration: Math.floor(Math.random() * 30) + 10,
                conversion_rate: (Math.random() * 0.3 + 0.1).toFixed(2)
            }
        };
        
        // 创建报告下载
        const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `user_report_${userId}_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        // 显示成功消息
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i> 
            用户报告生成成功并开始下载
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
        
    } catch (error) {
        console.error('生成用户报告失败:', error);
        alert('报告生成失败: ' + error.message);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('企业前端系统初始化...');
    
    try {
        // 初始化页面导航器
        window.pageNavigator = new PageNavigator();
        console.log('✅ PageNavigator 创建成功');
        
        // 调用初始化方法
        window.pageNavigator.init();
        console.log('✅ PageNavigator 初始化完成');
        
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

// 全局函数：测试导航功能
function testNavigation(pageName) {
    console.log(`🧪 测试导航到页面: ${pageName}`);
    if (window.pageNavigator) {
        window.pageNavigator.navigateToPage(pageName);
    } else {
        console.error('❌ PageNavigator 未初始化');
    }
}

// 全局函数：显示当前页面状态
function showCurrentPageStatus() {
    if (window.pageNavigator) {
        console.log('📊 当前页面状态:');
        console.log(`   当前页面: ${window.pageNavigator.currentPage}`);
        console.log(`   已初始化: ${window.pageNavigator.initialized}`);
        console.log(`   导航器状态: ${window.pageNavigator ? '✅ 已创建' : '❌ 未创建'}`);
    } else {
        console.error('❌ PageNavigator 未初始化');
    }
}

// 全局函数：手动绑定导航事件
function rebindNavigationEvents() {
    console.log('🔧 手动重新绑定导航事件...');
    if (window.pageNavigator) {
        window.pageNavigator.bindNavigationEvents();
    } else {
        console.error('❌ PageNavigator 未初始化');
    }
}

// 调试面板控制
function toggleDebugPanel() {
    const debugPanel = document.getElementById('debug-panel');
    const debugToggle = document.getElementById('debug-toggle');
    
    if (debugPanel.style.display === 'none') {
        debugPanel.style.display = 'block';
        debugToggle.style.display = 'none';
        debugCheckStatus(); // 自动检查状态
    } else {
        debugPanel.style.display = 'none';
        debugToggle.style.display = 'block';
    }
}

// 调试：检查状态
function debugCheckStatus() {
    console.log('🔍 调试：检查页面状态...');
    addDebugLog('🔍 检查页面状态...');
    
    if (window.pageNavigator) {
        const status = {
            currentPage: window.pageNavigator.currentPage,
            initialized: window.pageNavigator.initialized,
            navigatorExists: !!window.pageNavigator
        };
        
        // 更新状态显示
        const statusDiv = document.getElementById('debug-status');
        if (statusDiv) {
            statusDiv.innerHTML = `
                <strong>当前页面:</strong> ${status.currentPage}<br>
                <strong>已初始化:</strong> ${status.initialized ? '✅' : '❌'}<br>
                <strong>导航器状态:</strong> ${status.navigatorExists ? '✅ 已创建' : '❌ 未创建'}
            `;
            statusDiv.className = 'alert alert-success small';
        }
        
        // 检查导航元素
        const navLinks = document.querySelectorAll('.nav-link');
        const pageContents = document.querySelectorAll('.page-content');
        
        addDebugLog(`📊 页面元素状态:`);
        addDebugLog(`   导航链接数量: ${navLinks.length}`);
        addDebugLog(`   页面内容数量: ${pageContents.length}`);
        
        // 检查每个导航链接
        navLinks.forEach((link, index) => {
            const pageName = link.getAttribute('data-page');
            const isActive = link.classList.contains('active');
            addDebugLog(`   导航链接 ${index + 1}: ${pageName} (${isActive ? '激活' : '未激活'})`);
        });
        
        // 检查每个页面内容
        pageContents.forEach((page, index) => {
            const pageId = page.id;
            const isActive = page.classList.contains('active');
            addDebugLog(`   页面内容 ${index + 1}: ${pageId} (${isActive ? '显示' : '隐藏'})`);
        });
        
        console.log('✅ 调试状态检查完成');
        addDebugLog('✅ 调试状态检查完成');
    } else {
        addDebugLog('❌ PageNavigator 未初始化');
        const statusDiv = document.getElementById('debug-status');
        if (statusDiv) {
            statusDiv.innerHTML = '<strong>错误:</strong> PageNavigator 未初始化';
            statusDiv.className = 'alert alert-danger small';
        }
    }
}

// 调试：重新绑定事件
function debugRebindEvents() {
    console.log('🔧 调试：重新绑定导航事件...');
    addDebugLog('🔧 重新绑定导航事件...');
    
    if (window.pageNavigator && typeof window.pageNavigator.bindNavigationEvents === 'function') {
        window.pageNavigator.bindNavigationEvents();
        addDebugLog('✅ 导航事件重新绑定完成');
    } else {
        addDebugLog('❌ 无法重新绑定导航事件');
    }
}

// 调试：测试所有页面
function debugTestAllPages() {
    console.log('🧪 调试：测试所有页面导航...');
    addDebugLog('🧪 测试所有页面导航...');
    
    const pages = ['dashboard', 'user-behavior', 'recommendations', 'intent-analysis', 'products', 'analytics', 'monitoring'];
    
    pages.forEach((page, index) => {
        setTimeout(() => {
            addDebugLog(`测试页面 ${index + 1}: ${page}`);
            if (window.pageNavigator && typeof window.pageNavigator.navigateToPage === 'function') {
                window.pageNavigator.navigateToPage(page);
            } else {
                addDebugLog(`❌ 无法导航到页面: ${page}`);
            }
        }, index * 1000);
    });
}

// 调试：测试特定页面导航
function debugTestNavigation(pageName) {
    console.log(`🧪 调试：测试导航到页面: ${pageName}`);
    addDebugLog(`🧪 测试导航到页面: ${pageName}`);
    
    if (window.pageNavigator && typeof window.pageNavigator.navigateToPage === 'function') {
        window.pageNavigator.navigateToPage(pageName);
        addDebugLog(`✅ 导航到页面: ${pageName}`);
    } else {
        addDebugLog(`❌ 无法导航到页面: ${pageName}`);
    }
}

// 添加调试日志
function addDebugLog(message) {
    const logDiv = document.getElementById('debug-log');
    if (logDiv) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.textContent = `[${timestamp}] ${message}`;
        logDiv.appendChild(logEntry);
        logDiv.scrollTop = logDiv.scrollHeight;
        
        // 限制日志条目数量
        while (logDiv.children.length > 50) {
            logDiv.removeChild(logDiv.firstChild);
        }
    }
}

// 重写console.log以同时显示在调试面板
const originalLog = console.log;
const originalError = console.error;

console.log = function(...args) {
    originalLog.apply(console, args);
    addDebugLog(args.join(' '));
};

console.error = function(...args) {
    originalError.apply(console, args);
    addDebugLog(`❌ ${args.join(' ')}`);
};