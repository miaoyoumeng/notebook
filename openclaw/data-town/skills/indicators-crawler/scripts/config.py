#!/usr/bin/env python3

"""
SKILL 目录结构定义
.
├── SKILL.md
├── logs
├── references
└── scripts

"""
import logging
import os
from pathlib import Path
from datetime import datetime, timezone


SKILL_ROOT_DIR = Path(__file__).resolve().parent.parent

REFERENCES_DIR = Path(SKILL_ROOT_DIR / "references")

SCRIPTS_DIR = Path(SKILL_ROOT_DIR / "scripts")

LOGS_DIR = Path(SKILL_ROOT_DIR / "logs")

SKILL_FILE = Path(SKILL_ROOT_DIR / "SKILL.md")

# 以下是时间
TIMEZONE = "Asia/Shanghai"

def now_iso() -> str:
    """Current time in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def today_iso() -> str:
    """Current date in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")

def setup_logger(level=logging.INFO):
    """
    配置日志记录器，同时输出到文件和终端。

    参数:
        log_file_path: 日志文件的完整路径（如 './logs/crawler.log'）
        logger_name:   日志记录器名称
        level:         日志级别（默认 INFO）

    返回:
        配置好的 logger 对象
    """
    # 确保日志文件的父目录存在
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir(parents=True)

    logger_name: str = "crawler"

    log_file_path: str = Path(LOGS_DIR / "crawler.log")

    # 创建 logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # 避免重复添加 handler（如果多次调用 setup_logger）
    if logger.handlers:
        return logger

    # 文件处理器 (输出到文件)
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(level)

    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # 添加 handler
    logger.addHandler(file_handler)

    return logger

