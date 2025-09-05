# 👁️ Project Heimdall - AI意图广告引擎

<div align="center">

![Project Heimdall](https://img.shields.io/badge/Project-Heimdall-cyan?style=for-the-badge&logo=probot&logoColor=white)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

**企业级AI意图识别与广告推荐引擎，集成真实大模型、工具调用和会话管理功能。**

[核心特性](#-核心特性) • [快速开始](#-快速开始) • [API核心示例](#-api核心示例) • [深入指南](#️-深入指南) • [贡献](#-贡献指南)

</div>

---

## 🎯 项目概述

Project Heimdall是一个用于洞察用户真实意图并提供精准广告推荐的AI引擎。它集成了通义千问大模型、动态工具调用、持久化会话管理，并封装了从意图分析到混合推荐的全套企业级AI解决方案。

## ✨ 核心特性

### 🤖 AI核心功能
- **🧠 真实大模型**: 集成通义千问API，支持真实对话和意图分析。
- **🔧 动态工具调用**: 完整的工具注册和调用机制。
- **💬 持久化会话**: 基于PostgreSQL，支持多轮对话和历史记录。
- **🎯 精准意图分析**: 深度理解用户真实意图，支持多维度分析。
- **📢 智能推荐引擎**: 基于用户行为的个性化广告和产品推荐，支持混合算法。

### 📊 企业级可观测性
- **📈 结构化日志**: JSON格式日志，支持`request_id`全链路追踪。
- **⏱️ 性能监控**: 内置请求耗时统计。
- **🏥 健康检查**: 提供实时的服务、数据库、缓存健康状态监控。
- **🔍 遥测系统**: 集成Prometheus指标收集与导出。

### 🚀 卓越开发体验
- **🔄 热重载**: 开发模式下，代码变更自动重启。
- **📚 自动API文档**: 开箱即用的Swagger UI和ReDoc。
- **🛡️ 安全基线**: 内置JWT认证、速率限制和输入验证。
- **🌐 自带Web界面**: 提供一个基础的Bootstrap响应式管理界面。

## 🚀 快速开始

### 1. 环境要求
- Python 3.11+
- PostgreSQL 12+ & Redis
- Poetry (推荐) 或 pip

### 2. 安装与配置
```bash
# 克隆项目
git clone https://github.com/your-repo/project-heimdall.git
cd project-heimdall

# 安装依赖
poetry install

# 配置环境变量 (重要！)
cp .env.template .env
# 编辑 .env 文件，填入你的API密钥和数据库连接信息
```

### 3. 启动服务 (Docker)
*本项目为Docker优先设计，一键启动所有服务。*
```bash
docker-compose up -d --build
```
服务启动后，即可开始使用。

### 4. 访问服务
- **API文档:** `http://localhost:8003/docs`
- **健康检查:** `http://localhost:8003/health`
- **Web管理界面:** `http://localhost:8003/`

## 🔬 API核心示例

Heimdall提供了丰富的API，以下是其**核心价值**——“广告意图分析”的调用示例：

```bash
curl -X POST "http://localhost:8003/api/v1/advertising/analyze_intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想买一个适合跑步听音乐的蓝牙耳机，预算800元左右",
    "user_id": "user-abc-123"
  }'
```

> **💡 更多API测试示例**
> 
> 包括工具调用、对话管理、推荐系统等更详细的`curl`示例，请查阅文档： **[`docs/API_EXAMPLES.md`](docs/API_EXAMPLES.md)**。

## 🛠️ 深入指南

### 项目结构
```
project-heimdall/
├── src/heimdall/              # 主要应用代码
│   ├── api/                   # API层 (FastAPI Routers)
│   ├── core/                  # 核心功能 (配置, DI容器, 安全)
│   ├── models/                # 数据模型 (Pydantic & SQLAlchemy)
│   ├── services/              # 业务服务 (Agent, 推荐引擎)
│   ├── tools/                 # AI工具模块
│   └── main.py                # 主应用入口
├── sql/                       # 数据库迁移与脚本
├── templates/                 # Web界面模板
├── tests/                     # 自动化测试
└── ...
```

### 配置与安全
本项目严格遵守“配置与代码分离”、“敏感信息不上库”的原则。所有关键配置均通过`.env`文件加载。
- **密钥生成:** 请参考`安全注意事项`部分生成安全的`SECRET_KEY`。
- **环境变量:** ` .env.template`中列出了所有可配置项。

### 开发与测试
- **启动/停止:** 根目录提供了`start.bat`和`stop.bat`便捷脚本。
- **日志查看:** 所有日志输出到`logs/`目录，并采用结构化的JSON格式。
- **运行测试:** 我们提供了完整的测试套件，可通过`make test`或相关命令运行。

> 更详细的开发规范、贡献指南和部署说明，请查阅仓库内的相关文档。

## 🤝 贡献指南

我们欢迎社区的贡献！无论是Bug修复、新功能建议还是文档改进，都请随时发起Issue或Pull Request。请遵循仓库中定义的开发规范。

## 📄 开源许可证

本项目基于 **MIT许可证** 开源。详情请见 `LICENSE` 文件。
