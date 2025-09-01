# �ļ�·��: src/heimdall/services/advertising_service.py
# ��������ֱ�Ӹ����滻��ȫ����ע��

from .llm_service import LLMService, Message
from src.heimdall.models import schemas  # ����������������Pydanticģ��

class AdvertisingAnalysisService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def _create_expert_prompt(self, browsing_history: list[str]) -> str:
        """Ϊ������ר��Agent������ʼ���û�����"""
        history_str = "\n".join([f"- {url}" for url in browsing_history])
        
        # ���Prompt���ڸ�����������Agentʹ�ù���
        return f"""
        ����������û������ʷ���Զ����乺����ͼ���ṩ��潨�顣
        
        �û������ʷ:
        {history_str}
        
        ��������ǣ�
        1.  **����**ʹ��`get_product_details_from_url`���ߣ���һ����ÿ��URL���Ի�ȡ��ϸ����Ʒ��Ϣ����۸���𡢱�ǩ����
        2.  ���������ռ����Ľṹ����Ʒ��Ϣ��**�ۺϷ���**���������յ�JSON���档
        """

    def get_system_prompt(self) -> str:
        """���������ר��Agent�ĺ��Ľ�ɫ��ָ�"""
        # ��������Agent�ġ���ꡱ��
        return """
        �������綥����AI�����ͼ����ʦ��������ֽС�Heimdall����
        
        ��Ĺ��������ǣ�
        1.  ����һ���û������ʷURL�б���
        2.  ��ӵ��һ��ǿ��Ĺ����䣬�ر��� `get_product_details_from_url` ���ߡ�������������������������ȡÿ��URL����Ľṹ����Ʒ���ݡ�**��Ҫ����URL�������в²⣡**
        3.  ���ռ������б�Ҫ����Ϣ������뽫������շ��������ʽ��Ϊһ��**�ϸ��JSON����**��
        4.  ���JSON��������ϸ��������Pydanticģ�͵ĸ�ʽ��`AnalysisResultOutput`��
        
        **JSON�����ʽҪ��:**
        {{
            "intent_profile": {{
                "primary_intent": "һ������Ҫ�ĺ��Ĺ�����ͼ",
                "secondary_intents": ["������صĴ�Ҫ��ͼ�б�"],
                "target_audience_segment": "�û���������Ⱥ����",
                "urgency_level": "һ��0.0��1.0֮��Ĺ�����ȶ�����"
            }},
            "ad_recommendations": [
                {{
                    "ad_id": "Ϊ�Ƽ����ɵ�Ψһ���ID",
                    "product_id": "�Ƽ���Ʒ��ID",
                    "relevance_score": "һ��0.0��1.0֮������������",
                    "ad_copy": "Ϊ�����Ʒ����һ�伫���������Ĺ���İ�"
                }}
            ]
        }}
        
        �����ջش�ʱ��ֱ��������JSON���󣬲�Ҫ�����κζ���Ľ��͡����ܻ�Markdown��ǡ�
        """

    def analyze_intent(self, session_id: str, behavior_data: schemas.UserBehaviorInput) -> dict:
        """
        ִ����ͼ�����ĺ��ķ���������Agent�������
        """
        initial_query = self._create_expert_prompt(behavior_data.browsing_history)
        system_prompt = self.get_system_prompt()
        
        # �����������еġ�ǿ���LLM������ִ��һ��������Agent�Ự
        final_response_message = self.llm_service.process_message_with_tools(
            session_id=session_id,
            query=initial_query,
            system_prompt=system_prompt,
        )

        # Agentִ����Ϻ����Ļظ�����Ӧ����������Ҫ��JSON�ַ���
        return final_response_message["content"]