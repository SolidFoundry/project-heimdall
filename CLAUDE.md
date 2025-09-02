# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Project Heimdall is an enterprise-grade AI intent advertising engine designed to understand user intent and provide precise advertising recommendations. It integrates real large language models (LLMs), tool calling capabilities, session management systems, and supports multiple deployment options.

The codebase includes:

- **Backend API** (`/src/heimdall`): Python FastAPI application with real LLM services and tool calling
- **Test Interfaces** (`/src/heimdall/api/endpoints`): LLM and tool calling test endpoints
- **Database Layer** (`/src/heimdall/core`): SQLAlchemy async database operations and session management
- **SQL Schema** (`/sql`): Standardized database migration files
- **Enhanced Tools** (`/scripts`): Database management, migration, and utility scripts
- **Configuration** (`/config`): Application and logging configuration

## Development Commands

### Server Startup

The project provides multiple startup methods:

#### Recommended: Using Startup Scripts
```bash
# Windows (recommended)
start.bat                          # Auto-start main server (port 8003)
start_server.bat                   # Start server
stop.bat                           # Stop server
open_browser.bat                   # Open browser to access service
start_menu.bat                     # Launch menu

# Linux/Mac
./quick_test.sh                    # Quick test script
```

#### Manual Startup
```bash
# Set environment variable (Windows)
set PYTHONPATH=src

# Start different server versions
python run_server.py              # Start main server (port 8003)
python enhanced_server.py         # Start enhanced server (port 8002)
python src/heimdall/main.py        # Start FastAPI main server
python simple_server.py           # Start simple server (port 8001)
```

#### Docker Startup
```bash
# Using Docker Compose
docker-compose up -d               # Start all services
docker-compose up heimdall         # Start app service only
docker-compose up db               # Start database service only
docker-compose down                # Stop all services
```

### Server Access URLs

After startup, access through these URLs:

- **Main Application**: http://localhost:8003/
- **Enterprise Interface**: http://localhost:8003/enterprise
- **Test Platform**: http://localhost:8003/test
- **API Documentation**: http://localhost:8003/docs
- **Health Check**: http://localhost:8003/health
- **Tools List**: http://localhost:8003/api/v1/tools

### Backend Development

All Python commands require correct PYTHONPATH:

```bash
# Set environment variable (Windows)
set PYTHONPATH=src

# Run tests
python -m pytest tests/           # Run all tests
python -m pytest tests/ -v       # Verbose output
python -m pytest tests/ --cov=src  # Run with coverage

# Code quality checks
python -m ruff check src/         # Check code style
python -m ruff format src/        # Format code
python -m black src/              # Black formatting
python -m mypy src/               # Type checking

# Project management
pip install -e .                  # Install as editable package
pip install -r requirements.txt   # Install dependencies
```

### Database Operations

```bash
# Apply database migrations
psql -d heimdall_db -f sql/001_initial_schema.sql

# Database management scripts
python scripts/migrate_database.py              # Run database migration
python scripts/apply_unified_schema.py          # Apply unified schema
python scripts/reinitialize_database.py         # Reinitialize database
python scripts/unified_database_migration.py   # Unified migration
python scripts/standalone_migrate.py           # Standalone migration
python scripts/init_product_ads_db.py          # Initialize product ads DB

# Database verification
python scripts/check_db_structure.py           # Check DB structure
python scripts/simple_db_check.py              # Simple DB check
python scripts/verify_database_fix.py          # Verify DB fixes
python scripts/final_verification.py           # Final verification

# Database fixes
python scripts/fix_database_step_by_step.py    # Fix DB step by step
python scripts/fix_missing_tables.py           # Fix missing tables
python scripts/fix_data_type_mismatch.py       # Fix data types

# Test data
python scripts/add_test_data.py                # Add test data
python scripts/create_enterprise_data.py       # Create enterprise data

# View logs (logs directory created automatically at runtime)
tail -f logs/app.log              # Application logs
tail -f logs/access.log           # Access logs
```

### Project Utilities

