# 文件路径: src/heimdall/services/advertising_service.py
# 完整、可直接复制替换、全中文注释

from .llm_service import LLMService, Message
from heimdall.models import schemas  # 引入我们最初定义的Pydantic模型

class AdvertisingAnalysisService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def _create_expert_prompt(self, browsing_history: list[str]) -> str:
        """为广告分析专家Agent构建初始的用户请求。"""
        history_str = "\n".join([f"- {url}" for url in browsing_history])
        
        # 这个Prompt现在更侧重于引导Agent使用工具
        return f"""
        请分析以下用户浏览历史，以洞察其购买意图并提供广告建议。
        
        用户浏览历史:
        {history_str}
        
        你的任务是：
        1.  **主动**使用`get_product_details_from_url`工具，逐一分析每个URL，以获取详细的商品信息（如价格、类别、标签）。
        2.  基于所有收集到的结构化商品信息，**综合分析**并生成最终的JSON报告。
        """

    def get_system_prompt(self) -> str:
        """定义广告分析专家Agent的核心角色和指令。"""
        # 这是整个Agent的“灵魂”！
        return """
        你是世界顶级的AI广告意图分析师。你的名字叫“Heimdall”。
        
        你的工作流程是：
        1.  接收一段用户浏览历史URL列表。
        2.  你拥有一个强大的工具箱，特别是 `get_product_details_from_url` 工具。你必须主动调用这个工具来获取每个URL背后的结构化商品数据。**不要基于URL本身进行猜测！**
        3.  在收集了所有必要的信息后，你必须将你的最终分析结果格式化为一个**严格的JSON对象**。
        4.  这个JSON对象必须严格符合以下Pydantic模型的格式：`AnalysisResultOutput`。
        
        **JSON输出格式要求:**
        {{
            "intent_profile": {{
                "primary_intent": "一个最主要的核心购买意图",
                "secondary_intents": ["其他相关的次要意图列表"],
                "target_audience_segment": "用户所属的人群分类",
                "urgency_level": "一个0.0到1.0之间的购买紧迫度评分"
            }},
            "ad_recommendations": [
                {{
                    "ad_id": "为推荐生成的唯一广告ID",
                    "product_id": "推荐商品的ID",
                    "relevance_score": "一个0.0到1.0之间的相关性评分",
                    "ad_copy": "为这个商品生成一句极具吸引力的广告文案"
                }}
            ]
        }}
        
        在最终回答时，直接输出这个JSON对象，不要包含任何额外的解释、介绍或Markdown标记。
        """

    def analyze_intent(self, session_id: str, behavior_data: schemas.UserBehaviorInput) -> dict:
        """
        执行意图分析的核心方法，驱动Agent完成任务。
        """
        initial_query = self._create_expert_prompt(behavior_data.browsing_history)
        system_prompt = self.get_system_prompt()
        
        # 调用我们已有的、强大的LLM服务来执行一个完整的Agent会话
        final_response_message = self.llm_service.process_message_with_tools(
            session_id=session_id,
            query=initial_query,
            system_prompt=system_prompt,
        )

        # Agent执行完毕后，最后的回复内容应该是我们想要的JSON字符串
        return final_response_message["content"]