# ===================================================================
# 海姆达尔中间件模块
# ===================================================================
# 该模块定义了应用的中间件，包括：
# - 请求ID追踪和上下文管理
# - 请求处理时间监控
# - 访问日志记录
# ===================================================================

import time
import uuid
import logging
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from src.heimdall.core.context import request_id_var

# 访问日志记录器 - 专门记录HTTP访问日志
access_logger = logging.getLogger("heimdall.access")


class CtxTimingMiddleware(BaseHTTPMiddleware):
    """上下文和计时中间件
    
    这个中间件为每个HTTP请求：
    1. 生成唯一的请求ID并设置到上下文中
    2. 测量请求处理时间
    3. 在响应头中添加性能信息
    4. 记录结构化的访问日志
    
    Attributes:
        无特殊属性
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """处理HTTP请求的核心方法
        
        为每个请求执行以下操作：
        - 生成请求ID并设置上下文
        - 记录开始时间
        - 调用下一个中间件/路由处理器
        - 计算处理时间
        - 添加响应头
        - 记录访问日志
        
        Args:
            request: FastAPI请求对象
            call_next: 下一个处理器的调用函数
            
        Returns:
            Response: FastAPI响应对象，包含处理时间和请求ID头
        """
        # 1. 生成请求ID并设置到上下文变量中
        request_id = str(uuid.uuid4())
        token = request_id_var.set(request_id)

        # 2. 记录开始时间并调用下一个处理器
        start_time = time.time()
        response = await call_next(request)
        
        # 3. 计算请求处理时间（毫秒）
        process_time = time.time() - start_time
        process_time_ms = int(process_time * 1000)

        # 4. 在响应头中添加处理时间和请求ID
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        response.headers["X-Request-ID"] = request_id

        # 5. 准备日志消息和额外数据
        log_message = "HTTP请求已处理完成"

        # 6. 构造详细的访问日志数据结构
        extra_data: Dict[str, Any] = {
            "http": {
                "method": request.method,                    # HTTP方法
                "url": str(request.url),                     # 完整URL
                "path": request.url.path,                   # 路径
                "client": {
                    "host": request.client.host,            # 客户端IP
                    "port": request.client.port,            # 客户端端口
                },
                "status_code": response.status_code,        # HTTP状态码
            },
            "duration": {"ms": process_time_ms},            # 处理时长
        }

        # 7. 记录结构化访问日志
        # 使用 extra 参数传递字典，python-json-logger会自动处理
        access_logger.info(
            log_message,
            extra={
                "request_id": request_id,                  # 请求ID
                **extra_data                                # 展开额外数据
            }
        )

        # 8. 重置上下文变量并返回响应
        request_id_var.reset(token)
        
        return response


# ===================================================================
# 中间件使用说明：
# 1. 在 FastAPI 应用中添加中间件：
#    app.add_middleware(CtxTimingMiddleware)
#
# 2. 中间件会自动为每个请求：
#    - 生成唯一请求ID
#    - 记录处理时间
#    - 添加响应头
#    - 记录结构化日志
#
# 3. 在其他地方获取请求ID：
#    from src.heimdall.core.context import request_id_var
#    request_id = request_id_var.get()
# ===================================================================