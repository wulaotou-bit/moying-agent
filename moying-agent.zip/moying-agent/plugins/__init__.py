"""
墨影插件库
暴露核心类供外部调用
"""
from plugins.browser_core import BrowserCore
from plugins.browser_spider import NovelSpider
from plugins.file_manager import save_txt, save_json, save_excel

__all__ = ["BrowserCore", "NovelSpider", "save_txt", "save_json", "save_excel"]