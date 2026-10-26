#!/usr/bin/env python3
"""
playwright-cli.py — playwright-cli 命令行的封装层

被 scripts/ 下的脚本导入，不单独执行。这一层只管「怎么驱动浏览器」，不管某个
平台的具体流程；平台的身份信息在 config.py，各平台的流程在各自的脚本里。

三条约定，改之前先读：

1. **命令失败就终止进程**。playwright-cli 操作失败时可能把错误写进 stdout 而
   退出码仍是 0（实测），所以除了退出码还得看输出里有没有 "### Error"。
2. **eval 的返回值可能套两层字符串**。JS 侧统一 return JSON.stringify(...)，
   外层是 --raw 的输出，内层才是 JSON.stringify 的结果——见一层剥一层。
3. **窗口控制只能走 run-code**。playwright-cli 没有 minimize 命令，只有 resize，
   改不了窗口状态，所以得发 CDP 指令。
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

LOG_PREFIX = "[playwright-cli]"


def run_pw(session: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """执行一条 playwright-cli 命令；check 为真时出错直接终止脚本。"""
    cmd = ["playwright-cli", f"-s={session}", *args]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit(f"{LOG_PREFIX} 找不到 playwright-cli，请先确认它已安装且在 PATH 中。")

    # 操作失败时 playwright-cli 可能把错误写进 stdout 而退出码仍是 0，
    # 只盯退出码会把一段 "### Error\nTimeoutError: ..." 当成正常结果收下
    if check and (proc.returncode != 0 or "### Error" in proc.stdout[:100]):
        detail = (proc.stderr or proc.stdout).strip()
        sys.exit(f"{LOG_PREFIX} 命令执行失败：{' '.join(cmd)}\n{detail}")
    return proc


def _unwrap(raw: str) -> Any:
    """剥掉两层字符串包装（见文件头第 2 条约定）。"""
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def eval_js(session: str, js: str) -> Any:
    """在页面里求值。--raw 只回结果值，不带状态码包装。"""
    return _unwrap(run_pw(session, "--raw", "eval", js).stdout.strip())


def run_code(session: str, js: str) -> Any:
    """在 Playwright 上下文里连续跑一段代码。

    与 eval 的区别：eval 只在页面里求值，一次调用做一个动作；run-code 拿到的是
    Playwright 的 page 对象，能在同一次调用里连续做多个动作，中间不留空档。
    """
    return _unwrap(run_pw(session, "--raw", "run-code", js).stdout.strip())


def list_sessions() -> set[str]:
    """列出当前活着的浏览器会话名。

    list 的输出形如「- chat.doubao:」，一个都没有时是「(no browsers)」。
    """
    try:
        proc = subprocess.run(
            ["playwright-cli", "list"], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        return set()

    names = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("- ") and line.endswith(":"):
            names.add(line[2:-1])
    return names


# 最小化 / 恢复窗口，照搬 doubao-picker 技能步骤 1 与步骤 3 的做法。
# 窗口最小化不影响后续任何命令：快照、eval、取值照常。
MINIMIZE_JS = (
    "async page => {"
    "  const cdp = await page.context().newCDPSession(page);"
    "  const r = await cdp.send('Browser.getWindowForTarget');"
    "  await cdp.send('Browser.setWindowBounds', {"
    "    windowId: r.windowId, bounds: { windowState: 'minimized' } });"
    "  return 'minimized';"
    "}"
)

RESTORE_JS = (
    "async page => {"
    "  const cdp = await page.context().newCDPSession(page);"
    "  const r = await cdp.send('Browser.getWindowForTarget');"
    "  await cdp.send('Browser.setWindowBounds', {"
    "    windowId: r.windowId, bounds: { windowState: 'normal' } });"
    "  await page.bringToFront();"
    "  return 'restored';"
    "}"
)


def minimize(session: str) -> None:
    """最小化窗口，别让它跳出来挡视线。

    失败不报错：最多是窗口多显示一会儿，不值得为这个中断整个流程。
    """
    run_pw(session, "run-code", MINIMIZE_JS, check=False)


def restore(session: str) -> None:
    """恢复窗口并带到前台，交给用户接手（登录）。

    光把 windowState 改回 normal，窗口可能还压在别的窗口后面，用户照样找不到，
    所以顺手 bringToFront。
    """
    run_pw(session, "run-code", RESTORE_JS, check=False)
