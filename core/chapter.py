"""
墨影章节生成器
基于Dramatica骨架约束生成，自动去AI味，自动保存记忆，字数控制
"""
from core.llm import LLMClient
from core.memory import NovelLongTermMemory
from core.anti_ai_flavor import AntiAIFlavor
from config import Config
from utils.logger import log
import json

class ChapterGenerator:
    def __init__(self, memory: NovelLongTermMemory):
        self.memory = memory
        self.llm = LLMClient(memory)
        self.anti_ai = AntiAIFlavor(self.llm)
        log.success("✅ 章节生成器加载完成")

    def write_in_dramatica(self, chapter_info: dict, chapter_id: int, dramatica_skeleton: dict) -> str:
        """严格在Dramatica骨架内生成章节"""
        target_words = Config.DAILY_WORD_COUNT // 10
        
        system_prompt = f"""
        你是顶级番茄网文写手，严格遵守以下规则：
        1. 完全按照Dramatica骨架创作，绝对不偏离设定
        2. 短句口语化，1句话1段，无AI味
        3. 每500字一个小爽点，结尾必须留钩子
        4. 严格遵守人设，回收该章应该回收的伏笔
        5. 目标字数：{target_words}字

        【Dramatica骨架】
        {json.dumps(dramatica_skeleton, ensure_ascii=False)}
        """
        user_prompt = f"写第{chapter_id}章：{json.dumps(chapter_info, ensure_ascii=False)}"
        
        # 生成初稿
        content = self.llm.chat(system_prompt, user_prompt, temperature=0.7, max_tokens=3000)
        
        # 字数检查和补全/精简
        word_count = len(content)
        if word_count < target_words * 0.8:
            log.warning(f"章节字数不足，目标{target_words}，实际{word_count}，正在补全...")
            content += self.llm.chat("继续写下面的内容，保持风格一致，不要重复", content, temperature=0.7)
        elif word_count > target_words * 1.2:
            log.warning(f"章节字数过多，目标{target_words}，实际{word_count}，正在精简...")
            content = self.llm.chat("精简下面的内容，保留核心情节和爽点", content, temperature=0.3)
        
        # 基础质检
        content = self._quality_check(content)
        # 三重去AI味
        content = self.anti_ai.remove_ai_flavor(content)
        # 保存章节记忆
        self.memory.save_chapter(chapter_id, chapter_info["title"], content)
        # 保存本章伏笔
        if "foreshadowing" in chapter_info and chapter_info["foreshadowing"]:
            self.memory.save_foreshadow(chapter_id, chapter_info["foreshadowing"])
        
        return content

    def _quality_check(self, content: str) -> str:
        """基础质检：修正错别字、语病、强化爽点"""
        prompt = "修正以下内容的错别字和语病，强化爽点，保持原文风格"
        return self.llm.chat(prompt, content, temperature=0.3, max_tokens=4000)