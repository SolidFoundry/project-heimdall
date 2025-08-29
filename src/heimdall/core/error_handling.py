"""
企业级错误处理和异常管理模块。

提供统一的错误处理、异常分类、错误恢复、错误报告等功能。
"""

import traceback
import sys
import uuid
from typing import Dict, Any, Optional, List, Callable, Type, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import json

logger = logging.getLogger(__name__)

class ErrorType(str, Enum):
    """错误类型枚举"""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    DATABASE_ERROR = "database_error"
    EXTERNAL_API_ERROR = "external_api_error"
    NETWORK_ERROR = "network_error"
    SYSTEM_ERROR = "system_error"
    TIMEOUT_ERROR = "timeout_error"
    RESOURCE_NOT_FOUND = "resource_not_found"
    CONFLICT_ERROR = "conflict_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    CRITICAL_ERROR = "critical_error"
    UNKNOWN_ERROR = "unknown_error"

class ErrorSeverity(str, Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorContext:
    """错误上下文信息"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    environment: str = "development"

@dataclass
class ErrorDetail:
    """错误详情"""
    error_id: str
    error_type: ErrorType
    error_code: str
    message: str
    detail: Optional[str] = None
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    stack_trace: Optional[str] = None
    context: ErrorContext = field(default_factory=ErrorContext)
    additional_data: Dict[str, Any] = field(default_factory=dict)
    retryable: bool = False
    should_alert: bool = False
    resolved: bool = False
    resolution_notes: Optional[str] = None

class BaseHeimdallException(Exception):
    """基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN_ERROR,
        error_code: str = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        detail: str = None,
        additional_data: Dict[str, Any] = None,
        retryable: bool = False,
        should_alert: bool = False
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.detail = detail
        self.additional_data = additional_data or {}
        self.retryable = retryable
        self.should_alert = should_alert
        self.error_id = str(uuid.uuid4())

class ValidationError(BaseHeimdallException):
    """验证错误"""
    
    def __init__(self, message: str, field: str = None, detail: str = None, **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.VALIDATION_ERROR,
            error_code="VALIDATION_ERROR",
            severity=ErrorSeverity.LOW,
            detail=detail,
            additional_data={"field": field} if field else {},
            **kwargs
        )

class AuthenticationError(BaseHeimdallException):
    """认证错误"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.AUTHENTICATION_ERROR,
            error_code="AUTHENTICATION_ERROR",
            severity=ErrorSeverity.HIGH,
            should_alert=True,
            **kwargs
        )

class AuthorizationError(BaseHeimdallException):
    """授权错误"""
    
    def __init__(self, message: str = "Authorization failed", **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.AUTHORIZATION_ERROR,
            error_code="AUTHORIZATION_ERROR",
            severity=ErrorSeverity.HIGH,
            should_alert=True,
            **kwargs
        )

class BusinessLogicError(BaseHeimdallException):
    """业务逻辑错误"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.BUSINESS_LOGIC_ERROR,
            error_code="BUSINESS_LOGIC_ERROR",
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class DatabaseError(BaseHeimdallException):
    """数据库错误"""
    
    def __init__(self, message: str, retryable: bool = True, **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.DATABASE_ERROR,
            error_code="DATABASE_ERROR",
            severity=ErrorSeverity.HIGH,
            retryable=retryable,
            should_alert=True,
            **kwargs
        )

class ExternalAPIError(BaseHeimdallException):
    """外部API错误"""
    
    def __init__(self, message: str, service: str = None, retryable: bool = True, **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.EXTERNAL_API_ERROR,
            error_code="EXTERNAL_API_ERROR",
            severity=ErrorSeverity.MEDIUM,
            retryable=retryable,
            additional_data={"service": service} if service else {},
            **kwargs
        )

class NetworkError(BaseHeimdallException):
    """网络错误"""
    
    def __init__(self, message: str, retryable: bool = True, **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.NETWORK_ERROR,
            error_code="NETWORK_ERROR",
            severity=ErrorSeverity.MEDIUM,
            retryable=retryable,
            **kwargs
        )

class ResourceNotFoundError(BaseHeimdallException):
    """资源未找到错误"""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None, **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.RESOURCE_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            severity=ErrorSeverity.LOW,
            additional_data={
                "resource_type": resource_type,
                "resource_id": resource_id
            },
            **kwargs
        )

