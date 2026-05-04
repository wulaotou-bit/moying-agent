"""
墨影文件管理插件
功能：
1. 自动创建目录
2. 保存TXT/JSON/Excel
3. 文件自动备份（防止覆盖）
"""
from config import Config
from utils.logger import log
import json
import pandas as pd
from datetime import datetime
import os

def _auto_backup(file_path: str):
    """
    自动备份文件：如果文件存在，重命名为 原文件名_时间戳.后缀
    :param file_path: 文件路径
    """
    if file_path.exists():
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.parent / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            os.rename(str(file_path), str(backup_path))
            log.info(f"文件已备份: {backup_path}")
        except Exception as e:
            log.warning(f"文件备份失败: {e}，将覆盖原文件")

def save_txt(content: str, filename: str, backup: bool = True):
    """
    保存TXT文件
    :param content: 文件内容
    :param filename: 文件名
    :param backup: 是否自动备份
    """
    file_path = Config.OUTPUT_DIR / filename
    if backup:
        _auto_backup(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    log.info(f"TXT文件已保存: {file_path}")

def save_json(data: dict, filename: str, backup: bool = True):
    """
    保存JSON文件
    :param data: 数据字典
    :param filename: 文件名
    :param backup: 是否自动备份
    """
    file_path = Config.OUTPUT_DIR / filename
    if backup:
        _auto_backup(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"JSON文件已保存: {file_path}")

def save_excel(df: pd.DataFrame, filename: str, sheet_name: str = "Sheet1", backup: bool = True):
    """
    保存Excel文件
    :param df: DataFrame数据
    :param filename: 文件名
    :param sheet_name: 工作表名
    :param backup: 是否自动备份
    """
    file_path = Config.OUTPUT_DIR / filename
    if backup:
        _auto_backup(file_path)
    df.to_excel(file_path, sheet_name=sheet_name, index=False)
    log.info(f"Excel文件已保存: {file_path}")