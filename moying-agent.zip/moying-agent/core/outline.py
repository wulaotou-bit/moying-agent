"""
墨影大纲生成器
基于番茄爆款节奏生成详细大纲
"""
from core.llm import LLMClient
from core.memory import NovelLongTermMemory
from config import Config
import json
from utils.logger import log

class OutlineGenerator:
    def __init__(self, memory: NovelLongTermMemory):
        self.memory = memory
        self.llm = LLMClient(memory)
        self.save_path = Config.OUTPUT_DIR / "大纲.json"

    def generate(self, core_idea: str) -> dict:
        """生成番茄爆款节奏大纲"""
        log.info("📝 正在生成小说大纲...")
        system_prompt = """
        你是顶级番茄网文大纲师，输出标准JSON格式，无任何多余文字：
        {
            "novel_title": "书名",
            "worldview": "世界观（100字以内）",
            "volume_structure": [
                {
                    "volume_name": "第一卷：卷名",
                    "chapters": [
                        {
                            "chapter_id": 1,
                            "title": "章节标题",
                            "conflict": "核心冲突",
                            "cool_point": "爽点",
                            "foreshadowing": "伏笔",
                            "hook": "章末钩子",
                            "word_count": 2000
                        }
                    ]
                }
            ]
        }
        要求：番茄爆款节奏，3章一小高潮，10章一大高潮
        """
        user_prompt = f"""
        核心创意：{core_idea}
        小说类型：{Config.NOVEL_TYPE}
        总章节数：{Config.TOTAL_CHAPTERS}
        """
        
        result = self.llm.chat(system_prompt, user_prompt, temperature=0.7)
        
        # 提取JSON（防止AI输出多余文字）
        try:
            json_start = result.find("{")
            json_end = result.rfind("}") + 1
            outline = json.loads(result[json_start:json_end])
        except:
            log.error("大纲JSON解析失败，使用默认大纲")
            outline = {
                "novel_title": Config.NOVEL_TITLE,
                "worldview": f"{Config.NOVEL_TYPE}世界观，符合番茄小说阅读习惯",
                "volume_structure": [
                    {
                        "volume_name": "第一卷",
                        "chapters": [
                            {
                                "chapter_id": 1,
                                "title": "第一章",
                                "conflict": "核心冲突",
                                "cool_point": "爽点",
                                "foreshadowing": "伏笔",
                                "hook": "钩子",
                                "word_count": 2000
                            }
                        ]
                    }
                ]
            }
        
        # 保存大纲到文件
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(outline, f, ensure_ascii=False, indent=2)
        
        # 保存世界观到记忆
        worldview = outline.get("worldview", f"{Config.NOVEL_TYPE}世界观，符合番茄小说阅读习惯")
        self.memory.save_worldview(worldview)
        
        log.success("✅ 小说大纲生成完成！")
        return outline