class ConflictError(BaseHeimdallException):
    """冲突错误"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.CONFLICT_ERROR,
            error_code="CONFLICT_ERROR",
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

class RateLimitError(BaseHeimdallException):
    """速率限制错误"""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(
            message=message,
            error_type=ErrorType.RATE_LIMIT_ERROR,
            error_code="RATE_LIMIT_ERROR",
            severity=ErrorSeverity.LOW,
            **kwargs
        )

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_store: List[ErrorDetail] = []
        self.error_callbacks: Dict[ErrorType, List[Callable]] = {}
        self.alert_thresholds = {
            ErrorSeverity.CRITICAL: 1,
            ErrorSeverity.HIGH: 10,
            ErrorSeverity.MEDIUM: 50,
            ErrorSeverity.LOW: 100
        }
        
        # 注册错误回调
        self._register_default_callbacks()
    
    def _register_default_callbacks(self):
        """注册默认错误回调"""
        self.register_callback(ErrorType.CRITICAL_ERROR, self._handle_critical_error)
        self.register_callback(ErrorType.SYSTEM_ERROR, self._handle_high_severity_error)
        self.register_callback(ErrorType.DATABASE_ERROR, self._handle_database_error)
        self.register_callback(ErrorType.EXTERNAL_API_ERROR, self._handle_external_api_error)
    
    def register_callback(self, error_type: ErrorType, callback: Callable):
        """注册错误回调"""
        if error_type not in self.error_callbacks:
            self.error_callbacks[error_type] = []
        self.error_callbacks[error_type].append(callback)
    
    def handle_exception(self, exception: Exception, context: ErrorContext = None) -> ErrorDetail:
        """处理异常"""
        # 创建错误详情
        error_detail = self._create_error_detail(exception, context)
        
        # 存储错误
        self.error_store.append(error_detail)
        
        # 记录错误日志
        self._log_error(error_detail)
        
        # 调用错误回调
        self._call_error_callbacks(error_detail)
        
        # 检查是否需要发送警报
        self._check_alert_threshold(error_detail)
        
        return error_detail
    
    def _create_error_detail(self, exception: Exception, context: ErrorContext = None) -> ErrorDetail:
        """创建错误详情"""
        if isinstance(exception, BaseHeimdallException):
            return ErrorDetail(
                error_id=exception.error_id,
                error_type=exception.error_type,
                error_code=exception.error_code,
                message=exception.message,
                detail=exception.detail,
                severity=exception.severity,
                stack_trace=traceback.format_exc(),
                context=context or ErrorContext(),
                additional_data=exception.additional_data,
                retryable=exception.retryable,
                should_alert=exception.should_alert
            )
        else:
            return ErrorDetail(
                error_id=str(uuid.uuid4()),
                error_type=ErrorType.UNKNOWN_ERROR,
                error_code="UNKNOWN_ERROR",
                message=str(exception),
                severity=ErrorSeverity.HIGH,
                stack_trace=traceback.format_exc(),
                context=context or ErrorContext(),
                should_alert=True
            )
    
    def _log_error(self, error_detail: ErrorDetail):
        """记录错误日志"""
        log_data = {
            "error_id": error_detail.error_id,
            "error_type": error_detail.error_type.value,
            "error_code": error_detail.error_code,
            "message": error_detail.message,
            "severity": error_detail.severity.value,
            "context": asdict(error_detail.context),
            "additional_data": error_detail.additional_data
        }
        
        if error_detail.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error: {json.dumps(log_data, ensure_ascii=False)}")
        elif error_detail.severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {json.dumps(log_data, ensure_ascii=False)}")
        elif error_detail.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {json.dumps(log_data, ensure_ascii=False)}")
        else:
            logger.info(f"Low severity error: {json.dumps(log_data, ensure_ascii=False)}")
    
    def _call_error_callbacks(self, error_detail: ErrorDetail):
        """调用错误回调"""
        callbacks = self.error_callbacks.get(error_detail.error_type, [])
        for callback in callbacks:
            try:
                callback(error_detail)
            except Exception as e:
                logger.error(f"Error callback failed: {e}")
    
    def _check_alert_threshold(self, error_detail: ErrorDetail):
        """检查警报阈值"""
        if not error_detail.should_alert:
            return
        
        # 计算最近一小时的错误数量
        recent_errors = [
            error for error in self.error_store
            if (datetime.utcnow() - error.context.timestamp).total_seconds() < 3600
            and error.error_type == error_detail.error_type
        ]
        
        threshold = self.alert_thresholds.get(error_detail.severity, float('inf'))
        if len(recent_errors) >= threshold:
            self._send_alert(error_detail, len(recent_errors))
    
    def _send_alert(self, error_detail: ErrorDetail, count: int):
        """发送警报"""
        alert_data = {
            "error_type": error_detail.error_type.value,
            "error_code": error_detail.error_code,
            "message": error_detail.message,
            "severity": error_detail.severity.value,
            "count": count,
            "timestamp": error_detail.context.timestamp.isoformat()
        }
        
        logger.critical(f"ALERT: {json.dumps(alert_data, ensure_ascii=False)}")
        # 这里可以集成外部警报系统如邮件、Slack等
    
    def _handle_critical_error(self, error_detail: ErrorDetail):
        """处理严重错误"""
        logger.critical(f"Critical error detected: {error_detail.error_id}")
        # 可以添加自动恢复逻辑
    
    def _handle_high_severity_error(self, error_detail: ErrorDetail):
        """处理高严重性错误"""
        logger.error(f"High severity error: {error_detail.error_id}")
        # 可以添加降级逻辑
    
    def _handle_database_error(self, error_detail: ErrorDetail):
        """处理数据库错误"""
        logger.error(f"Database error: {error_detail.error_id}")
        # 可以添加数据库连接池检查
    
    def _handle_external_api_error(self, error_detail: ErrorDetail):
        """处理外部API错误"""
        logger.error(f"External API error: {error_detail.error_id}")
        # 可以添加熔断器逻辑
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计"""
        stats = {
            "total_errors": len(self.error_store),
            "by_type": {},
            "by_severity": {},
            "recent_errors": []
        }
        
        for error in self.error_store:
            # 按类型统计
            error_type = error.error_type.value
            if error_type not in stats["by_type"]:
                stats["by_type"][error_type] = 0
            stats["by_type"][error_type] += 1
            
            # 按严重程度统计
            severity = error.severity.value
            if severity not in stats["by_severity"]:
                stats["by_severity"][severity] = 0
            stats["by_severity"][severity] += 1
        
        # 最近错误
        stats["recent_errors"] = [
            {
                "error_id": error.error_id,
                "error_type": error.error_type.value,
                "message": error.message,
                "severity": error.severity.value,
                "timestamp": error.context.timestamp.isoformat()
            }
            for error in self.error_store[-10:]
        ]
        
        return stats