```bash
# Configuration and checks
python check_config.py            # Check configuration
python check_db_schema.py         # Check DB schema
python check_products_table.py    # Check products table
python create_products_table.py   # Create products table
python fix_database.py            # Fix database
python final_verification.py      # Final verification
python generate_fernet_key.py     # Generate Fernet key
python quick_test_enterprise.py   # Quick enterprise test
python run_migration.py           # Run migration

# User management
python scripts/check_user_profiles.py     # Check user profiles

# LLM testing
python scripts/simple_llm_test.py         # Simple LLM test

# Server management
python scripts/restart_server.py          # Restart server
```

## Testing Guide

### Backend Testing

- Use `pytest` for all backend testing
- Test-driven development (TDD) approach recommended
- Test structure: Arrange-Act-Assert

### API Testing

The project provides complete test interfaces supporting multiple scenarios:

#### Basic API Tests
```bash
# Health check
curl -X GET "http://localhost:8003/health"

# Get available tools list
curl -X GET "http://localhost:8003/api/v1/tools"
```

#### LLM Conversation Tests
```bash
# Test basic LLM conversation
curl -X POST "http://localhost:8003/api/v1/test/llm" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好，请介绍一下自己"}],
    "system_prompt": "你是一个 helpful assistant",
    "session_id": "test_session"
  }'

# Test complete conversation flow (with tool calling)
curl -X POST "http://localhost:8003/api/v1/test/llm-with-tools" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "现在几点了？",
    "session_id": "test_session",
    "system_prompt": "你是一个 helpful assistant"
  }'

# Test session management
curl -X POST "http://localhost:8003/api/v1/test/session" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "我叫张三"}], 
    "session_id": "test_session"
  }'
```

#### Tool Calling Tests
```bash
# Test specific tool call
curl -X POST "http://localhost:8003/api/v1/test/tools" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_current_datetime",
    "tool_args": {}
  }'
```

#### Advertising Intent Analysis Tests
```bash
# Test advertising intent analysis
curl -X POST "http://localhost:8003/api/v1/advertising/analyze_intent" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想买一个智能手表，预算2000元左右",
    "user_id": "user123"
  }'

# Record user behavior
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

# Get ad recommendations
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

# Get analytics overview
curl -X GET "http://localhost:8003/api/v1/advertising/analytics/overview?days=7"
```

## Code Style Requirements

### Python

- Use type hints for all functions and class attributes
- Avoid using `Any` type unless absolutely necessary
- Implement special methods appropriately (`__repr__`, `__str__`)
- Use async programming patterns (async/await)

### Database Operations

- Use SQLAlchemy async sessions
- All database operations must be in async context
- Use dependency injection to get database sessions

## Important Notes

- **Environment Variables**: Need to configure `.env` file with database connection info and LLM API keys
- **Comments**: Only write meaningful comments explaining "why", not "what"
- **File Creation**: Prefer editing existing files over creating new ones
- **Documentation**: Do not create documentation files unless explicitly requested
- **Code Quality**: Run code formatting and type checking before committing

## Environment Configuration

### Environment Variable Configuration

The project provides multiple environment configuration templates:

#### Basic Configuration (.env.example)
```bash
# === Database Configuration ===
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password_here
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=heimdall_db

# === LLM Configuration ===
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-3.5-turbo

# === Application Configuration ===
APP_NAME=Project Heimdall
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8001

# === Security Configuration ===
SECRET_KEY=your_secret_key_here_for_jwt
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Enterprise Configuration (.env.enterprise)
```bash
# === Application Configuration ===
ENVIRONMENT=development
DEBUG=true
APP_NAME=heimdall
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8003
WORKERS=1

# === Database Configuration ===
DATABASE_USER=heimdall
DATABASE_PASSWORD=heimdall_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=heimdall_db
DATABASE__POOL_SIZE=20
DATABASE__MAX_OVERFLOW=30
DATABASE__POOL_TIMEOUT=30
DATABASE__POOL_RECYCLE=3600
DATABASE__ECHO=false

# === Redis Configuration ===
REDIS__HOST=localhost
REDIS__PORT=6379
REDIS__DATABASE=0
REDIS__MAX_CONNECTIONS=20
REDIS__TIMEOUT=5

# === External API Configuration ===
OPENAI_API_KEY=your_qwen_api_key_here
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-max

