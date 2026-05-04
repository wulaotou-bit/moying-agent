from pipeline import MoyingAgent
from utils.logger import log

if __name__ == "__main__":
    # 核心创意（可修改为你自己的）
    CORE_IDEA = "女频权谋搞笑文，女主穿越成冷宫废后，靠吐槽和厨艺逆袭"
    
    try:
        agent = MoyingAgent()
        agent.run_dramatica_flow(core_idea=CORE_IDEA, platform="fanqie")
    except KeyboardInterrupt:
        log.warning("✅ 用户手动停止程序")
    except Exception as e:
        log.critical(f"💥 程序崩溃: {str(e)}")
        with open("crash_report.txt", "w", encoding="utf-8") as f:
            f.write(str(e))