class ErrorHandlingMiddleware:
    """错误处理中间件"""
    
    def __init__(self, app: FastAPI, error_handler: ErrorHandler):
        self.app = app
        self.error_handler = error_handler
        self._setup_exception_handlers()
    
    def _setup_exception_handlers(self):
        """设置异常处理器"""
        
        @self.app.exception_handler(BaseHeimdallException)
        async def handle_heimdall_exception(request: Request, exc: BaseHeimdallException):
            context = self._create_error_context(request)
            error_detail = self.error_handler.handle_exception(exc, context)
            
            return JSONResponse(
                status_code=self._get_status_code(exc.error_type),
                content=self._format_error_response(error_detail)
            )
        
        @self.app.exception_handler(StarletteHTTPException)
        async def handle_http_exception(request: Request, exc: StarletteHTTPException):
            context = self._create_error_context(request)
            error_detail = self.error_handler.handle_exception(exc, context)
            
            return JSONResponse(
                status_code=exc.status_code,
                content=self._format_error_response(error_detail)
            )
        
        @self.app.exception_handler(RequestValidationError)
        async def handle_validation_exception(request: Request, exc: RequestValidationError):
            context = self._create_error_context(request)
            validation_error = ValidationError(
                message="Validation failed",
                detail=str(exc.errors()),
                additional_data={"validation_errors": exc.errors()}
            )
            error_detail = self.error_handler.handle_exception(validation_error, context)
            
            return JSONResponse(
                status_code=422,
                content=self._format_error_response(error_detail)
            )
        
        @self.app.exception_handler(Exception)
        async def handle_generic_exception(request: Request, exc: Exception):
            context = self._create_error_context(request)
            error_detail = self.error_handler.handle_exception(exc, context)
            
            return JSONResponse(
                status_code=500,
                content=self._format_error_response(error_detail)
            )
    
    def _create_error_context(self, request: Request) -> ErrorContext:
        """创建错误上下文"""
        return ErrorContext(
            request_id=getattr(request.state, 'request_id', None),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            endpoint=str(request.url.path),
            method=request.method
        )
    
    def _get_status_code(self, error_type: ErrorType) -> int:
        """获取HTTP状态码"""
        status_code_map = {
            ErrorType.VALIDATION_ERROR: 422,
            ErrorType.AUTHENTICATION_ERROR: 401,
            ErrorType.AUTHORIZATION_ERROR: 403,
            ErrorType.RESOURCE_NOT_FOUND: 404,
            ErrorType.CONFLICT_ERROR: 409,
            ErrorType.RATE_LIMIT_ERROR: 429,
            ErrorType.BUSINESS_LOGIC_ERROR: 400,
            ErrorType.DATABASE_ERROR: 500,
            ErrorType.EXTERNAL_API_ERROR: 502,
            ErrorType.NETWORK_ERROR: 503,
            ErrorType.SYSTEM_ERROR: 500,
            ErrorType.TIMEOUT_ERROR: 504,
            ErrorType.UNKNOWN_ERROR: 500
        }
        return status_code_map.get(error_type, 500)
    
    def _format_error_response(self, error_detail: ErrorDetail) -> Dict[str, Any]:
        """格式化错误响应"""
        return {
            "error": {
                "id": error_detail.error_id,
                "type": error_detail.error_type.value,
                "code": error_detail.error_code,
                "message": error_detail.message,
                "detail": error_detail.detail,
                "severity": error_detail.severity.value,
                "retryable": error_detail.retryable
            },
            "request_id": error_detail.context.request_id,
            "timestamp": error_detail.context.timestamp.isoformat()
        }

