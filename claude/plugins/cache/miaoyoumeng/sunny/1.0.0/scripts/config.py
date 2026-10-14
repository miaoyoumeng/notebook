#!/usr/bin/env python3
"""
config.py — 各 AI 平台的会话常量与共用的日志函数

被 scripts/ 下的脚本导入，不单独执行。

会话名（session）是 playwright-cli 用来隔离浏览器 profile 的：一个会话名对一份
user-data-dir，登录态就挂在那份 profile 上。所以**改这里任何一个 session 字符串，
等于换一份 profile，用户得重新登一次**——别随手动。
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:
    """一个 AI 平台在 playwright-cli 里的身份。

    只放「这个平台是谁」；「怎么判断它登没登录」是各自的校验逻辑，不在这儿。
    """

    key: str  # 命令行里用的短名，也是各处日志的前缀
    session: str  # playwright-cli 会话名
    url: str  # 网页版入口


PLATFORMS: tuple[Platform, ...] = (
    Platform("doubao", "chat.doubao", "https://www.doubao.com/chat"),
    Platform("deepseek", "chat.deepseek", "https://chat.deepseek.com/"),
    Platform("glm", "chat.glm", "https://bigmodel.cn/trialcenter/modeltrial/text"),
    Platform("kimi", "chat.kimi", "https://www.kimi.com/"),
    Platform("qwen", "chat.qwen", "https://qianwen.com/"),
    Platform("xunfei", "chat.xunfei", "https://xinghuo.xfyun.cn/desk"),
    Platform("yuanbao", "chat.yuanbao", "https://yuanbao.tencent.com/chat"),
    Platform("wenxin", "chat.wenxin", "https://wenxin.baidu.com/"),
)

PLATFORM_KEYS: tuple[str, ...] = tuple(p.key for p in PLATFORMS)
PLATFORM_BY_KEY: dict[str, Platform] = {p.key: p for p in PLATFORMS}

# 批量提问脚本各自的默认目标，一个平台一个，名字就是平台 key 的大写
DOUBAO = PLATFORM_BY_KEY["doubao"]
DEEPSEEK = PLATFORM_BY_KEY["deepseek"]
GLM = PLATFORM_BY_KEY["glm"]
KIMI = PLATFORM_BY_KEY["kimi"]
QWEN = PLATFORM_BY_KEY["qwen"]
XUNFEI = PLATFORM_BY_KEY["xunfei"]
YUANBAO = PLATFORM_BY_KEY["yuanbao"]
WENXIN = PLATFORM_BY_KEY["wenxin"]


def make_logger(prefix: str) -> Callable[[str], None]:
    """造一个带固定前缀的日志函数。

    进度日志一律走 stderr，stdout 只留给最终结果——重定向 stdout 时才拿得到
    干净的结果。flush 是为了长任务里用户能实时看到进度，而不是等进程结束。
    """

    def log(msg: str) -> None:
        print(f"{prefix} {msg}", file=sys.stderr, flush=True)

    return log
