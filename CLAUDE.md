# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# Or install with development dependencies
pip install -e ".[dev,test,mcp]"
```

### Running the Application
```bash
# Start the server (recommended)
start.bat

# Manual startup
set PYTHONPATH=src
python run_server.py

# Stop the server
stop.bat
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# Run all quality checks
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_endpoints.py

# Run with verbose output
pytest -v
```

### Database Operations
```bash
# Initialize database schema
psql -d heimdall_db -f sql/001_initial_schema.sql

# The application uses SQLAlchemy with asyncpg for database operations
# Models are defined in src/heimdall/models/db_models.py
```

## Architecture Overview

Project Heimdall is an Enterprise AI Intent Advertising Engine built with FastAPI. The architecture follows a layered pattern with clear separation of concerns:

### Core Components

1. **API Layer** (`src/heimdall/api/`)
   - Endpoints organized by domain (testing, intent_analysis, advertising, etc.)
   - FastAPI routers with automatic OpenAPI documentation
   - Request/response models using Pydantic

2. **Core Infrastructure** (`src/heimdall/core/`)
   - Database connection and ORM setup (SQLAlchemy async)
   - Configuration management (Pydantic Settings)
   - Security middleware (JWT, rate limiting)
   - Structured logging and monitoring
   - Error handling and telemetry

3. **Services Layer** (`src/heimdall/services/`)
   - Business logic implementation
   - LLM integration (Qwen/通义千问 via OpenAI-compatible API)
   - Session management and data persistence
   - Recommendation algorithms

4. **Tools System** (`src/heimdall/tools/`)
   - Dynamic tool registry and execution
   - General-purpose tools (datetime, weather, math)
   - Domain-specific tools (advertising, analytics)

### Key Architectural Patterns

- **Async/Await**: Fully async architecture for high performance
- **Dependency Injection**: FastAPI's dependency system throughout
- **Repository Pattern**: Data access abstraction via services
- **Factory Pattern**: Application and component initialization
- **Middleware Pipeline**: Cross-cutting concerns (logging, security, monitoring)

### Configuration

- Environment-based configuration using `.env` file
- Pydantic Settings for type-safe configuration
- Separate configurations for development/production
- No hardcoded secrets - all via environment variables

### Database Schema

The application uses PostgreSQL with the following main entities:
- User sessions and conversations
- Intent analysis results
- Product catalogs and recommendations
- User behavior tracking
- Advertising analytics

See `sql/001_initial_schema.sql` for the complete schema.

### Security Implementation

- JWT-based authentication
- Rate limiting with Redis
- Input validation via Pydantic
- CORS configuration
- Security headers (OWASP recommended)
- No hardcoded secrets

### Monitoring and Observability

- Structured JSON logging with request IDs
- Health check endpoints (`/health`, `/api/health`)
- Performance metrics collection
- Error tracking and reporting
- Prometheus-ready metrics

## Development Guidelines

### Adding New Endpoints

1. Create router in `src/heimdall/api/endpoints/`
2. Define Pydantic models for requests/responses
3. Implement business logic in services layer
4. Register router in `main.py`
5. Add tests in `tests/`

### Adding New Tools

1. Implement tool function in `src/heimdall/tools/`
2. Register in `tools/registry.py`
3. Add schema definition for tool parameters
4. Test via `/api/v1/tools/call` endpoint

### Database Changes

1. Update migration files in `sql/`
2. Modify SQLAlchemy models in `models/db_models.py`
3. Update Pydantic schemas if needed
4. Add tests for new functionality

### Environment Variables

Required environment variables (see `.env.template`):
- `DATABASE_URL`: PostgreSQL connection string
- `QWEN_API_KEY`: Qwen/通义千问 API key
- `QWEN_BASE_URL`: Qwen API base URL
- `SECRET_KEY`: JWT secret key
- `REDIS_URL`: Redis connection string

## Project Structure Notes

- Source code in `src/heimdall/` following Python packaging standards
- Templates in `templates/` for web interface
- Static assets in `static/`
- Tests in `tests/` with pytest structure
- SQL migrations in `sql/`
- Configuration templates in root (`.env.template`)

## Common Issues

- Port conflicts: Application runs on port 8003 by default
- PYTHONPATH: Must include `src` directory
- Virtual environment: Use provided activation scripts
- Database: PostgreSQL must be running and accessible
- API keys: Valid Qwen API key required for LLM features