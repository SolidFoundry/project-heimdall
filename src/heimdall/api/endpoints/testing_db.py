# 文件路径: src/heimdall/api/endpoints/testing.py
# 大模型和工具调用测试接口 (集成真实LLM服务)

import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Body, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# 直接集成LLM服务和工具注册表
import logging
import os
from openai import AsyncOpenAI
from typing import List, Dict, Any, Callable, Optional
import json
import uuid
from datetime import datetime

# 配置
class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-4dbe359e6a7c4404b4611e49a985ee2b")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "qwen-max")
    DEFAULT_SYSTEM_PROMPT = os.getenv("DEFAULT_SYSTEM_PROMPT", "你是一个通用的万能助手，名叫万能。请友好、专业地回答用户问题。")

settings = Settings()

# 导入数据库会话服务和模型
from src.heimdall.py_ai_core.services.session_service import SessionService
from src.heimdall.py_ai_core.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# 创建全局会话服务实例
session_service = SessionService()

# LLM服务
class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY, 
            base_url=settings.OPENAI_API_BASE
        )

    async def get_model_decision(self, messages: List[Dict[str, Any]], tool_schemas: List[Dict[str, Any]]):
        response = await self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            tools=tool_schemas,
            tool_choice="auto",
        )
        return response.choices[0].message

    async def get_summary_from_tool_results(self, messages_for_summary: List[Dict[str, Any]]):
        response = await self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages_for_summary,
        )
        return response.choices[0].message.content

llm_service = LLMService()

# 工具注册表
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: List[Dict[str, Any]] = []

    def register(self, func: Callable):
        tool_name = func.__name__
        self.tools[tool_name] = func

        # 生成schema
        import inspect
        doc = inspect.getdoc(func)
        description = doc.split("\n")[0] if doc else ""

        parameters = {"type": "object", "properties": {}, "required": []}
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            param_type = "string"
            if hasattr(param.annotation, '__name__'):
                type_mapping = {"str": "string", "int": "integer", "float": "number", "bool": "boolean"}
                param_type = type_mapping.get(param.annotation.__name__, "string")
            
            parameters["properties"][name] = {
                "type": param_type,
                "description": f"参数: {name}",
            }
            if param.default is inspect.Parameter.empty:
                parameters["required"].append(name)

        tool_schema = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
            },
        }
        self.tool_schemas.append(tool_schema)
        return func

    def get_tool(self, name: str) -> Callable | None:
        return self.tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        return self.tool_schemas

tool_registry = ToolRegistry()

def tool(func: Callable):
    return tool_registry.register(func)

# 导入并注册工具
import math

# 安全的数学函数白名单
SAFE_MATH_OPS = {
    "abs": abs, "acos": math.acos, "asin": math.asin, "atan": math.atan,
    "atan2": math.atan2, "ceil": math.ceil, "cos": math.cos, "cosh": math.cosh,
    "degrees": math.degrees, "exp": math.exp, "fabs": math.fabs, "floor": math.floor,
    "fmod": math.fmod, "frexp": math.frexp, "hypot": math.hypot, "ldexp": math.ldexp,
    "log": math.log, "log10": math.log10, "modf": math.modf, "pow": math.pow,
    "radians": math.radians, "sin": math.sin, "sinh": math.sinh, "sqrt": math.sqrt,
    "tan": math.tan, "tanh": math.tanh, "pi": math.pi, "e": math.e,
}

@tool
async def calculate(expression: str) -> str:
    """一个安全的计算器，用于执行数学表达式。"""
    try:
        result = eval(expression, {"__builtins__": None}, SAFE_MATH_OPS)
        return str(result)
    except Exception as e:
        return f"计算表达式 '{expression}' 时发生错误: {e}"

@tool
async def get_current_weather(city: str, unit: str = "celsius") -> str:
    """获取指定城市的当前天气信息。"""
    return f"{city}的天气是晴朗, 25度 {unit}."

