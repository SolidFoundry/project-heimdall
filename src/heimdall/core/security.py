"""
企业级安全中间件模块。

提供认证、授权、输入验证、安全头部等企业级安全功能。
"""

import secrets
import hashlib
import re
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 安全配置
@dataclass
class SecurityConfig:
    """安全配置类"""
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    MAX_CONTENT_LENGTH: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_HOSTS: List[str] = None
    CORS_ORIGINS: List[str] = None
    
    def __post_init__(self):
        if self.ALLOWED_HOSTS is None:
            self.ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
        if self.CORS_ORIGINS is None:
            self.CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]

security_config = SecurityConfig()

class SecurityMiddleware(BaseHTTPMiddleware):
    """企业级安全中间件"""
    
    def __init__(self, app: FastAPI, config: SecurityConfig = security_config):
        super().__init__(app)
        self.config = config
        self.rate_limit_store = {}  # 简单的内存存储，生产环境应使用Redis
        
    async def dispatch(self, request: Request, call_next):
        """处理每个请求的安全检查"""
        
        # 1. 主机验证
        if not await self._validate_host(request):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Host not allowed"}
            )
        
        # 2. 速率限制
        if not await self._check_rate_limit(request):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded"}
            )
        
        # 3. 内容长度验证
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.config.MAX_CONTENT_LENGTH:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request entity too large"}
            )
        
        # 4. 添加安全头部
        response = await call_next(request)
        response = self._add_security_headers(response)
        
        return response
    
    async def _validate_host(self, request: Request) -> bool:
        """验证请求主机"""
        host = request.headers.get("host", "").split(":")[0]
        return host in self.config.ALLOWED_HOSTS
    
    async def _check_rate_limit(self, request: Request) -> bool:
        """检查速率限制"""
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 清理过期的记录
        self.rate_limit_store = {
            ip: (count, timestamp) 
            for ip, (count, timestamp) in self.rate_limit_store.items()
            if current_time - timestamp < self.config.RATE_LIMIT_WINDOW
        }
        
        # 检查并更新计数
        if client_ip in self.rate_limit_store:
            count, timestamp = self.rate_limit_store[client_ip]
            if count >= self.config.RATE_LIMIT_REQUESTS:
                return False
            self.rate_limit_store[client_ip] = (count + 1, timestamp)
        else:
            self.rate_limit_store[client_ip] = (1, current_time)
        
        return True
    
    def _add_security_headers(self, response: Response) -> Response:
        """添加安全HTTP头部"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://code.jquery.com https://cdn.datatables.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdn.datatables.net; img-src 'self' data: https:; font-src 'self' https://cdn.jsdelivr.net data:;"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """验证密码强度"""
        result = {
            "is_valid": True,
            "score": 0,
            "issues": []
        }
        
        if len(password) < 8:
            result["issues"].append("Password must be at least 8 characters long")
            result["is_valid"] = False
        
        if not re.search(r'[A-Z]', password):
            result["issues"].append("Password must contain at least one uppercase letter")
            result["is_valid"] = False
        
        if not re.search(r'[a-z]', password):
            result["issues"].append("Password must contain at least one lowercase letter")
            result["is_valid"] = False
        
        if not re.search(r'\d', password):
            result["issues"].append("Password must contain at least one digit")
            result["is_valid"] = False
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["issues"].append("Password must contain at least one special character")
            result["is_valid"] = False
        
        # 计算密码强度分数
        result["score"] = len(password)
        result["score"] += 1 if re.search(r'[A-Z]', password) else 0
        result["score"] += 1 if re.search(r'[a-z]', password) else 0
        result["score"] += 1 if re.search(r'\d', password) else 0
        result["score"] += 1 if re.search(r'[!@#$%^&*(),.?":{}|<>]', password) else 0
        
        return result
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """清理输入字符串，防止XSS攻击"""
        # 移除潜在的恶意字符
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', input_string, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        return sanitized.strip()

class JWTManager:
    """JWT令牌管理器"""
    
    def __init__(self, config: SecurityConfig = security_config):
        self.config = config
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """创建访问令牌"""
        import jwt
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.config.SECRET_KEY, algorithm=self.config.ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        import jwt
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.config.SECRET_KEY, algorithm=self.config.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        import jwt
        try:
            payload = jwt.decode(token, self.config.SECRET_KEY, algorithms=[self.config.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTError:
            logger.warning("Invalid token")
            return None

# 安全依赖项
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_manager: JWTManager = Depends()
) -> Dict[str, Any]:
    """获取当前用户信息"""
    token = credentials.credentials
    payload = jwt_manager.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

def setup_security_middleware(app: FastAPI) -> FastAPI:
    """设置安全中间件"""
    
    # 1. 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=security_config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 2. 添加安全中间件
    app.add_middleware(SecurityMiddleware)
    
    logger.info("安全中间件已配置完成")
    
    return app

# 企业级安全异常处理
class SecurityHTTPException(HTTPException):
    """安全相关HTTP异常"""
    
    def __init__(self, status_code: int, detail: str, security_event_type: str):
        super().__init__(status_code=status_code, detail=detail)
        self.security_event_type = security_event_type
        
        # 记录安全事件
        logger.warning(
            f"安全事件: {security_event_type}, 状态码: {status_code}, 详情: {detail}",
            extra={"security_event": security_event_type, "status_code": status_code}
        )