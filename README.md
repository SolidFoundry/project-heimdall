# Project Heimdall - Enterprise AI Intent Advertising Engine

**海姆达尔** - 企业级AI意图识别与广告推荐引擎，集成真实大模型、工具调用和会话管理功能。

## 项目概述

Project Heimdall 是一个用于洞察用户真实意图并提供精准广告推荐的AI引擎。它集成了通义千问大模型、工具调用能力、数据库会话管理系统，为AI应用开发提供完整的解决方案。

## ✨ 核心特性

### 🤖 AI核心功能
- **🧠 真实大模型**: 集成通义千问API，支持真实对话和意图分析
- **🔧 工具调用**: 完整的工具注册和调用机制，支持动态工具执行
- **💬 会话管理**: PostgreSQL存储，支持多轮对话和历史记录
- **🗄️ 数据持久化**: 智能历史截断，高效会话管理
- **🎯 意图分析**: 深度理解用户真实意图，支持多维度分析
- **📢 智能推荐**: 基于用户行为的个性化广告和产品推荐
- **🔄 混合算法**: 结合内容过滤和协同过滤的推荐引擎

### 📊 监控与可观测性
- **📈 结构化日志**: JSON格式日志，支持请求ID追踪
- **⏱️ 性能监控**: 请求耗时统计和性能分析
- **🏥 健康检查**: 实时健康状态监控（数据库、Redis、服务等）
- **📝 完整审计**: 访问日志和错误日志分离
- **🔍 遥测系统**: Prometheus指标收集和导出

### 🚀 开发体验
- **🔄 热重载**: 开发模式自动重启
- **📚 API文档**: 自动生成Swagger UI文档
- **🧪 测试接口**: 完整的API测试端点
- **⚡ 异步架构**: 高性能异步处理
- **🛡️ 企业级安全**: JWT认证、速率限制、输入验证
- **🌐 Web界面**: Bootstrap响应式管理界面

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
python run_server.py
```

6. 访问服务：
- API文档: http://localhost:8003/docs
- 健康检查: http://localhost:8003/health
- 获取工具列表: http://localhost:8003/api/v1/tools
- Web管理界面: http://localhost:8003/

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
- 启动服务器（端口8003）

### 停止服务器
使用停止脚本安全关闭服务器：
```bash
stop.bat
```
该脚本会：
- 停止所有相关的 Python 进程
- 释放端口 8003
- 清理资源

## 🧪 API测试

项目提供完整的测试接口：

### 测试大模型对话
```bash
curl -X POST "http://localhost:8003/api/v1/test/llm" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好，请介绍一下自己"}],
    "system_prompt": "你是一个 helpful assistant",
    "session_id": "test_session"
  }'
```

### 测试工具调用
```bash
curl -X POST "http://localhost:8003/api/v1/test/tools" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_current_datetime",
    "tool_args": {}
  }'
```

### 测试完整对话流程
```bash
curl -X POST "http://localhost:8003/api/v1/test/llm-with-tools" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "现在几点了？",
    "session_id": "test_session",
    "system_prompt": "你是一个 helpful assistant"
  }'
```

### 获取可用工具列表
```bash
curl -X GET "http://localhost:8003/api/v1/tools"
```

### 测试广告意图分析
```bash
curl -X POST "http://localhost:8003/api/v1/advertising/analyze_intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想买一个智能手表，预算2000元左右",
    "user_id": "user123"
  }'
```

### 记录用户行为
```bash
curl -X POST "http://localhost:8003/api/v1/advertising/record_behavior" \
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
curl -X POST "http://localhost:8003/api/v1/advertising/recommend_ads" \
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
curl -X GET "http://localhost:8003/api/v1/advertising/analytics/overview?days=7"
```

### 测试企业级推荐
```bash
curl -X POST "http://localhost:8003/api/v1/enterprise/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "scenario": "电商购物",
    "context": {
      "user_preferences": ["电子产品", "运动"],
      "budget_range": [1000, 3000]
    }
  }'
```

### 测试混合推荐
```bash
curl -X POST "http://localhost:8003/api/v1/hybrid/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "content_based": true,
    "collaborative": true,
    "limit": 10
  }'
