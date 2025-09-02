# py_ai_core/services/llm_service.py

import logging
from openai import AsyncOpenAI
from typing import List, Dict, Any
from src.heimdall.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        """
        构造函数，初始化与大模型服务的异步客户端。
        """
        logger.info("正在初始化大模型服务 (LLMService)...")

        if not settings.LLM_API_KEY or not settings.LLM_API_BASE:
            logger.error(
                "关键配置 LLM_API_KEY 或 LLM_API_BASE 未设置！服务可能无法正常工作。"
            )

        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY, base_url=settings.LLM_API_BASE
        )
        logger.info(
            "大模型服务客户端已成功创建，目标地址: %s", settings.LLM_API_BASE
        )

    def _get_client(self):
        """
        获取或重新创建配置正确的OpenAI客户端
        """
        # 检查配置是否有效
        if not settings.LLM_API_KEY or not settings.LLM_API_BASE:
            logger.error("LLM服务配置缺失: API_KEY或API_BASE未设置")
            raise ValueError("LLM服务配置缺失")
        
        # 检查客户端是否存在且配置正确
        if (not hasattr(self, 'client') or 
            not self.client or 
            not self.client.base_url or 
            not self.client.api_key):
            
            logger.warning("重新创建LLM客户端...")
            
            # 重新创建客户端
            self.client = AsyncOpenAI(
                api_key=settings.LLM_API_KEY, 
                base_url=settings.LLM_API_BASE
            )
            logger.info("LLM客户端已创建，目标地址: %s", settings.LLM_API_BASE)
        
        return self.client

    async def get_model_decision(
        self, messages: List[Dict[str, Any]], tool_schemas: List[Dict[str, Any]]
    ):
        """
        请求大模型，让其根据完整的消息历史决定是直接回答还是调用工具。
        """
        logger.info("正在向大模型请求决策...")
        logger.debug(
            "发送给大模型的决策请求内容: messages=%s, tools=%s", messages, tool_schemas
        )

        # 获取配置正确的客户端
        client = self._get_client()
        
        # Debug: Check client configuration before making the call
        logger.debug("LLM Client config - API Key present: %s", bool(client.api_key))
        logger.debug("LLM Client config - Base URL: %s", client.base_url)
        logger.debug("LLM Client config - Model: %s", settings.MODEL_NAME)

        try:
            response = await client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            model_message = response.choices[0].message
            logger.info("成功从大模型获取决策响应。")
            logger.debug("大模型决策响应详情: %s", model_message)
            return model_message

        except Exception as e:
            logger.exception("调用大模型决策 API 时发生严重错误。")
            raise

    async def get_summary_from_tool_results(
        self,
        messages_for_summary: List[Dict[str, Any]],
    ):
        """
        在工具执行后，将包含工具结果的完整上下文发回给大模型，让其进行总结。
        :param messages_for_summary: 完整的对话历史，包含用户问题、AI思考、工具结果等。
        :return: 大模型生成的最终总结性回复字符串。
        """
        logger.info("正在向大模型请求对工具结果进行总结...")
        logger.debug("发送给大模型的总结请求内容: %s", messages_for_summary)

        # 获取配置正确的客户端
        client = self._get_client()
        
        # Debug: Check client configuration before making the call
        logger.debug("LLM Client config - API Key present: %s", bool(client.api_key))
        logger.debug("LLM Client config - Base URL: %s", client.base_url)
        logger.debug("LLM Client config - Model: %s", settings.MODEL_NAME)

        try:
            response = await client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=messages_for_summary,
            )
            summary_content = response.choices[0].message.content
            logger.info("成功从大模型获取总结性回复。")
            logger.debug("大模型总结回复详情: %.200s...", summary_content)
            return summary_content

        except Exception as e:
            logger.exception("调用大模型总结 API 时发生严重错误。")
            return "抱歉，我在总结工具执行结果时遇到了一个问题。"

    async def chat_completion(self, **kwargs):
        """
        通用的聊天补全方法，用于直接调用LLM API
        """
        logger.info("正在执行直接LLM聊天补全调用...")
        
        # 获取配置正确的客户端
        client = self._get_client()
        
        # Debug: Check client configuration before making the call
        logger.debug("LLM Client config - API Key present: %s", bool(client.api_key))
        logger.debug("LLM Client config - Base URL: %s", client.base_url)
        logger.debug("LLM Client config - Model: %s", settings.MODEL_NAME)
        
        try:
            response = await client.chat.completions.create(**kwargs)
            logger.info("成功执行直接LLM聊天补全调用。")
            return response
        except Exception as e:
            logger.exception("直接LLM聊天补全调用失败。")
            raise


# 创建一个全局单例
llm_service = LLMService()
