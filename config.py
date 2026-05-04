import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
BASE_PATH = Path(__file__).parent

# 安全校验
required_vars = ["DEEPSEEK_API_KEY", "FANQIE_USERNAME"]
for var in required_vars:
    if not os.getenv(var) or "你的" in os.getenv(var, ""):
        raise Exception("❌ 请配置 .env 文件中的真实信息")

class Config:
    # AI配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
    MODEL_NAME = os.getenv("MODEL_NAME")

    # 路径
    OUTPUT_DIR = BASE_PATH / "output"
    COOKIE_DIR = BASE_PATH / "cookies"
    LOG_DIR = BASE_PATH / "logs"
    for d in [OUTPUT_DIR, COOKIE_DIR, LOG_DIR]:
        d.mkdir(exist_ok=True)

    # 小说配置
    NOVEL_TITLE = os.getenv("NOVEL_TITLE")
    NOVEL_TYPE = os.getenv("NOVEL_TYPE")

    # 平台账号
    PLATFORM_ACCOUNTS = {
        "fanqie": {
            "user": os.getenv("FANQIE_USERNAME"),
            "pwd": os.getenv("FANQIE_PASSWORD")
        }
    }

    # 浏览器
    BROWSER_HEADLESS = False