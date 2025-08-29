# --- START OF FILE heimdall/core/context.py (复用自py_ai_core) ---
from contextvars import ContextVar

# 创建一个ContextVar，它将在整个应用的异步上下文中携带请求ID
# 'request_id'是变量名，default=None是当变量未设置时的默认值
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# --- END OF FILE heimdall/core/context.py ---