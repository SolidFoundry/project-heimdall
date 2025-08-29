# --- START OF FILE heimdall/core/middleware.py (复用自py_ai_core) ---

import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from heimdall.core.context import request_id_var

# 访问日志记录器
access_logger = logging.getLogger("heimdall.access")


class CtxTimingMiddleware(BaseHTTPMiddleware):
    """上下文和计时中间件，用于请求ID追踪和性能监控"""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # 生成请求ID并设置到上下文变量中
        request_id = str(uuid.uuid4())
        token = request_id_var.set(request_id)

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        process_time_ms = int(process_time * 1000)

        # 在响应头中添加处理时间和请求ID
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        response.headers["X-Request-ID"] = request_id

        log_message = "请求已处理"

        # 构造详细的访问日志数据
        extra_data = {
            "http": {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "client": {
                    "host": request.client.host,
                    "port": request.client.port,
                },
                "status_code": response.status_code,
            },
            "duration": {"ms": process_time_ms},
        }

        # 使用 extra 参数传递这个字典，python-json-logger会自动处理
        access_logger.info(log_message, extra=extra_data)

        # 重置上下文变量
        request_id_var.reset(token)

        return response


# --- END OF FILE heimdall/core/middleware.py ---