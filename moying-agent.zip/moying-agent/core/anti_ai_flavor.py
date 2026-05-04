"""
墨影AI味消除引擎
三重去味：规则硬清洗 → AI深度润色 → 格式校准
彻底消除AI僵硬感，贴合番茄/起点真人写手风格
"""
from core.llm import LLMClient
from utils.logger import log
import re

class AntiAIFlavor:
    def __init__(self, llm: LLMClient):
        self.llm = llm
        # 全网最常见的AI模板词（读者一眼识别）
        self.ai_forbidden_words = {
            "不由得", "只见", "此刻", "闻言", "心中暗道", "下意识",
            "缓缓", "轻轻", "似乎", "仿佛", "骤然", "随即", "于是",
            "不禁", "暗自", "心中一凛", "脸色一变", "眉头一皱",
            "嘴角勾起", "眼中闪过", "心里想着", "不由得想到"
        }
        log.success("✅ AI味消除引擎初始化完成")

    def _rule_clean(self, content: str) -> str:
        """第一层：规则硬清洗（秒级处理，不耗Token）"""
        # 删除所有AI模板词
        for word in self.ai_forbidden_words:
            content = content.replace(word, "")
        
        # 切割长句（真人网文：一句话一段，最长不超过25字）
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if len(line) > 25:
                sentences = re.split(r'[。！？；]', line)
                for s in sentences:
                    s = s.strip()
                    if s:
                        new_lines.append(s)
            else:
                new_lines.append(line)
        
        # 删除空行和重复行
        final_lines = []
        for line in new_lines:
            if line and line not in final_lines[-2:]:
                final_lines.append(line)
        
        return "\n".join(final_lines)

    def _ai_refine(self, content: str) -> str:
        """第二层：AI深度润色（模拟真人语气）"""
        system_prompt = """
        你是写了10年番茄小说的老写手，把下面的内容改成纯真人风格：
        1. 1句话1段，绝对不长段落
        2. 纯口语化，像说话一样自然
        3. 对话加情绪助词（啊、哇、靠、呢、吧）
        4. 删掉所有书面语和华丽辞藻
        5. 只输出修改后的内容，不要任何解释
        """
        return self.llm.chat(system_prompt, content, temperature=0.4)

    def _format_calibrate(self, content: str) -> str:
        """第三层：格式校准（番茄平台标准格式）"""
        # 确保每段只有一句话
        lines = content.split("\n")
        final_lines = []
        for line in lines:
            line = line.strip()
            if line:
                # 强制每段结尾加标点
                if not line.endswith(("。", "！", "？", "…")):
                    line += "。"
                final_lines.append(line)
        return "\n\n".join(final_lines)  # 段间空行，符合番茄阅读习惯

    def remove_ai_flavor(self, content: str) -> str:
        """总入口：三重去AI味"""
        log.info("🔧 启动三重AI味消除...")
        content = self._rule_clean(content)
        content = self._ai_refine(content)
        content = self._format_calibrate(content)
        log.success("✅ AI味已彻底消除！")
        return content