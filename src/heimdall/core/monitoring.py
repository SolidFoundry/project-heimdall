"""
企业级监控和可观测性模块。

提供指标收集、分布式追踪、健康检查、性能监控等功能。
"""

import time
import threading
import psutil
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
from contextlib import contextmanager
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
import json

logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    """指标数据"""
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PerformanceMetrics:
    """性能指标"""
    request_count: int = 0
    error_count: int = 0
    total_response_time: float = 0.0
    max_response_time: float = 0.0
    min_response_time: float = float('inf')
    last_request_time: Optional[datetime] = None
    
    def update(self, response_time: float, is_error: bool = False):
        """更新性能指标"""
        self.request_count += 1
        self.total_response_time += response_time
        self.max_response_time = max(self.max_response_time, response_time)
        self.min_response_time = min(self.min_response_time, response_time)
        self.last_request_time = datetime.utcnow()
        
        if is_error:
            self.error_count += 1
    
    def get_average_response_time(self) -> float:
        """获取平均响应时间"""
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
    
    def get_error_rate(self) -> float:
        """获取错误率"""
        if self.request_count == 0:
            return 0.0
        return (self.error_count / self.request_count) * 100

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, app_name: str = "heimdall"):
        self.app_name = app_name
        self.metrics_store: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.performance_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self.custom_metrics: Dict[str, MetricData] = {}
        
        # Prometheus指标
        self.request_counter = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        
        self.active_requests = Gauge(
            'http_active_requests',
            'Active HTTP requests'
        )
        
        self.error_counter = Counter(
            'http_errors_total',
            'Total HTTP errors',
            ['method', 'endpoint', 'status_code']
        )
        
        self.system_info = Info(
            'app_info',
            'Application information'
        )
        
        self.system_info.info({
            'app_name': app_name,
            'version': '1.0.0',
            'environment': 'development'
        })
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """记录请求指标"""
        key = f"{method}_{endpoint}"
        is_error = status_code >= 400
        
        # 更新性能指标
        self.performance_metrics[key].update(duration, is_error)
        
        # Prometheus指标
        self.request_counter.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        if is_error:
            self.error_counter.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
        
        # 存储原始指标
        metric = MetricData(
            name="http_request",
            value=duration,
            labels={
                "method": method,
                "endpoint": endpoint,
                "status_code": str(status_code),
                "app": self.app_name
            }
        )
        self.metrics_store["http_request"].append(metric)
    
    def record_custom_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """记录自定义指标"""
        metric = MetricData(
            name=name,
            value=value,
            labels=labels or {},
            timestamp=datetime.utcnow()
        )
        self.custom_metrics[name] = metric
        self.metrics_store[name].append(metric)
    
    def get_metrics(self, metric_name: str, limit: int = 100) -> List[MetricData]:
        """获取指标数据"""
        return list(self.metrics_store.get(metric_name, []))[-limit:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        summary = {}
        for key, metrics in self.performance_metrics.items():
            if metrics.request_count > 0:
                summary[key] = {
                    "request_count": metrics.request_count,
                    "error_count": metrics.error_count,
                    "avg_response_time": metrics.get_average_response_time(),
                    "max_response_time": metrics.max_response_time,
                    "min_response_time": metrics.min_response_time,
                    "error_rate": metrics.get_error_rate(),
                    "last_request_time": metrics.last_request_time.isoformat() if metrics.last_request_time else None
                }
        return summary
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {}
    
    def export_prometheus_metrics(self) -> str:
        """导出Prometheus格式指标"""
        return generate_latest().decode('utf-8')

class DistributedTracer:
    """分布式追踪器"""
    
    def __init__(self):
        self.traces: Dict[str, Dict[str, Any]] = {}
        self.active_spans: Dict[str, Any] = {}
    
    def start_span(self, trace_id: str, span_id: str, parent_span_id: str = None, 
                   operation: str = "", start_time: datetime = None) -> str:
        """开始一个span"""
        if start_time is None:
            start_time = datetime.utcnow()
        
        span = {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "operation": operation,
            "start_time": start_time,
            "end_time": None,
            "duration_ms": None,
            "tags": {},
            "logs": []
        }
        
        self.active_spans[span_id] = span
        return span_id
    
    def finish_span(self, span_id: str, end_time: datetime = None):
        """结束一个span"""
        if span_id not in self.active_spans:
            return
        
        span = self.active_spans[span_id]
        if end_time is None:
            end_time = datetime.utcnow()
        
        span["end_time"] = end_time
        span["duration_ms"] = (end_time - span["start_time"]).total_seconds() * 1000
        
        # 移到已完成traces
        trace_id = span["trace_id"]
        if trace_id not in self.traces:
            self.traces[trace_id] = []
        
        self.traces[trace_id].append(span)
        del self.active_spans[span_id]
    
    def add_tag(self, span_id: str, key: str, value: Any):
        """添加标签"""
        if span_id in self.active_spans:
            self.active_spans[span_id]["tags"][key] = value
    
    def add_log(self, span_id: str, message: str, level: str = "info"):
        """添加日志"""
        if span_id in self.active_spans:
            self.active_spans[span_id]["logs"].append({
                "timestamp": datetime.utcnow(),
                "level": level,
                "message": message
            })
    
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """获取追踪数据"""
        return self.traces.get(trace_id, [])

class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.last_check_time: Dict[str, datetime] = {}
        self.check_results: Dict[str, Dict[str, Any]] = {}
    
    def add_check(self, name: str, check_func: Callable):
        """添加健康检查"""
        self.checks[name] = check_func
    
    def run_check(self, name: str) -> Dict[str, Any]:
        """运行单个健康检查"""
        if name not in self.checks:
            return {
                "name": name,
                "status": "error",
                "message": "Check not found",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            start_time = time.time()
            result = self.checks[name]()
            duration = time.time() - start_time
            
            check_result = {
                "name": name,
                "status": "healthy" if result else "unhealthy",
                "duration_ms": duration * 1000,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if isinstance(result, dict):
                check_result.update(result)
            
            self.last_check_time[name] = datetime.utcnow()
            self.check_results[name] = check_result
            
            return check_result
            
        except Exception as e:
            error_result = {
                "name": name,
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.check_results[name] = error_result
            return error_result
    
    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        results = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        overall_healthy = True
        
        for name in self.checks:
            result = self.run_check(name)
            results["checks"][name] = result
            
            if result["status"] != "healthy":
                overall_healthy = False
        
        results["status"] = "healthy" if overall_healthy else "unhealthy"
        return results

class MonitoringMiddleware:
    """监控中间件"""
    
    def __init__(self, app: FastAPI, metrics_collector: MetricsCollector):
        self.app = app
        self.metrics_collector = metrics_collector
        self.tracer = DistributedTracer()
        
        # 替换默认路由器以添加监控
        self._setup_route_monitoring()
    
    def _setup_route_monitoring(self):
        """设置路由监控"""
        for route in self.app.routes:
            if isinstance(route, APIRoute):
                # 保存原始endpoint
                original_endpoint = route.endpoint
                
                def monitored_endpoint(request: Request, *args, **kwargs):
                    # 生成追踪ID
                    trace_id = request.headers.get("X-Trace-ID", f"trace_{int(time.time()*1000)}")
                    span_id = f"span_{int(time.time()*1000)}_{id(request)}"
                    
                    # 开始span
                    self.tracer.start_span(
                        trace_id=trace_id,
                        span_id=span_id,
                        operation=f"{request.method} {route.path}",
                        start_time=datetime.utcnow()
                    )
                    
                    # 增加活跃请求数
                    self.metrics_collector.active_requests.inc()
                    
                    start_time = time.time()
                    response = None
                    status_code = 200
                    
                    try:
                        response = original_endpoint(request, *args, **kwargs)
                        return response
                    except Exception as e:
                        status_code = 500
                        raise e
                    finally:
                        # 结束span
                        self.tracer.finish_span(span_id)
                        
                        # 减少活跃请求数
                        self.metrics_collector.active_requests.dec()
                        
                        # 记录指标
                        duration = time.time() - start_time
                        self.metrics_collector.record_request(
                            method=request.method,
                            endpoint=route.path,
                            status_code=status_code,
                            duration=duration
                        )
                
                route.endpoint = monitored_endpoint

class MonitoringManager:
    """监控管理器"""
    
    def __init__(self, app: FastAPI = None):
        self.metrics_collector = MetricsCollector()
        self.tracer = DistributedTracer()
        self.health_checker = HealthChecker()
        self.middleware = None
        
        if app:
            self.setup_monitoring(app)
        
        # 启动后台指标收集
        self._start_background_collection()
    
    def setup_monitoring(self, app: FastAPI):
        """设置监控"""
        self.middleware = MonitoringMiddleware(app, self.metrics_collector)
        
        # 添加监控端点
        @app.get("/metrics")
        async def metrics_endpoint():
            return Response(
                content=self.metrics_collector.export_prometheus_metrics(),
                media_type="text/plain"
            )
        
        @app.get("/health")
        async def health_endpoint():
            return self.health_checker.run_all_checks()
        
        @app.get("/health/{check_name}")
        async def specific_health_check(check_name: str):
            return self.health_checker.run_check(check_name)
        
        @app.get("/performance")
        async def performance_endpoint():
            return {
                "performance_summary": self.metrics_collector.get_performance_summary(),
                "system_metrics": self.metrics_collector.get_system_metrics()
            }
        
        # 添加默认健康检查
        self.add_default_health_checks()
        
        logger.info("监控系统已配置完成")
    
    def add_default_health_checks(self):
        """添加默认健康检查"""
        def database_check():
            """数据库健康检查"""
            try:
                # 这里应该检查数据库连接
                return {"status": "healthy", "message": "Database connection OK"}
            except Exception as e:
                return {"status": "unhealthy", "message": str(e)}
        
        def redis_check():
            """Redis健康检查"""
            try:
                # 这里应该检查Redis连接
                return {"status": "healthy", "message": "Redis connection OK"}
            except Exception as e:
                return {"status": "unhealthy", "message": str(e)}
        
        def memory_check():
            """内存使用检查"""
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            return {
                "status": "unhealthy",
                "message": f"Memory usage too high: {memory.percent}%",
                "memory_percent": memory.percent
            }
        return {
            "status": "healthy",
            "message": f"Memory usage normal: {memory.percent}%",
            "memory_percent": memory.percent
        }
    
        def disk_check():
            """磁盘使用检查"""
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                return {
                    "status": "unhealthy",
                    "message": f"Disk usage too high: {disk.percent}%",
                    "disk_percent": disk.percent
                }
            return {
                "status": "healthy",
                "message": f"Disk usage normal: {disk.percent}%",
                "disk_percent": disk.percent
            }
        
        self.health_checker.add_check("database", database_check)
        self.health_checker.add_check("redis", redis_check)
        self.health_checker.add_check("memory", memory_check)
        self.health_checker.add_check("disk", disk_check)
    
    def _start_background_collection(self):
        """启动后台指标收集"""
        def collect_system_metrics():
            while True:
                try:
                    system_metrics = self.metrics_collector.get_system_metrics()
                    
                    # 记录系统指标
                    for key, value in system_metrics.items():
                        if key != "timestamp":
                            self.metrics_collector.record_custom_metric(
                                name=f"system_{key}",
                                value=float(value) if isinstance(value, (int, float)) else 0.0,
                                labels={"host": "localhost"}
                            )
                    
                    time.sleep(30)  # 每30秒收集一次
                    
                except Exception as e:
                    logger.error(f"后台指标收集失败: {e}")
                    time.sleep(60)  # 错误时等待更长时间
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
        logger.info("后台指标收集已启动")

@contextmanager
def trace_operation(operation_name: str, tracer: DistributedTracer = None):
    """追踪操作的上下文管理器"""
    if tracer is None:
        # 使用全局tracer
        tracer = DistributedTracer()
    
    trace_id = f"trace_{int(time.time()*1000)}"
    span_id = f"span_{int(time.time()*1000)}_{id(trace_operation)}"
    
    try:
        tracer.start_span(trace_id, span_id, operation=operation_name)
        yield span_id
    finally:
        tracer.finish_span(span_id)

# 全局监控管理器实例
monitoring_manager = MonitoringManager()

def get_monitoring_manager() -> MonitoringManager:
    """获取监控管理器"""
    return monitoring_manager