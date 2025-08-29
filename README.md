# Project Heimdall - Enterprise AI Intent Advertising Engine

**海姆达尔** - 企业级AI意图识别与广告推荐引擎，集成真实大模型、工具调用和会话管理功能。

## 项目概述

Project Heimdall 是一个用于洞察用户真实意图并提供精准广告推荐的AI引擎。它集成了通义千问大模型、工具调用能力、数据库会话管理系统，为AI应用开发提供完整的解决方案。

## ✨ 核心特性

### 🤖 AI核心功能
- **🧠 真实大模型**: 集成通义千问API，支持真实对话
- **🔧 工具调用**: 完整的工具注册和调用机制
- **💬 会话管理**: PostgreSQL存储，支持多轮对话和历史记录
- **🗄️ 数据持久化**: 智能历史截断，高效会话管理

### 📊 监控与可观测性
- **📈 结构化日志**: JSON格式日志，支持请求ID追踪
- **⏱️ 性能监控**: 请求耗时统计和性能分析
- **🏥 健康检查**: 实时健康状态监控
- **📝 完整审计**: 访问日志和错误日志分离

### 🚀 开发体验
- **🔄 热重载**: 开发模式自动重启
- **📚 API文档**: 自动生成Swagger UI文档
- **🧪 测试接口**: 完整的API测试端点
- **⚡ 异步架构**: 高性能异步处理

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 12+
- 通义千问API密钥

### 安装步骤

1. 创建虚拟环境：
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥和数据库配置
```

4. 初始化数据库：
```bash
# 创建数据库表
psql -d heimdall_db -f sql/001_initial_schema.sql
```

5. 启动服务器：
```bash
# 使用启动脚本（推荐）
start.bat

# 或者手动启动
set PYTHONPATH=src
python enhanced_server.py
```

6. 访问服务：
- API文档: http://localhost:8002/docs
- 健康检查: http://localhost:8002/health
- 获取工具列表: http://localhost:8002/api/v1/tools

## 🚀 服务器管理

### 启动服务器
使用提供的启动脚本自动启动服务器：
```bash
start.bat
```
该脚本会：
- 自动检测并停止已运行的服务器进程
- 激活虚拟环境
- 设置正确的 PYTHONPATH
- 启动增强版服务器（端口8002）

### 停止服务器
使用停止脚本安全关闭服务器：
```bash
stop.bat
```
该脚本会：
- 停止所有相关的 Python 进程
- 释放端口 8002
- 清理资源

## 🧪 API测试

项目提供完整的测试接口：

### 测试大模型对话
```bash
curl -X POST "http://localhost:8002/api/v1/test/llm" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好，请介绍一下自己"}],
    "system_prompt": "你是一个 helpful assistant",
    "session_id": "test_session"
  }'
```

### 测试工具调用
```bash
curl -X POST "http://localhost:8002/api/v1/test/tools" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_current_datetime",
    "tool_args": {}
  }'
```

### 测试完整对话流程
```bash
curl -X POST "http://localhost:8002/api/v1/test/llm-with-tools" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "现在几点了？",
    "session_id": "test_session",
    "system_prompt": "你是一个 helpful assistant"
  }'
```

### 获取可用工具列表
```bash
curl -X GET "http://localhost:8002/api/v1/tools"
```

### 测试广告意图分析
```bash
curl -X POST "http://localhost:8002/api/v1/advertising/analyze_intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想买一个智能手表，预算2000元左右",
    "user_id": "user123"
  }'
```

### 记录用户行为
```bash
curl -X POST "http://localhost:8002/api/v1/advertising/record_behavior" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "session_abc",
    "behavior_type": "search",
    "behavior_data": {
      "query": "智能手表",
      "category": "电子产品"
    }
  }'
```

### 获取广告推荐
```bash
curl -X POST "http://localhost:8002/api/v1/advertising/recommend_ads" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "session_abc",
    "context": {
      "interests": ["电子产品", "健康"],
      "budget": 2000
    }
  }'
```

### 获取分析概览
```bash
curl -X GET "http://localhost:8002/api/v1/advertising/analytics/overview?days=7"
```

## 📁 项目结构

```
project-heimdall/
├── src/heimdall/              # 主要应用代码
│   ├── api/                   # API层
│   │   └── endpoints/         # API端点
│   ├── core/                  # 核心功能
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── logging_config.py  # 日志配置
│   │   └── structured_logging.py # 结构化日志
│   ├── models/                # 数据模型
│   │   └── db_models.py       # 数据库模型
│   ├── services/              # 业务服务
│   │   ├── llm_service.py     # 大模型服务
│   │   └── session_service.py # 会话服务
│   ├── tools/                 # 工具模块
│   │   ├── registry.py        # 工具注册
│   │   ├── general_tools.py   # 通用工具
│   │   └── math_tools.py      # 数学工具
│   └── main.py                # 主应用入口
├── enhanced_server.py         # 增强版服务器
├── tests/                     # 测试文件
├── sql/                       # 数据库迁移
├── logs/                      # 日志文件
├── pyproject.toml             # 项目配置
├── setup.cfg                  # 构建配置
├── requirements.txt           # 依赖列表
├── .env.example              # 环境变量示例
├── logging_config.yaml       # 日志配置
├── docker-compose.yml         # Docker编排
├── start.bat                 # 启动脚本
└── stop.bat                  # 停止脚本
```

## 🔧 配置说明

### 环境变量
复制 `.env.example` 为 `.env` 并配置以下变量：

```bash
# 应用配置
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8002

# 数据库配置
DATABASE_USER=heimdall
DATABASE_PASSWORD=heimdall_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=heimdall_db

# 大模型配置
OPENAI_API_KEY=your_qwen_api_key
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-turbo

# 日志配置
LOGGING__LEVEL=INFO
LOGGING__FORMAT=json
```

### 可用工具

项目内置以下工具：
- **数学计算**: calculate - 支持基本数学运算
- **时间查询**: get_current_datetime - 获取当前时间
- **天气查询**: get_current_weather - 获取天气信息

## 📊 项目状态

**✅ 已完成功能**:
- [x] 通义千问大模型集成
- [x] PostgreSQL会话存储
- [x] 工具注册和调用机制
- [x] 智能历史消息截断
- [x] 结构化日志记录
- [x] 请求ID追踪和监控
- [x] 完整的API测试接口
- [x] 自动化启动脚本

**🔄 当前版本**: v1.0.0

## 🔍 日志查看

### 实时日志
```bash
# 查看应用日志
tail -f logs/app.log

# 查看访问日志
tail -f logs/access.log

# 查看错误日志
tail -f logs/error.log
```

### 日志格式
所有日志采用JSON格式，包含以下字段：
- `timestamp`: 时间戳
- `message`: 日志消息
- `request_id`: 请求ID
- `duration`: 请求耗时（毫秒）
- `level`: 日志级别

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

### 开发规范
- 使用 `black` 和 `ruff` 进行代码格式化
- 遵循类型注解规范
- 编写完整的测试用例
- 更新相关文档

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 支持

- **问题反馈**: [GitHub Issues](https://github.com/your-org/project-heimdall/issues)
- **功能请求**: [GitHub Discussions](https://github.com/your-org/project-heimdall/discussions)

---

**🎯 Project Heimdall** - 让AI开发更智能、更高效！