# === Security Configuration ===
SECRET_KEY=your_enterprise_secret_key_here
SECURITY__ALGORITHM=HS256
SECURITY__ACCESS_TOKEN_EXPIRE_MINUTES=30
SECURITY__REFRESH_TOKEN_EXPIRE_DAYS=7
SECURITY__RATE_LIMIT_REQUESTS=100
SECURITY__RATE_LIMIT_WINDOW=60

# === Logging Configuration ===
LOGGING__LEVEL=INFO
LOGGING__FORMAT=json
LOGGING__FILE_PATH=logs/app.log
LOGGING__ENABLE_REQUEST_ID=true
LOGGING__ENABLE_PERFORMANCE_TRACKING=true

# === Monitoring Configuration ===
MONITORING__ENABLE_METRICS=true
MONITORING__METRICS_PORT=8080
MONITORING__ENABLE_TRACING=true
MONITORING__TRACING_SAMPLING_RATE=0.1

# === CORS Configuration ===
SECURITY__CORS_ORIGINS=["http://localhost:3000", "http://localhost:8001", "http://localhost:8003"]
SECURITY__ALLOWED_HOSTS=["localhost", "127.0.0.1"]
```

### Configuration Files

- **Logging Configuration**: `logging_config.yaml` - Detailed log format and handler configuration
- **Project Configuration**: `pyproject.toml` - Modern Python project configuration with build, test, and quality tools
- **Build Configuration**: `setup.cfg` - Traditional build and tool configuration
- **Dependency Management**: `requirements.txt` - Python dependency package list
- **Docker Configuration**: `docker-compose.yml` - Containerized deployment configuration

### Logging Configuration

The project uses structured JSON logging supporting multiple log levels and outputs:

```bash
# View application logs
tail -f logs/app.log

# View access logs
tail -f logs/access.log

