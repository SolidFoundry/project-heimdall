#!/usr/bin/env python3
"""
增强版服务器启动脚本 - 复用现有的heimdall模块功能
集成真实的大模型请求、数据库存储会话、工具注册功能
"""

import sys
import os
import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 导入现有的heimdall模块功能
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uvicorn

# 导入项目日志系统
from heimdall.core.logging_config import setup_logging
from heimdall.core.structured_logging import RequestIdMiddleware

# 导入现有的服务
from heimdall.services.llm_service import llm_service
from heimdall.services.session_service import session_service
from heimdall.tools.registry import tool_registry
from heimdall.tools.math_tools import calculate
from heimdall.tools.general_tools import get_current_weather, get_current_datetime
from heimdall.core.config import settings
from heimdall.core.database import get_db

# 导入advertising、products、enterprise和hybrid路由
from heimdall.api.endpoints.advertising import router as advertising_router
from heimdall.api.endpoints.products import router as products_router
from heimdall.api.endpoints.enterprise_recommendations import (
    router as enterprise_router,
)
from heimdall.api.endpoints.hybrid_recommendations import router as hybrid_router

# 设置日志系统
setup_logging()

# 获取日志记录器
logger = logging.getLogger("heimdall.server")
access_logger = logging.getLogger("heimdall.access")
api_logger = logging.getLogger("heimdall.api")

# 创建FastAPI应用
app = FastAPI(
    title="Project Heimdall - Enterprise AI Intent Advertising Engine",
    description="企业级AI意图识别与广告推荐引擎 - 集成真实大模型功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加请求ID中间件
app.add_middleware(RequestIdMiddleware)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 挂载路由
app.include_router(advertising_router)
app.include_router(products_router)
app.include_router(enterprise_router)
app.include_router(hybrid_router)


# 定义数据模型
class Message(BaseModel):
    role: str
    content: str


class LLMTestRequest(BaseModel):
    messages: List[Message]
    system_prompt: Optional[str] = None
    session_id: Optional[str] = None
    temperature: Optional[float] = 0.7


class ToolTestRequest(BaseModel):
    tool_name: str
    tool_args: Dict[str, Any]


class LLMWithToolsRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    system_prompt: Optional[str] = None


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    start_time = datetime.now()
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # 添加请求ID到请求状态中
    request.state.request_id = request_id

    # 记录请求开始
    client_host = request.client.host if request.client else "unknown"
    api_logger.info(
        f"API请求开始: {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params),
            "client_host": client_host,
            "user_agent": request.headers.get("user-agent", "unknown"),
        },
    )

    # 处理请求
    try:
        response = await call_next(request)

        # 计算处理时间
        duration = (datetime.now() - start_time).total_seconds() * 1000

        # 记录请求完成
        api_logger.info(
            f"API请求完成: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": {"ms": round(duration, 2)},
                "client_host": client_host,
            },
        )

        # 同时记录到访问日志
        access_logger.info(
            f"API请求完成: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": {"ms": round(duration, 2)},
                "client_host": client_host,
            },
        )

        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as e:
        # 计算处理时间
        duration = (datetime.now() - start_time).total_seconds() * 1000

        # 记录请求失败
        api_logger.error(
            f"API请求失败: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "duration": {"ms": round(duration, 2)},
                "client_host": client_host,
            },
        )

        # 同时记录到访问日志
        access_logger.error(
            f"API请求失败: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "duration": {"ms": round(duration, 2)},
                "client_host": client_host,
            },
        )

        raise


# 首页端点
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """项目首页"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问项目首页", extra={"request_id": request_id})

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "title": "Project Heimdall - 企业级AI广告推荐引擎",
            "version": "1.0.0",
        },
    )


# 测试平台端点
@app.get("/test", response_class=HTMLResponse)
async def frontend_home(request: Request):
    """前端测试界面主页"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问前端测试界面", extra={"request_id": request_id})

    return templates.TemplateResponse(
        "test.html",
        {"request": request, "title": "前端调试测试页面", "version": "1.0.0"},
    )


# JavaScript测试页面
@app.get("/js-test", response_class=HTMLResponse)
async def js_test_page(request: Request):
    """JavaScript测试页面"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问JavaScript测试页面", extra={"request_id": request_id})

    return templates.TemplateResponse(
        "js-test.html",
        {"request": request, "title": "JavaScript测试", "version": "1.0.0"},
    )


# 前端诊断工具
@app.get("/diagnose", response_class=HTMLResponse)
async def diagnose_page(request: Request):
    """前端诊断工具"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问前端诊断页面", extra={"request_id": request_id})

    return templates.TemplateResponse(
        "diagnose.html",
        {"request": request, "title": "前端诊断工具", "version": "1.0.0"},
    )


