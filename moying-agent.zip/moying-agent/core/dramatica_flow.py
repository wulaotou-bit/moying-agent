"""
墨影Dramatica故事工程学模块
功能：
1. 生成完整故事骨架（因果链+角色关系+伏笔清单+时间线）
2. 自动审计章节（OOC/伏笔/时间线/因果）
3. 自动修订不合格章节
"""
import json
from core.llm import LLMClient
from core.memory import NovelLongTermMemory
from config import Config
from utils.logger import log

class DramaticaSkeleton:
    def __init__(self, llm: LLMClient, memory: NovelLongTermMemory):
        self.llm = llm
        self.memory = memory
        self.skeleton_path = Config.OUTPUT_DIR / "dramatica_skeleton.json"

    def build_full_skeleton(self, core_idea: str) -> dict:
        """生成完整Dramatica故事骨架"""
        log.info("🏗️ 正在构建Dramatica故事骨架...")
        system_prompt = """
        你是顶级Dramatica故事架构师，专为番茄/起点网文设计。
        请严格按照以下JSON格式输出，**无任何多余文字**：
        {
            "novel_title": "书名",
            "worldview": "世界观（100字以内）",
            "character_relations": [
                {
                    "name": "角色名",
                    "identity": "身份",
                    "personality": "性格（3个关键词）",
                    "motivation": "核心动机",
                    "arc": "角色弧光（起点→转折点→终点）",
                    "relations": [{"target": "目标角色", "type": "关系类型（敌/友/恋/父/子等）"}]
                }
            ],
            "causal_chain": [
                {
                    "chapter_id": 章节号,
                    "cause": "起因",
                    "process": "经过",
                    "effect": "结果",
                    "next_chapter_trigger": "触发下一章的钩子"
                }
            ],
            "foreshadow_list": [
                {
                    "foreshadow_id": 伏笔号,
                    "content": "伏笔内容",
                    "plant_chapter": "埋设章节",
                    "recover_chapter": "回收章节",
                    "importance": "重要性（高/中/低）"
                }
            ],
            "timeline": [
                {
                    "date": "日期（如：大靖三年三月初一）",
                    "event": "事件",
                    "chapter_id": 关联章节号
                }
            ]
        }
        """
        user_prompt = f"""
        核心创意：{core_idea}
        小说类型：{Config.NOVEL_TYPE}
        总章节数：{Config.TOTAL_CHAPTERS}
        要求：
        1. 番茄爆款节奏：3章一小高潮，10章一大高潮
        2. 因果链强逻辑，无漏洞
        3. 伏笔清单明确，高重要性伏笔必须在10章内回收
        4. 时间线严谨，无冲突
        """
        try:
            result = self.llm.chat(system_prompt, user_prompt, temperature=0.1)
            # 提取JSON（防止AI输出多余文字）
            json_start = result.find("{")
            json_end = result.rfind("}") + 1
            skeleton = json.loads(result[json_start:json_end])
            
            # 保存骨架到文件
            with open(self.skeleton_path, "w", encoding="utf-8") as f:
                json.dump(skeleton, f, ensure_ascii=False, indent=2)
            
            # 保存骨架到记忆库
            self.memory.save_worldview(skeleton.get("worldview", "通用小说世界观"))
            for char in skeleton.get("character_relations", []):
                self.memory.save_character(char)
            for fs in skeleton.get("foreshadow_list", []):
                self.memory.save_foreshadow(fs["plant_chapter"], fs["content"])
            
            log.success("✅ Dramatica故事骨架构建完成！")
            return skeleton
        except Exception as e:
            log.error(f"❌ Dramatica故事骨架构建失败: {e}")
            # 返回默认骨架
            return {
                "novel_title": Config.NOVEL_TITLE,
                "worldview": "通用小说世界观",
                "character_relations": [],
                "causal_chain": [],
                "foreshadow_list": [],
                "timeline": []
            }

class DramaticaAuditor:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def audit_chapter(self, skeleton: dict, chapter_info: dict, content: str) -> dict:
        """自动审计章节"""
        log.info(f"🔍 正在审计章节: {chapter_info.get('title', '未知章节')}")
        system_prompt = """
        你是严格的Dramatica剧情审计师，专为番茄/起点网文设计。
        请严格按照以下JSON格式输出，**无任何多余文字**：
        {
            "pass": true/false,
            "ooc_check": {
                "pass": true/false,
                "issues": ["问题1", "问题2"]
            },
            "foreshadow_check": {
                "pass": true/false,
                "issues": ["问题1", "问题2"],
                "missed_foreshadows": ["遗漏的伏笔1", "遗漏的伏笔2"]
            },
            "timeline_check": {
                "pass": true/false,
                "issues": ["问题1", "问题2"]
            },
            "causal_check": {
                "pass": true/false,
                "issues": ["问题1", "问题2"]
            },
            "fix_suggestions": "具体的修订建议（100字以内）"
        }
        要求：
        1. 检查是否OOC（角色崩坏）
        2. 检查是否回收了本章应该回收的伏笔
        3. 检查时间线是否正确
        4. 检查因果逻辑是否通顺
        """
        user_prompt = f"""
        【故事骨架】：{json.dumps(skeleton, ensure_ascii=False)}
        【章节信息】：{json.dumps(chapter_info, ensure_ascii=False)}
        【章节内容】：{content}
        """
        try:
            result = self.llm.chat(system_prompt, user_prompt, temperature=0.1)
            json_start = result.find("{")
            json_end = result.rfind("}") + 1
            report = json.loads(result[json_start:json_end])
            
            if report["pass"]:
                log.success(f"✅ 章节审计通过！")
            else:
                log.warning(f"⚠️ 章节审计不通过！问题：{report['fix_suggestions']}")
            
            return report
        except Exception as e:
            log.error(f"❌ 章节审计失败: {e}")
            return {"pass": True, "fix_suggestions": "审计报告解析失败，默认通过"}

class DramaticaReviser:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def revise_chapter(self, content: str, audit_report: dict, skeleton: dict) -> str:
        """自动修订不合格章节"""
        log.info("🔧 正在自动修订章节...")
        system_prompt = """
        你是顶级番茄/起点网文修订师，严格按照审计报告和Dramatica骨架修订章节。
        要求：
        1. 修复所有审计问题
        2. 保持原有的番茄爆款节奏
        3. 保持原有的零AI味风格
        4. 只输出修订后的章节内容，**无任何多余文字**
        """
        user_prompt = f"""
        【原章节内容】：{content}
        【审计报告】：{json.dumps(audit_report, ensure_ascii=False)}
        【故事骨架】：{json.dumps(skeleton, ensure_ascii=False)}
        """
        try:
            revised = self.llm.chat(system_prompt, user_prompt, temperature=0.4)
            log.success("✅ 章节修订完成！")
            return revised
        except Exception as e:
            log.error(f"❌ 章节修订失败: {e}")
            return content