# View error logs
tail -f logs/error.log
```

Log format includes:
- `timestamp`: Timestamp
- `message`: Log message
- `request_id`: Request ID
- `duration`: Request duration (milliseconds)
- `level`: Log level
- `module`: Module name

## Architecture Overview

### High-Level Architecture

Project Heimdall follows an enterprise-grade architecture with:

- **Application Factory Pattern**: Uses `create_app()` for modular application construction
- **Dependency Injection**: FastAPI's dependency system throughout
- **Async-First Design**: All I/O operations use async/await patterns
- **Layered Architecture**: Clear separation of concerns (API, Service, Data Access)
- **Enterprise Features**: Monitoring, security, logging, health checks

### Core Infrastructure

The `/src/heimdall/core/` directory contains essential infrastructure:

- `config.py` - Pydantic settings for configuration management
- `config_manager.py` - Advanced configuration management
- `database.py` - SQLAlchemy async database setup
- `logging_config.py` - Structured logging configuration
- `security.py` - JWT, authentication, and security middleware
- `monitoring.py` - Prometheus metrics and monitoring
- `error_handling.py` - Centralized error handling
- `middleware.py` - Custom middleware implementations
- `telemetry.py` - Distributed tracing setup

### Database Architecture

- **PostgreSQL** with SQLAlchemy async ORM
- **Migration-based** schema management (`/sql/` directory)
- **Connection pooling** for performance
- **Soft deletes** and automatic timestamps
- **Intelligent history truncation** for session management

### API Organization

- `/api/v1/test/` - LLM and tool testing endpoints
- `/api/v1/analysis/` - Intent analysis services
- `/api/v1/advertising/` - Advertising recommendations
- `/api/v1/products/` - Product catalog management
- `/api/v1/enterprise/` - Enterprise-grade features
- `/api/v1/hybrid/` - Hybrid recommendation engine

## Common Development Tasks

### Adding New Test Endpoints

1. Create endpoint file in `/src/heimdall/api/endpoints/`
2. Register routes in `/src/heimdall/api/endpoints/__init__.py`
3. Add data models in `/src/heimdall/models/` (if needed)
4. Write tests in `/tests/`

### Adding New Tools

1. Use `@tool` decorator to register tool functions in test interface files
2. Tool functions must be async
3. Provide clear docstrings
4. Tool parameters need type annotations

### Database Migrations

1. Create new migration file in `/sql/` directory (format: `XXX_description.sql`)
2. Update `/sql/README.md` documentation
3. Apply migration files in order

## Available Tools

The project includes built-in tools supporting automatic invocation:

### General Tools
- **Math Calculation**: `calculate` - Supports basic math operations
- **Time Query**: `get_current_datetime` - Get current time
- **Weather Query**: `get_current_weather` - Get weather information

### Advertising Analysis Tools
- **Intent Analysis**: `analyze_user_intent` - Analyze user advertising intent
- **Behavior Recording**: `record_user_behavior` - Record user behavior
- **Ad Recommendations**: `recommend_ads` - Recommend ads based on user interests
- **Analytics Overview**: `get_analytics_overview` - Get analytics data

### Project Structure

```
project-heimdall/
├── src/heimdall/              # Main application code
│   ├── api/                   # API layer
│   │   └── endpoints/         # API endpoints
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection
│   │   ├── logging_config.py  # Logging configuration
│   │   └── structured_logging.py # Structured logging
│   ├── models/                # Data models
│   │   └── db_models.py       # Database models
│   ├── services/              # Business services
│   │   ├── llm_service.py     # LLM service
│   │   └── session_service.py # Session service
│   ├── tools/                 # Tools module
│   │   ├── registry.py        # Tool registry
│   │   ├── general_tools.py   # General tools
│   │   └── math_tools.py      # Math tools
│   └── main.py                # Main application entry
├── enhanced_server.py         # Enhanced server
├── run_server.py              # Main server startup script
├── simple_server.py           # Simple server
├── tests/                     # Test files
├── sql/                       # Database migrations
├── logs/                      # Log files
├── scripts/                   # Utility and management scripts
├── pyproject.toml             # Project configuration
├── setup.cfg                  # Build configuration
├── requirements.txt           # Dependency list
├── .env.example              # Environment variable example
├── .env.enterprise           # Enterprise configuration example
├── logging_config.yaml       # Logging configuration
├── docker-compose.yml         # Docker orchestration
├── start.bat                 # Windows startup script
├── stop.bat                  # Windows stop script
└── quick_test.sh             # Linux/Mac test script
```

### Startup Script Functionality

#### Windows Scripts
- **start.bat**: Main startup script, auto-detects ports, activates virtual environment, starts server
- **stop.bat**: Stop script, safely closes all related processes and ports
- **start_server.bat**: Server startup script
- **open_browser.bat**: Opens browser to access service
- **start_menu.bat**: Startup menu script

#### Linux/Mac Scripts
- **quick_test.sh**: Quick test script

### Port Configuration

The project uses multiple ports for different services:

- **8001**: Simple server (simple_server.py)
- **8002**: Enhanced server (enhanced_server.py)  
- **8003**: Main server (run_server.py) - Recommended
- **8080**: Monitoring metrics port (optional)
- **5432**: PostgreSQL database port

## Project-Specific Conventions

- **Session Management**: Use database-supported session service with intelligent history truncation
- **Tool Calling**: Integrate OpenAI function calling pattern, support async tool execution
- **Logging System**: Use structured JSON logs with request ID tracking
- **Configuration Management**: Use Pydantic Settings to manage environment variables
- **Error Handling**: Uniformly use HTTPException with appropriate error messages

### Architecture Principles

- **Dependency Injection**: Use FastAPI's dependency injection system
- **Async First**: All I/O operations use async patterns
- **Type Safety**: Strict type checking and hints
- **Test Coverage**: All new features need corresponding tests

### Database Design

- **Table Naming**: Use lowercase letters and underscores (e.g., `chat_sessions`)
- **Index Strategy**: Create appropriate indexes for common query paths
- **Timestamps**: All tables include creation and update times
- **Soft Deletes**: Prefer soft deletes over physical deletes

### Performance Considerations

- **Database Connections**: Use connection pooling to manage database connections
- **History Truncation**: Implement intelligent history message truncation to control memory usage
- **Caching Strategy**: Use caching where appropriate to improve performance
- **Batch Operations**: Prefer batch database operations

## Configuration Files

The project includes these important configuration files:

- **pyproject.toml**: Modern Python project configuration
- **setup.cfg**: Build and tool configuration
- **.editorconfig**: Editor configuration ensuring consistent coding style across editors
- **requirements.txt**: Python dependency package list
- **config/**: Configuration file directory (logging, etc.)