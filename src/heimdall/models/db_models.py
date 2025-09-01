# --- START OF FILE heimdall/models/db_models.py (针对广告推荐场景优化) ---

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, func
from src.heimdall.core.database import Base


class UserSession(Base):
    """
    用户会话数据模型，对应 'user_sessions' 表。
    用于存储用户会话的元数据，包括用户信息和会话设定。
    """

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    
    # 会话和用户信息
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    
    # 用户画像信息
    user_segment = Column(String(100), nullable=True)  # 用户分群
    preferences = Column(JSON, nullable=True)  # 用户偏好设置
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<UserSession(id={self.id}, session_id='{self.session_id}', user_id='{self.user_id}')>"


class UserBehavior(Base):
    """
    用户行为数据模型，对应 'user_behaviors' 表。
    用于存储用户的行为历史记录，如浏览、搜索、点击等。
    """

    __tablename__ = "user_behaviors"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    
    # 行为类型和内容
    behavior_type = Column(String(50), nullable=False)  # 'view', 'search', 'click', 'purchase'
    behavior_data = Column(JSON, nullable=False)  # 行为的具体数据
    
    # 意图分析结果
    detected_intent = Column(String(255), nullable=True)
    intent_confidence = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserBehavior(id={self.id}, session_id='{self.session_id}', type='{self.behavior_type}')>"


class IntentAnalysis(Base):
    """
    意图分析结果数据模型，对应 'intent_analyses' 表。
    用于存储AI对用户意图的分析结果。
    """

    __tablename__ = "intent_analyses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    
    # 意图分析结果
    primary_intent = Column(String(255), nullable=False)
    secondary_intents = Column(JSON, nullable=True)  # 次要意图列表
    target_audience_segment = Column(String(100), nullable=False)
    urgency_level = Column(Float, nullable=False)  # 0.0 到 1.0
    
    # 分析元数据
    analysis_model = Column(String(100), nullable=True)  # 使用的AI模型
    analysis_confidence = Column(Float, nullable=True)  # 整体置信度
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<IntentAnalysis(id={self.id}, session_id='{self.session_id}', intent='{self.primary_intent}')>"


class AdRecommendation(Base):
    """
    广告推荐数据模型，对应 'ad_recommendations' 表。
    用于存储为用户生成的广告推荐结果。
    """

    __tablename__ = "ad_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    analysis_id = Column(Integer, nullable=True)  # 关联的意图分析ID
    
    # 推荐内容
    ad_id = Column(String(255), nullable=False)
    product_id = Column(String(255), nullable=False)
    relevance_score = Column(Float, nullable=False)  # 相关性评分 0.0 到 1.0
    ad_copy = Column(Text, nullable=False)  # 推荐的广告文案
    
    # 推荐元数据
    recommendation_reason = Column(Text, nullable=True)  # 推荐理由
    position = Column(Integer, nullable=True)  # 推荐位置
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AdRecommendation(id={self.id}, ad_id='{self.ad_id}', score={self.relevance_score})>"


class ChatSession(Base):
    """
    聊天会话数据模型，对应 'chat_sessions' 表。
    用于存储聊天会话的元数据，包括系统提示词等。
    """

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    system_prompt = Column(Text, nullable=True)
    user_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}')>"


class ChatMessage(Base):
    """
    聊天消息数据模型，对应 'chat_messages' 表。
    用于存储聊天对话的消息历史。
    """

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'tool', 'system'
    content = Column(Text, nullable=False)  # JSON格式的消息内容
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id='{self.session_id}', role='{self.role}')>"


# --- END OF FILE heimdall/models/db_models.py ---