```

## 📁 项目结构

```
project-heimdall/
├── src/heimdall/              # 主要应用代码
│   ├── api/                   # API层
│   │   └── endpoints/         # API端点
│   │       ├── advertising.py      # 广告相关API
│   │       ├── enterprise_recommendations.py  # 企业级推荐
│   │       ├── hybrid_recommendations.py       # 混合推荐
│   │       ├── intent_analysis.py      # 意图分析
│   │       ├── products.py             # 产品管理
│   │       └── testing.py              # 测试接口
│   ├── core/                  # 核心功能
│   │   ├── config.py          # 配置管理
│   │   ├── config_manager.py  # 配置管理器
│   │   ├── context.py         # 上下文管理
│   │   ├── database.py        # 数据库连接
│   │   ├── error_handling.py  # 错误处理
│   │   ├── logging_config.py  # 日志配置
│   │   ├── middleware.py      # 中间件
│   │   ├── monitoring.py      # 监控
│   │   ├── security.py        # 安全
│   │   ├── structured_logging.py # 结构化日志
│   │   └── telemetry.py       # 遥测
│   ├── models/                # 数据模型
│   │   ├── db_models.py       # 数据库模型
│   │   └── schemas.py         # Pydantic模型
│   ├── services/              # 业务服务
│   │   ├── advertising_service.py         # 广告服务
│   │   ├── hybrid_recommendation_engine.py # 混合推荐引擎
│   │   ├── llm_service.py     # 大模型服务
│   │   ├── memory_data_provider.py        # 数据提供者
│   │   ├── recommendation_engine.py       # 推荐引擎
│   │   └── session_service.py # 会话服务
│   ├── tools/                 # 工具模块
│   │   ├── advertising_tools.py       # 广告工具
│   │   ├── general_tools.py   # 通用工具
│   │   ├── math_tools.py      # 数学工具
│   │   └── registry.py        # 工具注册
│   └── main.py                # 主应用入口
├── run_server.py              # 服务器运行脚本
├── tests/                     # 测试文件
├── sql/                       # 数据库迁移
├── templates/                 # Web模板
│   ├── enterprise.html        # 企业管理界面
│   ├── home.html              # 首页
│   └── index.html             # 测试界面
├── static/                    # 静态资源
├── logs/                      # 日志文件
├── pyproject.toml             # 项目配置
├── requirements.txt           # 依赖列表
├── .env.template             # 环境变量模板
├── logging_config.yaml       # 日志配置
├── docker-compose.yml         # Docker编排
├── start.bat                 # 启动脚本
└── stop.bat                  # 停止脚本
```

## 🔧 配置说明

### 环境变量
复制 `.env.template` 为 `.env` 并配置以下变量：

```bash
# 应用配置
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8003

# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/heimdall_db

# 大模型配置（通义千问）
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-max

# 安全配置
SECRET_KEY=your_generated_secret_key_min_32_chars
ENCRYPTION_KEY=your_generated_encryption_key

# Redis配置（用于速率限制）
REDIS_URL=redis://localhost:6379

# 日志配置
LOGGING__LEVEL=INFO
LOGGING__FORMAT=json

# CORS配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### 🔒 安全注意事项

**重要：** 本项目不包含任何硬编码的敏感信息。所有敏感配置都必须通过环境变量设置：

1. **环境变量文件**
   - `.env` 文件包含敏感信息，已添加到 `.gitignore`
   - 使用 `.env.template` 作为配置模板
   - 永远不要将 `.env` 文件提交到版本控制系统

2. **密钥生成**
   ```bash
   # 生成 JWT 密钥（至少32字符）
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # 生成 Fernet 加密密钥
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

3. **数据库安全**
   - 使用强密码
   - 生产环境不要使用默认用户名
   - 定期更新密码

4. **API 密钥**
   - 从官方平台获取真实的 API 密钥
   - 定期轮换密钥
   - 使用最小权限原则

### 可用工具

项目内置以下工具：
- **数学计算**: calculate - 支持基本数学运算
- **时间查询**: get_current_datetime - 获取当前时间
- **天气查询**: get_current_weather - 获取天气信息
- **广告工具**: 广告分析、用户行为记录、推荐生成

## 📊 项目状态

**✅ 已完成功能**:
- [x] 通义千问大模型集成
- [x] PostgreSQL异步数据库支持
- [x] 工具注册和调用机制
- [x] 智能历史消息截断
- [x] 结构化JSON日志记录
- [x] 请求ID追踪和监控
- [x] 完整的API测试接口
- [x] 自动化启动脚本
- [x] 意图分析功能
- [x] 广告推荐引擎
- [x] 企业级推荐系统
- [x] 混合推荐算法
- [x] JWT认证和授权
- [x] 速率限制和安全防护
- [x] 健康检查和遥测
- [x] 响应式Web管理界面
- [x] Redis缓存支持

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
- **所有代码注释必须使用中文**
- **所有日志输出必须使用中文**
- **所有文档字符串必须使用中文**

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 支持

- **问题反馈**: [GitHub Issues](https://github.com/your-org/project-heimdall/issues)
- **功能请求**: [GitHub Discussions](https://github.com/your-org/project-heimdall/discussions)

---

**🎯 Project Heimdall** - 让AI开发更智能、更高效！