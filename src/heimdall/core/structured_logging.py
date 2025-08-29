"""
结构化日志处理器模块。

提供JSON格式的结构化日志记录，支持请求ID追踪、耗时统计等企业级功能。
"""

import contextvars
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# 创建全局context variable
request_id_var = contextvars.ContextVar('request_id', default='N/A')


class StructuredLogFormatter(logging.Formatter):
    """JSON格式的结构化日志格式化器"""
    
    def __init__(self):
        super().__init__()
    
    def format(self, record):
        # 创建基础日志结构
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": record.getMessage(),
            "name": record.name,
            "levelname": record.levelname,
        }
        
        # 添加请求ID（优先从record获取，否则从上下文获取，总是包含）
        request_id = getattr(record, 'request_id', None)
        if request_id is None:
            request_id = get_request_id()
        log_entry["request_id"] = request_id
        
        # 添加HTTP信息（如果存在）
        if hasattr(record, 'http_info'):
            log_entry["http"] = record.http_info
        
        # 添加耗时信息（如果存在）
        if hasattr(record, 'duration'):
            log_entry["duration"] = record.duration
        
        # 添加其他额外字段
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # 添加异常信息（如果存在）
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """请求ID中间件，为每个请求生成唯一的追踪ID"""
    
    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 设置context variable
        set_request_id(request_id)
        
        # 记录开始时间
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算耗时
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        # 记录访问日志
        access_logger = logging.getLogger("heimdall.access")
        
        # 构建HTTP信息
        http_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client": {
                "host": request.client.host if request.client else "unknown",
                "port": request.client.port if request.client else 0
            },
            "status_code": response.status_code
        }
        
        # 设置日志记录器属性
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(name, level, fn, lno, msg, args, exc_info, func=None, sinfo=None):
            record = old_factory(name, level, fn, lno, msg, args, exc_info, func, sinfo)
            record.request_id = request_id
            record.http_info = http_info
            record.duration = {"ms": duration_ms}
            return record
        
        logging.setLogRecordFactory(record_factory)
        
        try:
            access_logger.info("request handled")
        finally:
            logging.setLogRecordFactory(old_factory)
        
        # 在响应头中添加请求ID
        response.headers["X-Request-ID"] = request_id
        
        return response


class HeartbeatManager:
    """心跳管理器"""
    
    def __init__(self, interval_hours: int = 1):
        import os
        # 从环境变量读取配置
        self.enabled = os.getenv("HEARTBEAT_ENABLED", "true").lower() == "true"
        self.interval_hours = int(os.getenv("HEARTBEAT_INTERVAL_HOURS", str(interval_hours)))
        self.interval_seconds = self.interval_hours * 3600
        self.is_running = False
        self.logger = logging.getLogger("heimdall.heartbeat")
    
    async def start(self):
        """启动心跳"""
        if not self.enabled:
            self.logger.info("心跳功能已禁用")
            return
            
        if self.is_running:
            return
        
        self.is_running = True
        import asyncio
        
        self.logger.info(f"心跳任务已启动，间隔: {self.interval_hours}小时")
        
        while self.is_running:
            # 记录心跳日志
            old_factory = logging.getLogRecordFactory()
            
            def record_factory(name, level, fn, lno, msg, args, exc_info, func=None, sinfo=None):
                record = old_factory(name, level, fn, lno, msg, args, exc_info, func, sinfo)
                record.request_id = "N/A"
                return record
            
            logging.setLogRecordFactory(record_factory)
            
            try:
                self.logger.info("心跳: 服务正在运行...")
            finally:
                logging.setLogRecordFactory(old_factory)
            
            # 等待下一次心跳
            await asyncio.sleep(self.interval_seconds)
    
    def stop(self):
        """停止心跳"""
        self.is_running = False


def get_request_id() -> str:
    """获取当前请求的ID"""
    return request_id_var.get()


def set_request_id(request_id: str):
    """设置当前请求的ID"""
    request_id_var.set(request_id)


def create_structured_logger(name: str) -> logging.Logger:
    """创建结构化日志记录器"""
    logger = logging.getLogger(name)
    return logger


# 全局心跳管理器实例
heartbeat_manager = HeartbeatManager(interval_hours=1)