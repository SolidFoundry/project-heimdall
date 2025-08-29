#!/bin/bash

# Project Heimdall API 快速测试脚本
# 使用方法: ./quick_test.sh [session_id]
# 如果没有提供session_id，会自动生成一个

set -e

# 生成或使用提供的session_id
SESSION_ID=${1:-"quick_test_$(date +%s_%N)"}
USER_ID="test_user_$(date +%s)"
BASE_URL="http://localhost:8002"

echo "==============================================="
echo "   Project Heimdall API 快速测试"
echo "==============================================="
echo "Session ID: $SESSION_ID"
echo "User ID: $USER_ID"
echo "Base URL: $BASE_URL"
echo "==============================================="
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试函数
test_api() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    
    echo -e "${BLUE}测试 $name${NC}"
    echo "请求: $method $url"
    
    if [ -n "$data" ]; then
        echo "数据: $data"
        response=$(curl -s -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$url" 2>/dev/null || echo '{"error": "请求失败"}')
    else
        response=$(curl -s -X "$method" "$url" 2>/dev/null || echo '{"error": "请求失败"}')
    fi
    
    # 检查响应是否包含error
    if echo "$response" | grep -q '"error"' || echo "$response" | grep -q '"detail"'; then
        echo -e "${RED}❌ 失败${NC}"
        echo "响应: $response"
    else
        echo -e "${GREEN}✅ 成功${NC}"
        # 显示关键信息
        if echo "$response" | grep -q '"detected_intent"'; then
            intent=$(echo "$response" | grep -o '"detected_intent":"[^"]*"' | cut -d'"' -f4)
            echo -e "${YELLOW}  检测到意图: $intent${NC}"
        fi
        if echo "$response" | grep -q '"total_count"'; then
            count=$(echo "$response" | grep -o '"total_count":[0-9]*' | cut -d':' -f2)
            echo -e "${YELLOW}  推荐数量: $count${NC}"
        fi
        if echo "$response" | grep -q '"status":"healthy"'; then
            echo -e "${YELLOW}  服务器状态: 健康${NC}"
        fi
    fi
    echo "----------------------------------------"
    echo
}

# 开始测试
echo "🚀 开始测试 Project Heimdall API"
echo "==============================================="
echo

# 1. 健康检查
test_api "健康检查" "GET" "$BASE_URL/health" ""

# 2. 获取工具列表
test_api "获取工具列表" "GET" "$BASE_URL/api/v1/tools" ""

# 3. 基础LLM对话
test_api "基础LLM对话" "POST" "$BASE_URL/api/v1/test/llm" \
    "{\"messages\": [{\"role\": \"user\", \"content\": \"你好\"}], \"session_id\": \"$SESSION_ID\"}"

# 4. 工具调用测试
test_api "时间工具测试" "POST" "$BASE_URL/api/v1/test/tools" \
    "{\"tool_name\": \"get_current_datetime\", \"tool_args\": {}}"

# 5. 数学工具测试
test_api "数学工具测试" "POST" "$BASE_URL/api/v1/test/tools" \
    "{\"tool_name\": \"calculate\", \"tool_args\": {\"expression\": \"123 + 456\"}}"

# 6. 完整对话流程测试
test_api "完整对话流程" "POST" "$BASE_URL/api/v1/test/llm-with-tools" \
    "{\"query\": \"现在几点了？请计算 25 * 4 等于多少\", \"session_id\": \"$SESSION_ID\"}"

echo "==============================================="
echo "🎯 广告引擎核心功能测试"
echo "==============================================="
echo

# 7. 用户意图分析测试
test_api "购买意图分析" "POST" "$BASE_URL/api/v1/advertising/analyze_intent" \
    "{\"user_input\": \"我想买一个智能手表，预算2000元\", \"user_id\": \"$USER_ID\", \"session_id\": \"$SESSION_ID\"}"

# 8. 信息查询意图分析
test_api "信息查询意图分析" "POST" "$BASE_URL/api/v1/advertising/analyze_intent" \
    "{\"user_input\": \"请问iPhone 15有什么新功能？\", \"user_id\": \"$USER_ID\", \"session_id\": \"$SESSION_ID\"}"

# 9. 用户行为记录测试
test_api "搜索行为记录" "POST" "$BASE_URL/api/v1/advertising/record_behavior" \
    "{\"user_id\": \"$USER_ID\", \"session_id\": \"$SESSION_ID\", \"behavior_type\": \"search\", \"behavior_data\": {\"query\": \"智能手表\", \"category\": \"电子产品\"}}"

# 10. 点击行为记录
test_api "点击行为记录" "POST" "$BASE_URL/api/v1/advertising/record_behavior" \
    "{\"user_id\": \"$USER_ID\", \"session_id\": \"$SESSION_ID\", \"behavior_type\": \"click\", \"behavior_data\": {\"ad_id\": \"ad_001\", \"product_id\": \"prod_001\"}}"

# 11. 广告推荐测试
test_api "个性化推荐" "POST" "$BASE_URL/api/v1/advertising/recommend_ads" \
    "{\"user_id\": \"$USER_ID\", \"session_id\": \"$SESSION_ID\", \"context\": {\"interests\": [\"电子产品\", \"健康\"], \"budget\": 2000}}"

# 12. 分析概览测试
test_api "分析概览" "GET" "$BASE_URL/api/v1/advertising/analytics/overview" ""

echo "==============================================="
echo "🎉 测试完成！"
echo "==============================================="
echo

# 显示测试统计
echo -e "${GREEN}✅ 已测试 12 个接口${NC}"
echo -e "${BLUE}📋 Session ID: $SESSION_ID${NC}"
echo -e "${BLUE}👤 User ID: $USER_ID${NC}"
echo

# 显示如何查看更多详细信息
echo "🔍 查看详细日志："
echo "   tail -f logs/app.log"
echo "   tail -f logs/access.log"
echo

echo "📖 查看API文档："
echo "   open http://localhost:8002/docs"
echo

echo "🎯 测试特定接口："
echo "   使用此脚本: ./quick_test.sh [session_id]"
echo "   或查看 API_TESTING_GUIDE.md 获取详细测试方法"
echo

# 检查服务器是否正常运行
final_health=$(curl -s "$BASE_URL/health" 2>/dev/null || echo '{"status": "error"}')
if echo "$final_health" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}🎊 服务器运行正常，所有功能可用！${NC}"
else
    echo -e "${RED}⚠️  服务器状态异常，请检查日志${NC}"
fi