# --- START OF FILE heimdall/core/utils.py (复用自py_ai_core) ---
from slowapi import Limiter
from slowapi.util import get_remote_address
from cachetools import TTLCache

# 创建限流器实例
limiter = Limiter(key_func=get_remote_address)
# 创建健康检查缓存
health_check_cache = TTLCache(maxsize=1, ttl=5)

# --- END OF FILE heimdall/core/utils.py ---