# API测试页面
@app.get("/api-test", response_class=HTMLResponse)
async def api_test_page(request: Request):
    """API测试页面"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问API测试页面", extra={"request_id": request_id})

    return templates.TemplateResponse(
        "api-test.html",
        {"request": request, "title": "API测试页面", "version": "1.0.0"},
    )


# JavaScript类测试页面
@app.get("/js-class-test", response_class=HTMLResponse)
async def js_class_test_page(request: Request):
    """JavaScript类测试页面"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问JavaScript类测试页面", extra={"request_id": request_id})

    return templates.TemplateResponse(
        "js-class-test.html",
        {"request": request, "title": "JavaScript类测试", "version": "1.0.0"},
    )


# 简单JavaScript测试页面
@app.get("/simple-js-test", response_class=HTMLResponse)
async def simple_js_test_page(request: Request):
    """简单JavaScript测试页面"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问简单JavaScript测试页面", extra={"request_id": request_id})

    return templates.TemplateResponse(
        "simple-js-test.html",
        {"request": request, "title": "简单JavaScript测试", "version": "1.0.0"},
    )


# 企业级前端界面
@app.get("/enterprise", response_class=HTMLResponse)
async def enterprise_frontend(request: Request):
    """企业级前端界面"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问企业级前端界面", extra={"request_id": request_id})

    return templates.TemplateResponse(
        "enterprise.html",
        {
            "request": request,
            "title": "Project Heimdall - 企业级AI推荐系统",
            "version": "1.0.0",
        },
    )


# AI广告引擎测试平台
@app.get("/index", response_class=HTMLResponse)
async def index_frontend(request: Request):
    """AI广告引擎测试平台"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问AI广告引擎测试平台", extra={"request_id": request_id})

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Project Heimdall - AI广告引擎测试平台",
            "version": "1.0.0",
        },
    )


# API根端点
@app.get("/api")
async def api_root(request: Request):
    """API根端点"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("访问API根端点", extra={"request_id": request_id})

    return {
        "message": "Welcome to Project Heimdall - 真实大模型集成版",
        "version": "1.0.0",
        "description": "Enterprise AI Intent Advertising Engine with Real LLM Integration",
        "docs_url": "/docs",
        "frontend_url": "/",
        "status": "running",
        "request_id": request_id,
    }


