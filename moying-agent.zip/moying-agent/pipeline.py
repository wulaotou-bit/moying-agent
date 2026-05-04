"""
墨影Dramatica-Flow全流程编排
严格执行：骨架构建 → 约束生成 → 自动审计 → 自动修订 → 发布 → 评论分析 → 数据监控
"""
from core.llm import LLMClient
from core.outline import OutlineGenerator
from core.chapter import ChapterGenerator
from core.memory import NovelLongTermMemory
from core.dramatica_flow import DramaticaSkeleton, DramaticaAuditor, DramaticaReviser
from core.comment_analyze import CommentAnalyzer
from core.data_analyze import DataAnalyzer
from plugins.browser_spider import NovelSpider
from plugins.file_manager import save_txt, save_json
from utils.logger import log
from config import Config
import json

class MoyingAgent:
    def __init__(self):
        # 初始化核心组件
        self.memory = NovelLongTermMemory(Config.NOVEL_TITLE)
        self.llm = LLMClient(self.memory)
        self.memory.set_llm(self.llm)  # 注入LLM客户端
        
        # Dramatica核心三组件
        self.dramatica = DramaticaSkeleton(self.llm, self.memory)
        self.auditor = DramaticaAuditor(self.llm)
        self.reviser = DramaticaReviser(self.llm)
        
        # 业务组件
        self.chapter = ChapterGenerator(self.memory)
        self.comment_analyze = CommentAnalyzer()
        self.data_analyze = DataAnalyzer()
        
        log.success("🎉 墨影Agent【Dramatica-Flow终极模式】初始化完成！")

    def run_dramatica_flow(self, core_idea: str, platform: str = "fanqie"):
        """运行完整Dramatica-Flow流程"""
        # 检查是否有未完成的进度（断点续传）
        progress_path = Config.OUTPUT_DIR / "进度.json"
        completed_chapters = 0
        if progress_path.exists():
            try:
                with open(progress_path, "r", encoding="utf-8") as f:
                    progress = json.load(f)
                completed_chapters = progress.get("completed_chapters", 0)
                log.info(f"🔄 恢复进度：已完成{completed_chapters}章")
            except Exception as e:
                log.warning(f"进度文件读取失败: {e}，将从头开始")
        
        # Step1: 构建Dramatica故事骨架（锁死所有逻辑）
        skeleton = self.dramatica.build_full_skeleton(core_idea)
        
        # Step2: 生成详细大纲
        outline = OutlineGenerator(self.memory).generate(core_idea)
        
        # Step3: 初始化爬虫
        spider = NovelSpider(platform)
        spider.login()
        
        # Step4: 逐章执行创作闭环
        log.info("🚀 启动逐章创作闭环")
        total_chapters = sum(len(vol["chapters"]) for vol in outline["volume_structure"])
        
        for volume in outline["volume_structure"]:
            for chapter in volume["chapters"]:
                chap_id = chapter["chapter_id"]
                
                # 跳过已完成的章节（断点续传）
                if chap_id <= completed_chapters:
                    log.info(f"⏭️ 跳过第{chap_id}章（已完成）")
                    continue
                
                chap_title = chapter["title"]
                log.info(f"\n======= 第{chap_id}/{total_chapters}章：{chap_title} =======")

                # 创作-审计-修订 闭环
                max_retry = 3
                content = ""
                for retry in range(max_retry):
                    content = self.chapter.write_in_dramatica(chapter, chap_id, skeleton)
                    report = self.auditor.audit_chapter(skeleton, chapter, content)
                    if report["pass"]:
                        log.success(f"✅ 第{chap_id}章审计通过！（重试{retry}次）")
                        break
                    log.warning(f"⚠️ 第{chap_id}章审计不通过，开始修订...")
                    content = self.reviser.revise_chapter(content, report, skeleton)
                else:
                    log.critical(f"💥 第{chap_id}章连续{max_retry}次审计失败，跳过")
                    continue

                # 保存+发布
                save_txt(content, f"第{chap_id}章_{chap_title}.txt")
                
                # 可选：人类审核环节
                # log.info(f"第{chap_id}章已生成，请审核内容（输入y发布，n跳过）")
                # choice = input().strip().lower()
                # if choice == 'y':
                #     spider.publish_chapter(chap_title, content)
                # else:
                #     log.info(f"跳过发布第{chap_id}章")
                
                spider.publish_chapter(chap_title, content)
                
                # 保存进度
                completed_chapters = chap_id
                with open(progress_path, "w", encoding="utf-8") as f:
                    json.dump({"completed_chapters": completed_chapters}, f)
        
        # Step5: 评论分析
        log.info("\n=== 启动评论分析 ===")
        comments = spider.crawl_comments()
        save_json(comments, "评论数据.json")
        comment_report = self.comment_analyze.analyze(comments)
        save_txt(comment_report, "评论分析报告.txt")
        log.info("✅ 评论分析完成")
        
        # Step6: 数据监控
        log.info("\n=== 启动数据监控 ===")
        raw_data = spider.crawl_data()
        data_report = self.data_analyze.run_full_analysis(raw_data)
        save_json(data_report, "数据分析报告.json")
        save_txt(data_report["suggestions"], "写作优化建议.txt")
        log.info("✅ 数据监控完成")
        
        # 关闭资源
        spider.close()
        
        # 清除进度文件
        if progress_path.exists():
            progress_path.unlink()
        
        log.success("\n🏆 【Dramatica-Flow】全流程完美完成！")
        log.info(f"📊 写作优化建议：\n{data_report['suggestions']}")