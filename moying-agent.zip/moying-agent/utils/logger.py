"""
墨影日志系统
彩色控制台日志 + 按天轮转文件日志
"""
from loguru import logger
from config import Config
import sys

# 移除默认日志
logger.remove()

# 控制台日志（彩色）
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    colorize=True
)

# 文件日志（按天轮转，保留7天）
logger.add(
    Config.LOG_DIR / "moying_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    rotation="1 day",
    retention="7 days",
    encoding="utf-8"
)

log = logger