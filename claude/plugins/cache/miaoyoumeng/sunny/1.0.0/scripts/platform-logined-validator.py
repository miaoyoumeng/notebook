#!/usr/bin/env python3
"""
platform-logined-validator.py — 校验各 AI 平台网页版的登录态，未登录就等着用户登完

用法（在插件根目录执行，即 pyproject.toml 所在那一层）：

    # 校验全部平台
    uv run python scripts/platform-logined-validator.py --platform=all

    # 只校验其中一个，或同时指定几个（可重复出现）
    uv run python scripts/platform-logined-validator.py --platform=doubao
    uv run python scripts/platform-logined-validator.py --platform=doubao --platform=kimi

    # 结果以 JSON 输出
    uv run python scripts/platform-logined-validator.py --platform=all --json

输出：过程日志走 stderr，结论走 stdout——每个平台一行「[平台] 已登录完成」。

行为：

- `--platform` **必填**：填 `all` 校验全部，填平台名只校验指定的那个，
  写多个平台名就按给的次数重复指定
- 打开浏览器后**先最小化**，不让窗口跳出来挡视线
- **已登录** → 报「已登录完成」，随即关掉那个平台的浏览器（窗口全程最小化，不打扰）
- **未登录** → 把窗口**恢复出来**、提示用户在里面自己登，然后轮询等着；
  登完报「已登录完成」，同样关掉那个窗口

五个平台按 doubao → deepseek → kimi → qwen → yuanbao 的顺序逐个走完，不并发——
同时开好几个登录窗口，用户分不清该登哪个。`--keep-open` 可让窗口留着不关。

平台身份（会话名、入口地址）在 config.py，浏览器封装在 playwright-cli.py，
本文件只管「怎么判断某个平台登没登录」。

登录流程参考 sunny 插件里五个 picker 技能（doubao / deepseek / kimi / qwen / yuanbao）
的「打开 → 判断登录 → 让用户登录 → 复核」四步，只取登录那几步，提问与取值不管。

三个沿用自那些技能的红线：不代用户登录、不触碰 cookie 与 token、登录永远由用户本人完成。
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any

# 公共层放在同目录，其中 playwright-cli.py 文件名带连字符，普通 import 语句写不了，
# 只能靠 importlib 按名字加载——先把 scripts/ 放到 sys.path 最前面
sys.path.insert(0, str(Path(__file__).resolve().parent))
config = importlib.import_module("config")
pwc = importlib.import_module("playwright-cli")

Platform = config.Platform
PLATFORMS = config.PLATFORMS
PLATFORM_KEYS = config.PLATFORM_KEYS

LOG_PREFIX = "[login]"
log = config.make_logger(LOG_PREFIX)

# 每个平台的登录态探针：返回 logged_in / logged_out / unknown 三种字符串。
# unknown 表示「页面还没渲染出可判断的东西」——它是暂态，不是结论，轮询要等它过去。
#
# 为什么不像技能里那样用 snapshot 判断：snapshot 给的是给模型看的文本快照，
# 解析它要迁就排版；这些平台的关键元素都有稳定的类名或属性，eval 读一次更直接。

DOUBAO_STATE_JS = """(() => {
  if (!document.querySelector("[contenteditable=true]")) return "unknown";
  const loginBtn = [...document.querySelectorAll("button")]
    .filter(b => (b.textContent || "").trim() === "登录").length;
  return loginBtn > 0 ? "logged_out" : "logged_in";
})()"""

# deepseek 未登录时整页就是登录表单（没有输入框），登录后才是聊天页
DEEPSEEK_STATE_JS = """(() => {
  if (location.pathname.startsWith("/sign_in")) return "logged_out";
  if (document.querySelector("[class*=ds-sign-in-form]")) return "logged_out";
  if (!document.querySelector("textarea, [contenteditable=true]")) return "unknown";
  const loginBtn = [...document.querySelectorAll("button, div")]
    .filter(b => (b.textContent || "").trim() === "登录").length;
  return loginBtn > 0 ? "logged_out" : "logged_in";
})()"""

KIMI_STATE_JS = """(() => {
  const login = document.querySelectorAll(".login-button").length;
  const user = document.querySelectorAll("[data-testid=sidebar-user-menu-trigger]").length;
  if (login > 0) return "logged_out";
  if (user > 0) return "logged_in";
  return "unknown";
})()"""

# 千问未登录也能提问（输入框照样在），所以只认「登录」按钮
QWEN_STATE_JS = """(() => {
  if (!document.querySelector("textarea, [contenteditable=true]")) return "unknown";
  const loginBtn = [...document.querySelectorAll("button")]
    .filter(b => (b.textContent || "").trim() === "登录").length;
  return loginBtn > 0 ? "logged_out" : "logged_in";
})()"""

# 元宝未登录时右上会弹登录浮层，侧栏那一格写着「未登录」。
#
# 已知边界（2026-10 实测）：元宝会给匿名访客分一个默认昵称（形如「用户80e4」），
# 浮层一消失，侧栏显示的就是它——跟真登录的用户名长得一模一样，光看页面文本
# 分不开。参考技能里「显示用户名即已登录」那条判据在当前版本已经失效。
# 所以判据只往「未登录」方向认，认不出就算已登录：漏报（把匿名当已登录）比
# 误报（把已登录当未登录、白白把人赶去登录一遍）温和，何况元宝匿名也能用。
# 「登录」按钮必须先看：它比侧栏文字更早渲染，能挡住加载中间态。
YUANBAO_STATE_JS = """(() => {
  const loginBtn = [...document.querySelectorAll("button")]
    .filter(b => (b.textContent || "").trim() === "登录").length;
  if (loginBtn > 0) return "logged_out";
  const el = document.querySelector("[class*=yb-nav__user]");
  const navText = el ? (el.textContent || "").trim() : "";
  if (navText.includes("未登录")) return "logged_out";
  if (navText) return "logged_in";
  return "unknown";
})()"""

# 平台 key → 登录态探针。key 取自 config.PLATFORMS，两边对不上会在这里露馅
STATE_JS: dict[str, str] = {
    "doubao": DOUBAO_STATE_JS,
    "deepseek": DEEPSEEK_STATE_JS,
    "kimi": KIMI_STATE_JS,
    "qwen": QWEN_STATE_JS,
    "yuanbao": YUANBAO_STATE_JS,
}


def probe_state(session: str, state_js: str) -> str:
    """读一次登录态，归一成 logged_in / logged_out / unknown。"""
    value = pwc.eval_js(session, state_js)
    return value if isinstance(value, str) else "unknown"


def read_confirmed_state(session: str, state_js: str) -> str:
    """读一次登录态并隔一拍复核，两次一致才采信。

    复核不是多余的：Kimi 首屏会先吐一份未登录形态的 HTML，前端接管后才换成登录态，
    只读一次会把已登录误判成未登录，白白把用户拉去登录一遍。其它平台同理——
    页面切换的瞬间读到的可能是上一屏。
    """
    first = probe_state(session, state_js)
    if first == "unknown":
        return "unknown"
    # 复核间隔别调小：页面切换的那一两秒里，前后两屏可能给出同一个「确定」答案，
    # 而这个答案属于即将被替换掉的那一屏（deepseek 就栽在这儿）
    time.sleep(2.0)
    return first if probe_state(session, state_js) == first else "unknown"


def wait_url_stable(session: str, timeout: int, interval: int = 2) -> str:
    """等 URL 不再变化，返回稳定下来的那个 URL。

    SPA 在 goto 之后常再跳一次——deepseek 未登录时会从 / 跳到 /sign_in，
    跳转前那一屏会给出错误的登录答案（把未登录判成已登录）。必须等它安定。
    """
    deadline = time.monotonic() + timeout
    last = str(pwc.eval_js(session, "location.href"))
    while True:
        time.sleep(interval)
        current = str(pwc.eval_js(session, "location.href"))
        if current == last:
            return current
        last = current
        if time.monotonic() >= deadline:
            return current


def wait_state(
    session: str,
    state_js: str,
    timeout: int,
    interval: int,
    targets: tuple[str, ...],
) -> str | None:
    """轮询等待状态落进 targets；到点还没等到返回 None。"""
    deadline = time.monotonic() + timeout
    while True:
        state = read_confirmed_state(session, state_js)
        if state in targets:
            return state
        if time.monotonic() >= deadline:
            return None
        time.sleep(interval)


def check_platform(platform: Platform, args: argparse.Namespace) -> dict[str, Any]:
    """校验一个平台的登录态；需要登录时等到用户登完。

    返回一条结论记录，不在这里决定退出码——中途失败不打断后面的平台，
    用户跑一次就能看全五个平台的状态。
    """
    session = platform.session
    state_js = STATE_JS[platform.key]

    if session not in pwc.list_sessions():
        log(f"[{platform.key}] 打开浏览器（会话 {session}）")
        pwc.run_pw(session, "open", "--persistent", "--headed")
    else:
        log(f"[{platform.key}] 复用已经开着的会话 {session}")

    # 打开就先最小化，别让窗口跳出来挡视线；判定未登录时会再把它恢复出来
    pwc.minimize(session)
    log(f"[{platform.key}] 窗口已最小化")

    log(f"[{platform.key}] 导航到 {platform.url}")
    pwc.run_pw(session, "goto", platform.url)
    settled_url = wait_url_stable(session, args.page_timeout)
    log(f"[{platform.key}] 页面停在 {settled_url}")

    state = wait_state(
        session, state_js, args.page_timeout, args.interval, ("logged_in", "logged_out")
    )
    if state is None:
        log(f"[{platform.key}] 页面状态读不出来（一直不确定），跳过这个平台")
        return {"platform": platform.key, "logged_in": False, "action": "unreadable"}

    if state == "logged_out":
        # 把窗口恢复出来交给用户——最小化状态下他看不到登录页，没法登
        pwc.restore(session)
        log(
            f"[{platform.key}] 未登录：窗口已恢复出来，请在窗口里完成登录，"
            f"脚本会等你登完，最长等 {args.login_timeout} 秒"
        )
        state = wait_state(session, state_js, args.login_timeout, args.interval, ("logged_in",))
        if state is None:
            log(f"[{platform.key}] 等待登录超时（{args.login_timeout} 秒）")
            return {"platform": platform.key, "logged_in": False, "action": "timeout"}

        log(f"[{platform.key}] 登录完成")
        return {"platform": platform.key, "logged_in": True, "action": "logged_in_now"}

    log(f"[{platform.key}] 本来就是登录状态")
    return {"platform": platform.key, "logged_in": True, "action": "already"}


def announce(result: dict[str, Any]) -> None:
    """一个平台的结论，确认一个就报一个，不攒到最后。"""
    if result["logged_in"]:
        print(f"[{result['platform']}] 已登录完成", flush=True)
    elif result["action"] == "timeout":
        print(f"[{result['platform']}] 未登录完成（等待超时）", flush=True)
    else:
        print(f"[{result['platform']}] 未登录完成（页面状态读不出来）", flush=True)


def emit_json(results: list[dict[str, Any]]) -> None:
    print(json.dumps(results, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验各 AI 平台网页版的登录态，未登录就等着用户登完",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--platform",
        action="append",
        required=True,
        choices=(*PLATFORM_KEYS, "all"),
        help=(
            f"要校验的平台，必填；可重复出现，或用 all 表示全部"
            f"（{' / '.join(PLATFORM_KEYS)} / all）"
        ),
    )
    parser.add_argument(
        "--login-timeout", type=int, default=300, help="等待用户登录的上限秒数（默认 300）"
    )
    parser.add_argument(
        "--page-timeout", type=int, default=60, help="等待页面出状态的上限秒数（默认 60）"
    )
    parser.add_argument("--interval", type=int, default=3, help="轮询间隔秒数（默认 3）")
    parser.add_argument("--keep-open", action="store_true", help="校验完不关闭浏览器窗口")
    parser.add_argument("--json", action="store_true", help="结果以 JSON 输出")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # all 是「全选」的简写；跟具体平台名混着给时也按全选处理
    wanted = set(PLATFORM_KEYS) if "all" in args.platform else set(args.platform)
    selected = [p for p in PLATFORMS if p.key in wanted]

    # 严格顺序验证：一个平台完整走完（登完 + 关窗）再走下一个，不并发。
    # 串行不只是为了好读日志——同时开好几个登录窗口，用户分不清该登哪个。
    results: list[dict[str, Any]] = []
    for i, platform in enumerate(selected, 1):
        log(f"--- {i}/{len(selected)} 校验 {platform.key} ---")
        result = check_platform(platform, args)
        results.append(result)

        # 结论立刻打出来，不等全部平台跑完
        if not args.json:
            announce(result)

        # 确认登录了就当场收工关窗，不留一堆窗口在后面。
        # 没登上的不关：用户可能正对着那个窗口登录，关掉等于把他手上的活掐了。
        if result["logged_in"] and not args.keep_open:
            pwc.run_pw(platform.session, "close", check=False)
            log(f"[{platform.key}] 已关闭浏览器窗口")

    if args.json:
        emit_json(results)

    failed = [r["platform"] for r in results if not r["logged_in"]]
    if failed:
        log(f"未完成登录的平台：{', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
