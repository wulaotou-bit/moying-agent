"""
墨影核心业务模块
暴露核心类供外部调用
"""
from core.llm import LLMClient
from core.memory import NovelLongTermMemory
from core.anti_ai_flavor import AntiAIFlavor
from core.outline import OutlineGenerator
from core.chapter import ChapterGenerator
from core.dramatica_flow import DramaticaSkeleton, DramaticaAuditor, DramaticaReviser
from core.comment_analyze import CommentAnalyzer
from core.data_analyze import DataAnalyzer

__all__ = [
    "LLMClient",
    "NovelLongTermMemory",
    "AntiAIFlavor",
    "OutlineGenerator",
    "ChapterGenerator",
    "DramaticaSkeleton",
    "DramaticaAuditor",
    "DramaticaReviser",
    "CommentAnalyzer",
    "DataAnalyzer"
]