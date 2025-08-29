# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中处理代码时提供指导。

## 项目概述

Project Heimdall 是一个AI意图广告引擎原型，专门用于洞察用户意图并提供精准广告推荐。该平台集成了大模型测试接口、工具调用能力、会话管理系统和MCP（Model Context Protocol）集成。

代码库包含：

- **后端API** (`/src/heimdall`): Python FastAPI 应用，集成了真实LLM服务和工具调用
- **测试接口** (`/src/heimdall/api/endpoints`): 大模型和工具调用测试接口
- **数据库层** (`/src/heimdall/core`): SQLAlchemy异步数据库操作和会话管理
- **SQL架构** (`/sql`): 标准化的数据库迁移文件
- **MCP集成** (`.mcp.json`): Model Context Protocol服务器配置
- **增强工具** (`/scripts`): MCP增强的开发和测试工具
- **配置管理** (`/config`): 应用配置和日志配置

## 开发命令

### 后端API

所有Python命令需要设置正确的PYTHONPATH：

```bash
# 设置环境变量 (Windows)
set PYTHONPATH=src

# 启动开发服务器
python src/heimdall/main.py      # 启动主服务器
python src/heimdall/simple_main.py  # 启动简化版服务器

# 运行测试
python -m pytest tests/           # 运行所有测试
python -m pytest tests/ -v       # 详细输出
python -m pytest tests/ --cov=src  # 带覆盖率测试

# 代码质量检查
python -m ruff check src/         # 检查代码规范
python -m ruff format src/        # 格式化代码
python -m black src/              # Black格式化
python -m mypy src/               # 类型检查
```

### MCP增强工具

```bash
# 运行MCP增强开发工具
python scripts/mcp_dev_tools.py              # 综合项目分析和开发辅助

# 运行智能代码分析
python scripts/intelligent_code_analyzer.py  # 深度代码分析和质量检查

# 运行数据库集成工具
python scripts/postgres_mcp_integration.py   # 数据库查询和分析

# 运行自动化测试工作流
python scripts/automated_testing_workflow.py # 全面的测试和验证
```

### 数据库操作

```bash
# 应用数据库迁移
psql -d heimdall_db -f sql/001_initial_schema.sql

# 查看日志 (logs目录会在运行时自动创建)
tail -f logs/app.log              # 应用日志
tail -f logs/access.log           # 访问日志
```

## 测试指南

### 后端测试

- 使用 `pytest` 进行所有后端测试
- 推荐测试驱动开发（TDD）方法
- 测试结构：安排-执行-断言（Arrange-Act-Assert）

### 接口测试

```bash
# 测试LLM基础能力
curl -X POST "http://localhost:8001/api/v1/test/llm" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "你好"}]}'

# 测试工具调用
curl -X POST "http://localhost:8001/api/v1/test/tools" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "计算2+2等于多少"}]}'

# 测试会话管理
curl -X POST "http://localhost:8001/api/v1/test/session" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "我叫张三"}], "session_id": "test_session"}'

# 健康检查
curl -X GET "http://localhost:8001/health"
```

## 代码风格要求

### Python

- 为所有函数和类属性使用类型提示
- 除非绝对必要，否则避免使用 `Any` 类型
- 适当实现特殊方法（`__repr__`, `__str__`）
- 使用异步编程模式（async/await）

### 数据库操作

- 使用 SQLAlchemy 异步会话
- 所有数据库操作都要在异步上下文中进行
- 使用依赖注入获取数据库会话

## 重要说明

- **环境变量**: 需要配置 `.env` 文件，包含数据库连接信息和LLM API密钥
- **注释**: 只写有意义的注释，解释"为什么"，而不是"是什么"
- **文件创建**: 优先编辑现有文件而不是创建新文件
- **文档**: 除非明确要求，否则不要创建文档文件
- **代码质量**: 提交前运行代码格式化和类型检查

## 常见开发任务

### 添加新的测试接口

1. 在 `/src/heimdall/api/endpoints/` 中创建端点文件
2. 在 `/src/heimdall/api/endpoints/__init__.py` 中注册路由
3. 在 `/src/heimdall/models/` 中添加数据模型（如需要）
4. 在 `/tests/` 中编写测试

### 添加新工具

1. 在测试接口文件中使用 `@tool` 装饰器注册工具函数
2. 工具函数必须是异步的
3. 提供清晰的文档字符串
4. 工具参数需要有类型注解

### 数据库迁移

1. 在 `/sql/` 目录中创建新的迁移文件（格式：`XXX_description.sql`）
2. 更新 `/sql/README.md` 文档
3. 按顺序应用迁移文件

## 项目特定约定

- **会话管理**: 使用数据库支持的会话服务，支持智能历史截断
- **工具调用**: 集成OpenAI函数调用模式，支持异步工具执行
- **日志系统**: 使用结构化JSON日志，支持请求ID追踪
- **配置管理**: 使用Pydantic Settings管理环境变量
- **错误处理**: 统一使用HTTPException和适当的错误消息

### 架构原则

- **依赖注入**: 使用FastAPI的依赖注入系统
- **异步优先**: 所有I/O操作都使用异步模式
- **类型安全**: 严格的类型检查和提示
- **测试覆盖**: 所有新功能都需要相应的测试

### 数据库设计

- **表命名**: 使用小写字母和下划线（如：`chat_sessions`）
- **索引策略**: 为常用查询路径创建合适的索引
- **时间戳**: 所有表都包含创建时间和更新时间
- **软删除**: 优先使用软删除而非物理删除

### 性能考虑

- **数据库连接**: 使用连接池管理数据库连接
- **历史截断**: 实现智能的历史消息截断以控制内存使用
- **缓存策略**: 在适当的地方使用缓存提高性能
- **批量操作**: 优先使用批量数据库操作

## MCP集成

### Model Context Protocol配置

项目配置了多个MCP服务器以增强AI开发能力：

- **核心工具**: context7, sequential-thinking, github, fetch, filesystem, git
- **数据库服务**: postgres, sqlite, redis
- **开发工具**: puppeteer, brave-search, slack, email
- **通信服务**: 各种第三方API集成

### MCP增强功能

- **智能代码分析**: 自动检测代码异味和安全漏洞
- **数据库集成**: 自动化数据库操作和性能监控
- **测试自动化**: 全面的测试覆盖和性能测试
- **开发工作流**: 自动化的开发流程和报告生成

### 使用MCP工具

所有MCP增强工具都支持命令行直接运行，并提供详细的报告和建议：

```bash
# 运行完整的开发分析
python scripts/mcp_dev_tools.py

# 生成代码质量报告
python scripts/intelligent_code_analyzer.py

# 检查数据库状态
python scripts/postgres_mcp_integration.py

# 执行自动化测试
python scripts/automated_testing_workflow.py
```

## 文档结构

项目包含以下关键文档：

- **CLAUDE.md**: Claude Code开发指南（本文件）
- **AGENTS.md**: AI代理专用指南（内容同CLAUDE.md）
- **PROJECT_STATUS.md**: 项目最新状态和功能概述
- **MCP_INTEGRATION_REPORT.md**: MCP集成完成报告
- **sql/README.md**: 数据库迁移管理指南（中文版）

## 配置文件

项目包含以下重要配置文件：

- **pyproject.toml**: 现代Python项目配置
- **setup.cfg**: 构建和工具配置
- **.editorconfig**: 编辑器配置，确保跨编辑器一致的编码风格
- **.mcp.json**: MCP服务器配置
- **.env.example**: 环境变量示例（需要复制为.env）
- **requirements.txt**: Python依赖包列表
- **config/**: 配置文件目录（日志配置等）