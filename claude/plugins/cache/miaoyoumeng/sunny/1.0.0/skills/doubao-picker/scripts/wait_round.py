#!/usr/bin/env python3
"""
轮询等待豆包这一轮回答收尾，单段最长 60 秒

为什么需要这个脚本：
等待生成本质上是个循环，而一条 shell 命令要跑完才把输出交出来——
循环跑满 5 分钟，用户那边就是 5 分钟毫无反应，看起来像卡死。
所以等待必须分段：本脚本一次只轮询 --segment 秒（默认 60），
把读到的每次状态打印出来就返回，由上层决定要不要再来一段，
段与段之间向用户报进度。

判据为什么长这样（2026-10 实测，都是踩过的坑）：
- 只看最后一条 assistant 消息。全局抓 .md-box-root 会回退到上一轮的容器，
  读到它已完成的状态，把新轮次误判成结束。
- 主判据是开场白计时器的折叠属性，不是 data-streaming：豆包的节奏是
  开场白 → 执行工具 → 写正文，工具执行期间正文容器根本不存在，
  data-streaming 给不出"还在跑"的信号，单看它会取到半截回答。
- 一轮可能挂多个 .md-box-root（实测 4 个），所以只判断"有没有还在跑的"，
  不按容器数量数轮次。

用法：
    uv run python skills/doubao-picker/scripts/wait_round.py
    uv run python skills/doubao-picker/scripts/wait_round.py --segment 120 --interval 5

输出：每次探询的状态各占一行，最后一行是退出时的状态。
退出码：0 = 已收尾（done），可以取值；1 = 这一段没等到，可以再来一段；2 = 出错。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time

PROBE_JS = (
    "(() => {"
    "  const msgs = [...document.querySelectorAll('[data-message-role=assistant]')];"
    "  if (!msgs.length) return 'wait:no-message';"
    "  const last = msgs[msgs.length - 1];"
    "  const el = last.querySelector('[data-testid=preamble-elapsed]');"
    "  if (el) return el.getAttribute('data-message-content-collapsed') === 'true'"
    " ? 'done' : 'wait:running';"
    "  const boxes = [...last.querySelectorAll('.md-box-root')];"
    "  if (!boxes.length) return 'wait:no-container';"
    "  return boxes.some(b => b.dataset.streaming === 'true') ? 'wait:streaming' : 'suspect';"
    "})()"
)


def probe(session: str) -> str:
    """读一次状态。命令出错时按退出码 2 结束。"""
    try:
        proc = subprocess.run(
            ["playwright-cli", "-s", session, "--raw", "eval", PROBE_JS],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("找不到 playwright-cli 命令，请先确认它已安装且在 PATH 中。", file=sys.stderr)
        sys.exit(2)

    if proc.returncode != 0:
        print(f"playwright-cli 执行失败：{(proc.stderr or proc.stdout).strip()}", file=sys.stderr)
        sys.exit(2)

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(f"playwright-cli 返回的不是合法 JSON：{proc.stdout[:200]}", file=sys.stderr)
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="轮询等待豆包这一轮回答收尾")
    parser.add_argument(
        "--session",
        default="chat.doubao",
        help="playwright-cli 的会话名（默认 chat.doubao）",
    )
    parser.add_argument(
        "--segment",
        type=int,
        default=60,
        help="单段最长秒数（默认 60；别调太大，段内用户看不到进度）",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="两次探询之间的间隔秒数（默认 5）",
    )
    args = parser.parse_args()

    deadline = time.monotonic() + args.segment

    while True:
        if time.monotonic() >= deadline:
            print(f"这一段 {args.segment} 秒没等到收尾，可以再来一段", file=sys.stderr)
            sys.exit(1)

        status = probe(args.session)
        print(status, flush=True)

        if status == "done":
            sys.exit(0)

        # 没有开场白计时器兜底的情况：等一个间隔复读，两次都是 suspect 才采信
        if status == "suspect":
            time.sleep(args.interval)
            again = probe(args.session)
            print(again, flush=True)
            if again in ("suspect", "done"):
                sys.exit(0)
            continue

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
