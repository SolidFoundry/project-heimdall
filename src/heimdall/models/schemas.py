# 文件路径: src/heimdall/models/schemas.py
# 完整、可直接复制替换、全中文注释

from pydantic import BaseModel, Field
from typing import List, Optional

# --- 输入模型 ---

class UserBehaviorInput(BaseModel):
    """
    用户行为数据的输入模型。
    这是我们API接收的原始数据结构。
    """
    user_id: str = Field(..., description="唯一用户标识符", example="user-12345")
    session_id: str = Field(..., description="当前会话的唯一标识符", example="session-abcde")
    browsing_history: List[str] = Field(
        ..., 
        description="用户最近浏览的商品URL列表", 
        example=[
            "https://example-ecommerce.com/product/high-end-gaming-laptop-x1",
            "https://example-ecommerce.com/product/mechanical-keyboard-rgb",
            "https://example-ecommerce.com/reviews/gaming-laptop-x1"
        ]
    )

# --- 输出模型 ---

class IntentProfile(BaseModel):
    """
    分析后生成的结构化用户意图画像。
    这是我们AI引擎的核心产出之一。
    """
    primary_intent: str = Field(..., description="推断出的主要用户意图", example="寻找高性能游戏设备")
    secondary_intents: List[str] = Field(default_factory=list, description="推断出的次要意图", example=["提升游戏体验", "比较不同品牌"])
    target_audience_segment: str = Field(..., description="用户所属的目标人群分段", example="硬核游戏玩家")
    urgency_level: float = Field(..., description="购买紧迫度评分 (0.0 到 1.0)", example=0.85)
    confidence_score: Optional[float] = Field(None, description="意图分析的置信度评分 (0.0 到 1.0)", example=0.9)
    recommendation_reason: Optional[str] = Field(None, description="大模型生成的推荐理由", example="用户表现出对高性能游戏设备的强烈需求...")

class AdRecommendation(BaseModel):
    """
    单个广告推荐的结构。
    """
    ad_id: str = Field(..., description="广告素材的唯一ID", example="AD-GAMING-MOUSE-001")
    product_id: str = Field(..., description="广告关联的商品ID", example="PROD-LOGI-G502")
    relevance_score: float = Field(..., description="与用户意图的相关性评分 (0.0 到 1.0)", example=0.95)
    ad_copy: str = Field(..., description="推荐的广告文案", example="极致精准，掌控战场！新款G502电竞鼠标，专为胜利者设计。")
    # 产品详细信息（可选字段）
    product_name: Optional[str] = Field(None, description="商品名称", example="罗技 G502 HERO 电竞鼠标")
    product_category: Optional[str] = Field(None, description="商品类别", example="电竞鼠标")
    product_brand: Optional[str] = Field(None, description="商品品牌", example="罗技")
    product_price: Optional[float] = Field(None, description="商品价格", example=299.99)

class AnalysisResultOutput(BaseModel):
    """
    API返回给客户端的最终完整结果。
    """
    request_id: str = Field(..., description="本次分析请求的唯一ID")
    intent_profile: IntentProfile = Field(..., description="分析得出的用户意图画像")
    ad_recommendations: List[AdRecommendation] = Field(..., description="基于意图推荐的广告列表")