# 全局错误处理器实例
error_handler = ErrorHandler()

def setup_error_handling(app: FastAPI) -> FastAPI:
    """设置错误处理"""
    middleware = ErrorHandlingMiddleware(app, error_handler)
    logger.info("错误处理中间件已配置完成")
    return app

# 错误恢复装饰器
def with_error_handling(error_types: List[ErrorType] = None, max_retries: int = 3):
    """错误处理装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if isinstance(e, BaseHeimdallException):
                        if not e.retryable or attempt == max_retries:
                            raise
                    else:
                        if attempt == max_retries:
                            raise
                    
                    logger.warning(f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__}: {e}")
                    
                    # 指数退避
                    import time
                    time.sleep(2 ** attempt)
            
            raise last_exception
        
        return wrapper
    return decorator

# 错误报告工具
class ErrorReporter:
    """错误报告工具"""
    
    @staticmethod
    def report_error(error_detail: ErrorDetail):
        """报告错误"""
        # 这里可以集成外部错误报告服务
        logger.error(f"Error reported: {error_detail.error_id}")
    
    @staticmethod
    def generate_error_report(time_range_hours: int = 24) -> Dict[str, Any]:
        """生成错误报告"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        recent_errors = [
            error for error in error_handler.error_store
            if error.context.timestamp >= cutoff_time
        ]
        
        report = {
            "time_range_hours": time_range_hours,
            "total_errors": len(recent_errors),
            "by_type": {},
            "by_severity": {},
            "top_errors": []
        }
        
        for error in recent_errors:
            # 按类型统计
            error_type = error.error_type.value
            if error_type not in report["by_type"]:
                report["by_type"][error_type] = 0
            report["by_type"][error_type] += 1
            
            # 按严重程度统计
            severity = error.severity.value
            if severity not in report["by_severity"]:
                report["by_severity"][severity] = 0
            report["by_severity"][severity] += 1
        
        # 最常见错误
        error_counts = {}
        for error in recent_errors:
            key = f"{error.error_type.value}:{error.error_code}"
            error_counts[key] = error_counts.get(key, 0) + 1
        
        report["top_errors"] = [
            {"error_key": key, "count": count}
            for key, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return report