"""
墨影评论分析模块
功能：分析读者情绪、喜爱角色/剧情，给出写作建议
"""
from core.llm import LLMClient
from utils.logger import log
import json

class CommentAnalyzer:
    def __init__(self):
        self.llm = LLMClient()

    def analyze(self, comments: list) -> str:
        """智能分析读者评论"""
        log.info("📝 正在分析读者评论...")
        if not comments:
            return "暂无评论，无法分析"
        
        system_prompt = """
        你是专业网文评论分析师，分析读者评论并给出写作建议：
        1. 读者整体情绪（正面/负面/中性）
        2. 读者最喜欢的角色和剧情
        3. 读者最不满意的地方
        4. 具体的写作优化建议
        分点清晰，语言简洁
        """
        user_prompt = f"评论数据：{json.dumps(comments, ensure_ascii=False)}"
        
        result = self.llm.chat(system_prompt, user_prompt, temperature=0.3)
        log.success("✅ 评论分析完成！")
        return result