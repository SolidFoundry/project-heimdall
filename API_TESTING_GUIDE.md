# Project Heimdall API 测试指南

## 📋 测试流程概览

按照真实的业务场景，建议按以下顺序测试接口：

### 1️⃣ 基础测试接口
### 2️⃣ 广告意图分析接口 (核心功能)
### 3️⃣ 用户行为记录接口
### 4️⃣ 广告推荐接口
### 5️⃣ 数据分析接口

---

## 🧪 详细测试步骤

### 第一步：基础健康检查

**目的**：确认服务器正常运行
```bash
# 健康检查
curl -X GET "http://localhost:8002/health"

# 预期响应：
{
  "status": "healthy",
  "timestamp": "2025-08-29T16:15:30.636370",
  "version": "1.0.0",
  "request_id": "..."
}
```

---

### 第二步：获取可用工具列表

**目的**：了解系统支持的工具
```bash
# 获取工具列表
curl -X GET "http://localhost:8002/api/v1/tools"

# 预期响应：
{
  "tools": [
    {
      "name": "calculate",
      "description": "数学计算工具",
      "parameters": {...}
    },
    {
      "name": "get_current_datetime", 
      "description": "获取当前时间",
      "parameters": {...}
    },
    {
      "name": "get_current_weather",
      "description": "获取天气信息", 
      "parameters": {...}
    }
  ],
  "total_count": 3
}
```

---

### 第三步：测试大模型基础对话

**目的**：验证大模型服务是否正常
```bash
# 基础对话测试
curl -X POST "http://localhost:8002/api/v1/test/llm" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好，请介绍一下自己"}
    ],
    "session_id": "test_session_001"
  }'

# 预期响应：
{
  "response": "我是通义千问，是阿里巴巴集团旗下的...",
  "model": "qwen-turbo",
  "timestamp": "...",
  "session_id": "test_session_001"
}
```

---

### 第四步：测试工具调用

**目的**：验证工具注册和调用功能
```bash
# 测试时间工具
curl -X POST "http://localhost:8002/api/v1/test/tools" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_current_datetime",
    "tool_args": {}
  }'

# 预期响应：
{
  "result": "2025-08-29 16:15:30",
  "success": true,
  "tool_name": "get_current_datetime"
}

# 测试数学计算工具
curl -X POST "http://localhost:8002/api/v1/test/tools" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "calculate",
    "tool_args": {"expression": "2 + 2 * 3"}
  }'
```

---

### 第五步：测试完整对话流程（核心）

**目的**：测试大模型+工具调用的完整流程
```bash
# 完整对话测试
curl -X POST "http://localhost:8002/api/v1/test/llm-with-tools" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "现在几点了？请帮我计算一下 15 * 23 等于多少",
    "session_id": "test_session_002"
  }'

# 预期响应：大模型会自动调用工具并整合结果
{
  "final_answer": "现在是2025-08-29 16:15:30，15 * 23 = 345",
  "tool_calls": [
    {
      "tool_name": "get_current_datetime",
      "tool_args": {}
    },
    {
      "tool_name": "calculate", 
      "tool_args": {"expression": "15 * 23"}
    }
  ],
  "execution_steps": [...]
}
```

---

## 🎯 广告引擎核心功能测试

### 第六步：用户意图分析（最重要的接口）

**目的**：分析用户输入，识别购买意图
```bash
# 测试购买意图分析
curl -X POST "http://localhost:8002/api/v1/advertising/analyze_intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想买一个智能手表，预算2000元左右，最好有健康监测功能",
    "user_id": "user_001",
    "session_id": "ad_session_001"
  }'

# 预期响应：
{
  "request_id": "...",
  "user_input": "我想买一个智能手表，预算2000元左右，最好有健康监测功能",
  "detected_intent": "产品购买",
  "intent_confidence": 0.8,
  "target_audience": "有购买智能手表需求的消费者",
  "urgency_level": 0.7,
  "recommended_ads": [...],
  "analysis_summary": "意图类型: 产品购买\n目标受众: ..."
}
```

**更多测试用例：**
```bash
# 信息查询意图
curl -X POST "http://localhost:8002/api/v1/advertising/analyze_intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "请问iPhone 15和iPhone 14有什么区别？",
    "user_id": "user_002"
  }'

# 价格比较意图
curl -X POST "http://localhost:8002/api/v1/advertising/analyze_intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "哪款笔记本电脑性价比更高？预算5000元",
    "user_id": "user_003"
  }'
```

---

### 第七步：记录用户行为

**目的**：记录用户的各种行为，为推荐系统提供数据
```bash
# 记录搜索行为
curl -X POST "http://localhost:8002/api/v1/advertising/record_behavior" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "ad_session_001", 
    "behavior_type": "search",
    "behavior_data": {
      "query": "智能手表",
      "category": "电子产品",
      "price_range": "1000-2000"
    }
  }'

# 记录点击行为
curl -X POST "http://localhost:8002/api/v1/advertising/record_behavior" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "ad_session_001",
    "behavior_type": "click", 
    "behavior_data": {
      "ad_id": "ad_001",
      "product_id": "prod_001",
      "position": 1
    }
  }'

# 记录购买行为
curl -X POST "http://localhost:8002/api/v1/advertising/record_behavior" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "ad_session_001",
    "behavior_type": "purchase",
    "behavior_data": {
      "ad_id": "ad_001", 
      "product_id": "prod_001",
      "amount": 1599,
      "currency": "CNY"
    }
  }'
```

---

### 第八步：获取个性化推荐

