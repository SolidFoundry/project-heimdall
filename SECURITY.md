# Project Heimdall 安全配置指南

## 概述

Project Heimdall 遵循安全最佳实践，不在代码中硬编码任何敏感信息。所有敏感配置都通过环境变量管理。

## 安全原则

1. **零硬编码**: 代码中不包含任何敏感信息
2. **环境变量**: 所有敏感信息通过环境变量注入
3. **最小权限**: 使用最小必要的权限
4. **定期轮换**: 定期更换密钥和密码

## 环境变量配置

### 必需的环境变量

```bash
# 数据库配置
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=heimdall_db

# 安全配置
SECRET_KEY=your_jwt_secret_key_min_32_chars
ENCRYPTION_KEY=your_fernet_encryption_key

# LLM API配置
LLM_API_KEY=your_actual_llm_api_key
LLM_API_BASE=https://your-api-endpoint.com/v1
```

### 可选的环境变量

```bash
# Redis配置（如果使用）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# 应用配置
ENVIRONMENT=development
DEBUG=false
HOST=0.0.0.0
PORT=8003
```

## 生成安全密钥

使用提供的脚本生成安全密钥：

```bash
python generate_secure_keys.py
```

这将生成：
- JWT Secret Key
- Fernet Encryption Key
- Database Password
- 其他随机字符串

## 安全检查

项目提供了安全检查工具：

```bash
# 运行安全检查
python simple_security_check.py
```

此工具会扫描项目文件，查找可能的硬编码敏感信息。

## 最佳实践

### 1. 环境管理

- **开发环境**: 使用 `.env` 文件
- **测试环境**: 使用 CI/CD 环境变量
- **生产环境**: 使用 secrets management 服务

### 2. 密钥管理

- 每个环境使用不同的密钥
- 定期轮换密钥（建议每90天）
- 使用强密码（至少16字符）
- 不要在多个服务间共享密钥

### 3. 数据库安全

```sql
-- 创建专用用户
CREATE USER heimdall_user WITH PASSWORD 'strong_password';
-- 授予最小权限
GRANT CONNECT ON DATABASE heimdall_db TO heimdall_user;
GRANT USAGE ON SCHEMA public TO heimdall_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO heimdall_user;
```

### 4. API安全

- 使用HTTPS
- 实现速率限制
- 验证输入数据
- 记录安全事件

### 5. Docker安全

```yaml
# docker-compose.yml 安全实践
services:
  app:
    environment:
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}  # 不提供默认值
    # 不要挂载包含敏感信息的卷
```

## 文件安全

### .gitignore 确保

确保以下文件在 `.gitignore` 中：

```
# 环境变量
.env
.env.local
.env.*.local

# 日志
*.log
logs/

# 临时文件
*.tmp
*.temp

# 数据库
*.db
*.sqlite
```

### 配置文件安全

- `config_manager.py`: 使用 Pydantic Settings 从环境变量读取
- 不在配置文件中硬编码默认值
- 使用类型安全的配置管理

## 部署安全

### 1. 环境变量注入

```bash
# systemd 服务
Environment="DATABASE_PASSWORD=${DATABASE_PASSWORD}"
Environment="SECRET_KEY=${SECRET_KEY}"

# Docker
docker run -e DATABASE_PASSWORD=${DATABASE_PASSWORD} ...

# Kubernetes
env:
  - name: DATABASE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: heimdall-secrets
        key: database-password
```

### 2. Secrets Management

推荐使用专业的 secrets 管理方案：
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

## 监控和审计

### 1. 日志监控

```python
# 记录安全事件
logger.warning("Failed login attempt", extra={"user_id": user_id})
logger.error("Security violation", extra={"ip": request.client.host})
```

### 2. 访问控制

```python
# 实现基于角色的访问控制
@app.get("/admin")
async def admin_panel(current_user: User = Depends(get_current_admin_user)):
    # 只有管理员可以访问
    pass
```

## 安全更新

定期更新依赖项：

```bash
# 检查过时的包
pip list --outdated

# 更新依赖
pip-compile --upgrade requirements.in
```

## 应急响应

### 1. 密钥泄露

如果怀疑密钥泄露：
1. 立即更换所有密钥
2. 检查日志确认泄露范围
3. 通知相关方
4. 审计访问记录

### 2. 安全事件响应流程

1. 检测：监控系统告警
2. 评估：确定影响范围
3. 控制：限制损害
4. 根除：修复漏洞
5. 恢复：恢复正常运营
6. 总结：更新安全策略

## 联系信息

发现安全问题请联系：
- 安全团队邮箱：security@yourcompany.com
- 紧急安全事件：创建带 "SECURITY" 标签的 GitHub Issue

---

**记住：安全是一个持续的过程，不是一次性任务。**