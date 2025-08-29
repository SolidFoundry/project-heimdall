# SQL 数据库迁移文件

本目录包含 Project Heimdall 的数据库架构迁移文件。

## 文件命名规范

文件使用格式：`XXX_描述.sql`，其中：
- `XXX` 是顺序号（001, 002, 003 等）
- `描述` 是对迁移的简要说明

## 当前迁移文件

- `001_initial_schema.sql` - 初始数据库架构，包含 chat_sessions 和 chat_messages 表

## 数据库架构

### 表结构

1. **chat_sessions** - 存储聊天会话元数据
   - `id` - 主键
   - `session_id` - 唯一会话标识符
   - `system_prompt` - 会话的系统提示词
   - `created_at` - 创建时间戳
   - `updated_at` - 最后更新时间戳

2. **chat_messages** - 存储单个聊天消息
   - `id` - 主键
   - `session_id` - 关联到聊天会话
   - `role` - 消息角色（user, assistant, tool, system）
   - `content` - JSON 格式的消息内容
   - `created_at` - 创建时间戳

### 索引

- 为优化查询性能创建了索引
- 复合索引支持常见查询模式

## 如何应用迁移

### 方法一：使用自动化迁移工具（推荐）
```bash
# 显示迁移状态
python scripts/database_migrate.py --status

# 应用所有待处理的迁移
python scripts/database_migrate.py --migrate

# 迁移到特定版本
python scripts/database_migrate.py --version 001
```

### 方法二：手动应用迁移
```bash
# 手动执行SQL文件
psql -d your_database -f sql/001_initial_schema.sql
```

### 方法三：使用Docker Compose（开发环境）
```bash
docker-compose exec heimdall python scripts/database_migrate.py --migrate
```

2. 对于新的迁移，使用下一个顺序号创建文件，迁移工具会自动发现并应用。

## 最佳实践

1. 始终先在开发环境中测试迁移
2. 对复杂迁移使用事务
3. 尽可能包含回滚脚本
4. 添加新迁移时更新此 README
5. 使用描述性的迁移文件名

## 开发团队协作

- 所有数据库变更都必须通过迁移文件进行
- 迁移文件需要经过代码审查
- 保持迁移文件的顺序性和完整性
- 定期清理和优化迁移历史