# 健康检查端点
@app.get("/api/v1/health")
async def health(request: Request):
    """健康检查端点"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("健康检查请求", extra={"request_id": request_id})

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "request_id": request_id,
    }


# 保留原有的健康检查端点作为备用
@app.get("/health")
async def health_legacy(request: Request):
    """健康检查端点（兼容性）"""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("健康检查请求（兼容性）", extra={"request_id": request_id})

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "request_id": request_id,
    }


# 真实LLM测试接口
@app.post("/api/v1/test/llm")
async def test_llm(request: LLMTestRequest, http_request: Request):
    """测试真实的大模型基础能力"""
    request_id = getattr(http_request.state, "request_id", "unknown")

    # 将消息格式转换为标准格式
    if request.messages:
        user_content = request.messages[-1].content
        message_count = len(request.messages)
    else:
        user_content = "empty"
        message_count = 0

    api_logger.info(
        f"LLM测试请求: {user_content}",
        extra={
            "request_id": request_id,
            "message_count": message_count,
            "system_prompt": request.system_prompt,
            "session_id": request.session_id,
        },
    )

    try:
        # 生成或使用提供的会话ID
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"

        # 获取数据库会话
        async for db in get_db():
            # 获取系统提示词
            system_prompt = await session_service.get_or_create_session_prompt(
                session_id, db, request.system_prompt
            )

            # 构建消息列表，包含历史记录
            history_messages = await session_service.get_history(session_id, db)
            current_user_message = {"role": "user", "content": user_content}

            messages = (
                [{"role": "system", "content": system_prompt}]
                + history_messages
                + [current_user_message]
            )

            # 调用真实的LLM服务
            response = await llm_service.chat_completion(
                model=settings.MODEL_NAME,
                messages=messages,
                temperature=request.temperature,
            )

            response_content = response.choices[0].message.content

            # 保存对话历史
            assistant_message = {"role": "assistant", "content": response_content}
            await session_service.update_history(
                session_id, [current_user_message, assistant_message], db
            )

            # 构建响应
            result = {
                "response": response_content,
                "model": settings.MODEL_NAME,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": (
                    response.usage.total_tokens
                    if response.usage
                    else len(user_content.split())
                ),
                "messages_count": message_count,
                "session_id": session_id,
                "request_id": request_id,
            }

            api_logger.info(
                f"LLM响应生成成功",
                extra={
                    "request_id": request_id,
                    "response_length": len(response_content),
                    "tokens_used": result["tokens_used"],
                },
            )

            return result

    except Exception as e:
        api_logger.error(f"LLM处理失败: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=f"大模型调用失败: {str(e)}")


# 工具调用测试接口
@app.post("/api/v1/test/tools")
async def test_tools(request: ToolTestRequest, http_request: Request):
    """测试单个工具的调用能力"""
    request_id = getattr(http_request.state, "request_id", "unknown")

    api_logger.info(
        f"工具测试请求: {request.tool_name}, 参数: {request.tool_args}",
        extra={"request_id": request_id},
    )

    try:
        # 获取工具
        tool_func = tool_registry.get_tool(request.tool_name)
        if not tool_func:
            raise HTTPException(
                status_code=404, detail=f"工具 '{request.tool_name}' 不存在"
            )

        # 执行工具
        try:
            result = await tool_func(**request.tool_args)
            success = True
            error_message = None
            api_logger.info("工具测试执行成功: %s", request.tool_name)
        except Exception as e:
            result = f"工具执行失败: {str(e)}"
            success = False
            error_message = str(e)
            api_logger.error(
                "工具测试执行失败: %s, 错误: %s", request.tool_name, str(e)
            )

        return {
            "request_id": request_id,
            "tool_name": request.tool_name,
            "tool_args": request.tool_args,
            "result": str(result),
            "success": success,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(
            f"工具测试请求处理失败: {str(e)}", extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"工具调用失败: {str(e)}")


# 获取可用工具列表
@app.get("/api/v1/tools")
async def get_tools(request: Request):
    """获取所有可用工具"""
    request_id = getattr(request.state, "request_id", "unknown")

    api_logger.info("获取工具列表请求", extra={"request_id": request_id})

    try:
        tool_schemas = tool_registry.get_all_schemas()

        tools_info = []
        for schema in tool_schemas:
            tool_func = schema["function"]
            tools_info.append(
                {
                    "name": tool_func["name"],
                    "description": tool_func["description"],
                    "parameters": tool_func["parameters"],
                }
            )

        return {
            "tools": tools_info,
            "total_count": len(tools_info),
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        api_logger.error(
            f"获取工具列表失败: {str(e)}", extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=f"获取工具列表失败: {str(e)}")


# 大模型带工具调用接口
@app.post("/api/v1/test/llm-with-tools")
async def test_llm_with_tools(request: LLMWithToolsRequest, http_request: Request):
    """测试大模型结合工具调用的完整能力"""
    request_id = getattr(http_request.state, "request_id", "unknown")

    api_logger.info(
        f"大模型带工具调用测试请求: {request.query}, 会话ID: {request.session_id}",
        extra={"request_id": request_id},
    )

    try:
        import asyncio
        from openai.types.chat import ChatCompletionMessage

        # 生成或使用提供的会话ID
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"

        # 获取数据库会话
        async for db in get_db():
            # 获取系统提示词
            system_prompt = await session_service.get_or_create_session_prompt(
                session_id, db, request.system_prompt
            )

            # 构建消息列表，包含历史记录
            history_messages = await session_service.get_history(session_id, db)
            current_user_message = {"role": "user", "content": request.query}

            messages = (
                [{"role": "system", "content": system_prompt}]
                + history_messages
                + [current_user_message]
            )

            # 获取工具schemas
            tool_schemas = tool_registry.get_all_schemas()

            # 调用LLM获取决策
            model_message = await llm_service.get_model_decision(messages, tool_schemas)

            if not model_message:
                raise HTTPException(status_code=500, detail="与大模型通信失败。")

            # 根据是否有工具调用进行不同处理
            if model_message.tool_calls:
                # 有工具调用的情况
                api_logger.info(
                    f"大模型决定调用工具: {[tc.function.name for tc in model_message.tool_calls]}",
                    extra={"request_id": request_id},
                )

                # 执行工具调用
                assistant_message = model_message.model_dump(exclude_unset=True)
                tasks = [execute_real_tool(tc) for tc in model_message.tool_calls]
                tool_results = await asyncio.gather(*tasks)

                # 构建总结消息
                messages_for_summary = messages + [assistant_message] + tool_results
                final_answer = await llm_service.get_summary_from_tool_results(
                    messages_for_summary
                )

                # 构建返回结果
                tool_calls_info = []
                for i, tool_call in enumerate(model_message.tool_calls):
                    tool_calls_info.append(
                        {
                            "tool_name": tool_call.function.name,
                            "tool_args": json.loads(tool_call.function.arguments),
                            "tool_call_id": tool_call.id,
                        }
                    )

                execution_steps = [
                    {"step": f"分析用户查询: {request.query}", "status": "success"},
                    {
                        "step": f"检测到工具调用需求: {[tc.function.name for tc in model_message.tool_calls]}",
                        "status": "success",
                    },
                    *[
                        {
                            "step": f"调用工具 {tool_calls_info[i]['tool_name']}: {tool_calls_info[i]['tool_args']}",
                            "status": "success",
                        }
                        for i in range(len(tool_calls_info))
                    ],
                    {"step": f"生成最终回答", "status": "success"},
                ]

                # 保存对话历史
                messages_to_save = [current_user_message]
                messages_to_save.append(assistant_message)
                messages_to_save.extend(tool_results)

                final_assistant_message = {"role": "assistant", "content": final_answer}
                messages_to_save.append(final_assistant_message)

                await session_service.update_history(session_id, messages_to_save, db)

            else:
                # 直接回答的情况
                api_logger.info("大模型提供直接回答", extra={"request_id": request_id})
                final_answer = model_message.content or "抱歉，我无法回答。"
                tool_calls_info = []
                execution_steps = [
                    {"step": f"分析用户查询: {request.query}", "status": "success"},
                    {"step": "未检测到工具调用需求", "status": "success"},
                    {"step": "生成直接回答", "status": "success"},
                ]

                # 保存对话历史
                messages_to_save = [current_user_message]
                final_assistant_message = {"role": "assistant", "content": final_answer}
                messages_to_save.append(final_assistant_message)

                await session_service.update_history(session_id, messages_to_save, db)

            return {
                "request_id": request_id,
                "query": request.query,
                "final_answer": final_answer,
                "tool_calls": tool_calls_info,
                "execution_steps": execution_steps,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        api_logger.error(
            f"大模型带工具调用测试请求处理失败: {str(e)}",
            extra={"request_id": request_id},
        )
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


async def execute_real_tool(tool_call):
    """执行真实的工具调用"""
    tool_name = tool_call.function.name
    api_logger.info(f"正在执行工具: '{tool_name}'")

    tool_to_call = tool_registry.get_tool(tool_name)
    if not tool_to_call:
        error_msg = f"错误: 找不到名为 '{tool_name}' 的工具。"
        api_logger.error(f"尝试调用一个不存在的工具: '{tool_name}'")
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": error_msg,
        }

    try:
        tool_args_str = tool_call.function.arguments
        tool_args = json.loads(tool_args_str)
        api_logger.debug(f"调用工具 '{tool_name}' 的参数: {tool_args}")

        result = await tool_to_call(**tool_args)
        str_result = str(result)
        api_logger.info(f"成功执行工具 '{tool_name}'")

        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": str_result,
        }
    except Exception as e:
        api_logger.error(f"执行工具 '{tool_name}' 时失败: {str(e)}")
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": f"执行失败: {e}",
        }


# 错误处理
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"404错误: {request.url.path}", extra={"request_id": request_id})

    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found", "request_id": request_id},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"500错误: {str(exc)}", extra={"request_id": request_id})

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": request_id},
    )


if __name__ == "__main__":
    print("Starting Project Heimdall Enhanced Server with Real LLM Integration...")
    print("=" * 70)
    print("Server URL: http://127.0.0.1:8003")
    print("API Docs: http://127.0.0.1:8003/docs")
    print("Health Check: http://127.0.0.1:8003/health")
    print("Available Endpoints:")
    print("  - POST /api/v1/test/llm - 真实大模型测试")
    print("  - POST /api/v1/test/tools - 工具调用测试")
    print("  - GET /api/v1/tools - 获取工具列表")
    print("  - POST /api/v1/test/llm-with-tools - 大模型带工具调用")
    print("  - POST /api/v1/hybrid-recommendations/recommendations - AI混合推荐")
    print("  - POST /api/v1/hybrid-recommendations/analyze-intent - AI意图分析")
    print("=" * 70)
    
    # Debug: Check LLM service configuration
    print("LLM Service Configuration:")
    print(f"  API Key present: {bool(settings.OPENAI_API_KEY)}")
    print(f"  Base URL: {settings.OPENAI_API_BASE}")
    print(f"  Model: {settings.MODEL_NAME}")
    
    print("功能特性:")
    print("- [OK] 真实大模型集成 (通义千问)")
    print("- [OK] 数据库会话存储")
    print("- [OK] 工具注册和调用")
    print("- [OK] 智能历史截断")
    print("- [OK] 结构化日志记录")
    print("- [OK] 请求追踪和监控")
    print("- [OK] AI意图识别集成")
    print("- [OK] 混合推荐系统")
    print("=" * 70)

    uvicorn.run(app, host="127.0.0.1", port=8003, reload=False, log_level="info")