**目的**：基于用户画像和行为数据生成推荐
```bash
# 基于兴趣推荐
curl -X POST "http://localhost:8002/api/v1/advertising/recommend_ads" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "session_id": "ad_session_001",
    "context": {
      "interests": ["电子产品", "健康", "运动"],
      "budget": 2000,
      "recent_searches": ["智能手表", "无线耳机"]
    },
    "limit": 3
  }'

# 预期响应：
{
  "recommendations": [
    {
      "ad_id": "ad_001",
      "product_id": "prod_001", 
      "title": "智能手表 Pro",
      "description": "最新款智能手表，健康监测，运动追踪",
      "relevance_score": 0.95,
      "category": "电子产品",
      "price_range": "1000-2000"
    }
  ],
  "total_count": 1
}
```

---

### 第九步：查看数据分析

**目的**：获取广告效果和用户行为分析报告
```bash
# 获取7天分析概览
curl -X GET "http://localhost:8002/api/v1/advertising/analytics/overview"

# 获取30天分析概览
curl -X GET "http://localhost:8002/api/v1/advertising/analytics/overview?days=30"

# 预期响应：
{
  "overview": {
    "period_days": 7,
    "total_impressions": 12500,
    "total_clicks": 342,
    "click_through_rate": 2.74,
    "conversions": 28,
    "conversion_rate": 8.19,
    "revenue": 4560,
    "top_performing_ads": [...],
    "intent_distribution": {
      "产品购买": 45,
      "信息查询": 30,
      "价格比较": 15,
      "售后服务": 10
    }
  }
}
```

---

## 🔄 完整业务流程测试示例

### 场景：用户从搜索到购买的完整流程

```bash
# 1. 用户搜索产品
curl -X POST "http://localhost:8002/api/v1/advertising/record_behavior" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "session_id": "demo_session",
    "behavior_type": "search",
    "behavior_data": {"query": "跑步鞋", "category": "运动用品"}
  }'

# 2. 分析用户意图
curl -X POST "http://localhost:8002/api/v1/advertising/analyze_intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想买一双用于跑步的鞋子，预算500元左右",
    "user_id": "demo_user",
    "session_id": "demo_session"
  }'

# 3. 获取个性化推荐
curl -X POST "http://localhost:8002/api/v1/advertising/recommend_ads" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "session_id": "demo_session",
    "context": {"interests": ["运动", "跑步"], "budget": 500}
  }'

# 4. 记录点击行为
curl -X POST "http://localhost:8002/api/v1/advertising/record_behavior" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user", 
    "session_id": "demo_session",
    "behavior_type": "click",
    "behavior_data": {"ad_id": "ad_005", "product_id": "shoe_001"}
  }'

# 5. 记录购买行为
curl -X POST "http://localhost:8002/api/v1/advertising/record_behavior" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "session_id": "demo_session", 
    "behavior_type": "purchase",
    "behavior_data": {"ad_id": "ad_005", "product_id": "shoe_001", "amount": 459}
  }'

# 6. 查看分析报告
curl -X GET "http://localhost:8002/api/v1/advertising/analytics/overview"
```

---

## 🛠️ 测试技巧

### 1. 使用相同的session_id
```bash
# 在多个请求中使用相同的session_id，可以保持上下文
export SESSION_ID="test_session_$(date +%s)"
```

### 2. 批量测试脚本
创建一个测试脚本文件 `test_api.sh`：
```bash
#!/bin/bash

SESSION_ID="batch_test_$(date +%s)"
USER_ID="test_user_$(date +%s)"

echo "=== 开始批量测试 ==="
echo "Session ID: $SESSION_ID"
echo "User ID: $USER_ID"
echo

# 1. 健康检查
curl -s -X GET "http://localhost:8002/health" | jq '.'
echo

# 2. 意图分析
curl -s -X POST "http://localhost:8002/api/v1/advertising/analyze_intent" \
  -H "Content-Type: application/json" \
  -d "{\"user_input\":\"我想买一个手机\", \"user_id\":\"$USER_ID\", \"session_id\":\"$SESSION_ID\"}" | jq '.'
echo

# 3. 记录行为
curl -s -X POST "http://localhost:8002/api/v1/advertising/record_behavior" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$USER_ID\", \"session_id\":\"$SESSION_ID\", \"behavior_type\":\"search\", \"behavior_data\":{\"query\":\"手机\"}}" | jq '.'
echo

echo "=== 测试完成 ==="
```

### 3. 使用jq工具美化输出
```bash
# 安装jq工具 (如果还没有)
# macOS: brew install jq
# Ubuntu: sudo apt-get install jq

# 在curl命令后添加 | jq '.' 可以美化JSON输出
curl ... | jq '.'
```

---

## 🐛 常见问题

### 1. 服务器未启动
```bash
# 检查服务器状态
curl -X GET "http://localhost:8002/health"

# 如果失败，启动服务器
start.bat
```

### 2. JSON格式错误
```bash
# 使用在线JSON验证工具检查格式
# 确保使用双引号，不要用单引号
# 确保括号匹配
```

### 3. 端口被占用
```bash
# 检查端口占用
netstat -ano | findstr ":8002"

# 停止占用进程
taskkill //F //PID <进程ID>
```

---

## 📊 测试结果验证

### ✅ 成功标志
- 所有HTTP状态码为200
- JSON响应格式正确
- request_id不为空
- 数据符合预期格式

### ⚠️ 注意事项
- 每次测试可以使用不同的session_id避免数据干扰
- 观察日志文件中的详细执行信息
- 测试完成后可以查看分析报告验证数据完整性

按照这个指南，你可以系统地测试Project Heimdall的所有功能！