@tool
async def get_current_datetime() -> str:
    """返回当前服务器的日期和时间。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)

# 创建API路由器
router = APIRouter()

# --- 请求和响应模型 ---

class LLMTestRequest(BaseModel):
    """大模型测试请求"""
    prompt: str = Field(..., description="发送给大模型的提示词", example="你好，请介绍一下你自己")
    session_id: Optional[str] = Field(None, description="会话ID，用于保持对话上下文", example="user_123")
    system_prompt: Optional[str] = Field(None, description="可选的系统提示词", example="你是一个专业的AI助手")
    temperature: Optional[float] = Field(0.7, description="温度参数，控制回答的随机性", ge=0.0, le=2.0)

class LLMTestResponse(BaseModel):
    """大模型测试响应"""
    request_id: str = Field(..., description="请求的唯一标识符")
    prompt: str = Field(..., description="原始提示词")
    response: str = Field(..., description="大模型的回答")
    model_used: str = Field(..., description="使用的模型名称")
    session_id: Optional[str] = Field(None, description="会话ID")
    timestamp: str = Field(..., description="响应时间戳")

class ToolTestRequest(BaseModel):
    """工具调用测试请求"""
    tool_name: str = Field(..., description="要测试的工具名称", example="calculate")
    tool_args: Dict[str, Any] = Field(..., description="工具参数", example={"expression": "2 + 2 * 3"})

class ToolTestResponse(BaseModel):
    """工具调用测试响应"""
    request_id: str = Field(..., description="请求的唯一标识符")
    tool_name: str = Field(..., description="工具名称")
    tool_args: Dict[str, Any] = Field(..., description="工具参数")
    result: str = Field(..., description="工具执行结果")
    success: bool = Field(..., description="是否执行成功")
    error_message: Optional[str] = Field(None, description="错误信息（如果有）")
    timestamp: str = Field(..., description="响应时间戳")

class SimpleToolInfo(BaseModel):
    """简单工具信息"""
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    parameters: Dict[str, Any] = Field(..., description="工具参数")

class ToolListResponse(BaseModel):
    """可用工具列表响应"""
    tools: List[SimpleToolInfo] = Field(..., description="所有可用工具的信息")
    total_count: int = Field(..., description="工具总数")

class LLMWithToolsRequest(BaseModel):
    """大模型带工具调用请求"""
    query: str = Field(..., description="用户查询")
    session_id: Optional[str] = Field(None, description="会话ID，用于保持对话上下文")
    system_prompt: Optional[str] = Field(None, description="可选的系统提示词")

# --- API端点 ---

@router.post("/llm-test", response_model=LLMTestResponse, summary="测试大模型基础能力")
async def test_llm_capability(request: LLMTestRequest, db: AsyncSession = Depends(get_db)):
    """
    测试大模型的基础对话能力，支持历史记录和上下文传递。
    
    **功能:**
    - 支持会话ID，保持对话上下文
    - 自动包含历史记录
    - 获取模型的原始回答
    - 可调整温度参数控制回答的随机性
    """
    logger.info("收到大模型测试请求: %s, 会话ID: %s", request.prompt[:100], request.session_id)
    
    try:
        # 生成或使用提供的会话ID
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # 获取系统提示词
        system_prompt = await session_service.get_or_create_session_prompt(session_id, db, request.system_prompt)
        
        # 构建消息列表，包含历史记录
        history_messages = await session_service.get_history(session_id, db)
        current_user_message = {"role": "user", "content": request.prompt}
        
        messages = [{"role": "system", "content": system_prompt}] + history_messages + [current_user_message]
        
        # 调用真实的LLM服务
        response = await llm_service.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=request.temperature
        )
        
        response_content = response.choices[0].message.content
        
        # 保存对话历史
        assistant_message = {"role": "assistant", "content": response_content}
        await session_service.update_history(session_id, [current_user_message, assistant_message], db)
        
        return LLMTestResponse(
            request_id=str(uuid.uuid4()),
            prompt=request.prompt,
            response=response_content,
            model_used=settings.MODEL_NAME,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.exception("大模型测试请求处理失败")
        raise HTTPException(status_code=500, detail=f"大模型调用失败: {str(e)}")

@router.post("/tool-test", response_model=ToolTestResponse, summary="测试单个工具调用")
async def test_tool_capability(request: ToolTestRequest):
    """
    测试单个工具的调用能力。
    
    **功能:**
    - 直接调用指定的工具
    - 传入指定参数
    - 返回工具执行结果
    """
    logger.info("收到工具测试请求: %s, 参数: %s", request.tool_name, request.tool_args)
    
    try:
        # 获取工具
        tool_func = tool_registry.get_tool(request.tool_name)
        if not tool_func:
            raise HTTPException(status_code=404, detail=f"工具 '{request.tool_name}' 不存在")
        
        # 执行工具
        try:
            result = await tool_func(**request.tool_args)
            success = True
            error_message = None
            logger.info("工具测试执行成功: %s", request.tool_name)
        except Exception as e:
            result = f"工具执行失败: {str(e)}"
            success = False
            error_message = str(e)
            logger.error("工具测试执行失败: %s, 错误: %s", request.tool_name, str(e))
        
        return ToolTestResponse(
            request_id=str(uuid.uuid4()),
            tool_name=request.tool_name,
            tool_args=request.tool_args,
            result=str(result),
            success=success,
            error_message=error_message,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("工具测试请求处理失败")
        raise HTTPException(status_code=500, detail=f"工具调用失败: {str(e)}")

@router.get("/tools", response_model=ToolListResponse, summary="获取所有可用工具")
async def get_available_tools():
    """
    获取所有已注册的工具信息。
    
    **功能:**
    - 列出所有可用的工具
    - 显示每个工具的名称和描述
    - 显示参数要求
    """
    logger.info("收到获取工具列表请求")
    
    try:
        # 获取所有工具的schema
        tool_schemas = tool_registry.get_all_schemas()
        
        # 转换为我们的格式
        tools_info = []
        for schema in tool_schemas:
            tool_func = schema["function"]
            tool = SimpleToolInfo(
                name=tool_func["name"],
                description=tool_func["description"],
                parameters=tool_func["parameters"]
            )
            tools_info.append(tool)
        
        logger.info("成功获取工具列表，共 %d 个工具", len(tools_info))
        
        return ToolListResponse(
            tools=tools_info,
            total_count=len(tools_info)
        )
        
    except Exception as e:
        logger.exception("获取工具列表失败")
        raise HTTPException(status_code=500, detail=f"获取工具列表失败: {str(e)}")

@router.post("/llm-with-tools", summary="测试大模型带工具调用")
async def test_llm_with_tools(request: LLMWithToolsRequest, db: AsyncSession = Depends(get_db)):
    """
    测试大模型结合工具调用的完整能力，支持历史记录和上下文传递。
    
    **功能:**
    - 支持会话ID，保持对话上下文
    - 自动包含历史记录
    - 大模型分析用户查询
    - 决定是否需要调用工具
    - 执行工具调用（如果需要）
    - 生成最终回答
    """
    logger.info("收到大模型带工具调用测试请求: %s, 会话ID: %s", request.query, request.session_id)
    
    try:
        import json
        import asyncio
        from openai.types.chat import ChatCompletionMessage
        
        # 生成或使用提供的会话ID
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # 获取系统提示词
        system_prompt = await session_service.get_or_create_session_prompt(session_id, db, request.system_prompt)
        
        # 构建消息列表，包含历史记录
        history_messages = await session_service.get_history(session_id, db)
        current_user_message = {"role": "user", "content": request.query}
        
        messages = [{"role": "system", "content": system_prompt}] + history_messages + [current_user_message]
        
        # 获取工具schemas
        tool_schemas = tool_registry.get_all_schemas()
        
        # 调用LLM获取决策
        model_message = await llm_service.get_model_decision(messages, tool_schemas)
        
        if not model_message:
            raise HTTPException(status_code=500, detail="与大模型通信失败。")
        
        # 根据是否有工具调用进行不同处理
        if model_message.tool_calls:
            # 有工具调用的情况
            logger.info("大模型决定调用工具: %s", [tc.function.name for tc in model_message.tool_calls])
            
            # 执行工具调用
            assistant_message = model_message.model_dump(exclude_unset=True)
            tasks = [execute_real_tool(tc) for tc in model_message.tool_calls]
            tool_results = await asyncio.gather(*tasks)
            
            # 构建总结消息
            messages_for_summary = messages + [assistant_message] + tool_results
            final_answer = await llm_service.get_summary_from_tool_results(messages_for_summary)
            
            # 构建返回结果
            tool_calls_info = []
            for i, tool_call in enumerate(model_message.tool_calls):
                tool_calls_info.append({
                    "tool_name": tool_call.function.name,
                    "tool_args": json.loads(tool_call.function.arguments),
                    "tool_call_id": tool_call.id
                })
            
            execution_steps = [
                {"step": f"分析用户查询: {request.query}", "status": "success"},
                {"step": f"检测到工具调用需求: {[tc.function.name for tc in model_message.tool_calls]}", "status": "success"},
                *[{"step": f"调用工具 {tool_calls_info[i]['tool_name']}: {tool_calls_info[i]['tool_args']}", "status": "success"} for i in range(len(tool_calls_info))],
                {"step": f"生成最终回答", "status": "success"}
            ]
            
        else:
            # 直接回答的情况
            logger.info("大模型提供直接回答")
            final_answer = model_message.content or "抱歉，我无法回答。"
            tool_calls_info = []
            execution_steps = [
                {"step": f"分析用户查询: {request.query}", "status": "success"},
                {"step": "未检测到工具调用需求", "status": "success"},
                {"step": "生成直接回答", "status": "success"}
            ]
        
        # 保存对话历史
        messages_to_save = [current_user_message]
        if model_message.tool_calls:
            assistant_message = model_message.model_dump(exclude_unset=True)
            messages_to_save.append(assistant_message)
            messages_to_save.extend(tool_results)
        
        final_assistant_message = {"role": "assistant", "content": final_answer}
        messages_to_save.append(final_assistant_message)
        
        await session_service.update_history(session_id, messages_to_save, db)
        
        return {
            "request_id": str(uuid.uuid4()),
            "query": request.query,
            "final_answer": final_answer,
            "tool_calls": tool_calls_info,
            "execution_steps": execution_steps,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.exception("大模型带工具调用测试请求处理失败")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


async def execute_real_tool(tool_call):
    """执行真实的工具调用"""
    tool_name = tool_call.function.name
    logger.info("正在执行工具: '%s'", tool_name)
    
    tool_to_call = tool_registry.get_tool(tool_name)
    if not tool_to_call:
        error_msg = f"错误: 找不到名为 '{tool_name}' 的工具。"
        logger.error("尝试调用一个不存在的工具: '%s'", tool_name)
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": error_msg,
        }
    
    try:
        tool_args_str = tool_call.function.arguments
        tool_args = json.loads(tool_args_str)
        logger.debug("调用工具 '%s' 的参数: %s", tool_name, tool_args)
        
        result = await tool_to_call(**tool_args)
        str_result = str(result)
        logger.info("成功执行工具 '%s'", tool_name)
        
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": str_result,
        }
    except Exception as e:
        logger.exception("执行工具 '%s' 时失败", tool_name)
        return {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": tool_name,
            "content": f"执行失败: {e}",
        }