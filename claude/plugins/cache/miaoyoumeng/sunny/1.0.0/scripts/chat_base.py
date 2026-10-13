#!/usr/bin/env python3
"""
chat_base.py — 批量提问脚本的公共模板（模板方法模式）

被 `scripts/chat-<平台>.py` 继承，不单独执行。

分工：

    playwright-cli.py   怎么驱动浏览器（最底层，谁都能用）
    config.py           平台身份 + 日志（配置）
    chat_base.py        批量提问的流程模板（本文件）
    chat-<平台>.py      平台差异（选择器、探测 JS、提交方式、完成判据、删会话）

## 模板方法

`ChatScript.main()` 把流程钉死，顺序不再由各脚本自己拼：

    三步验证（① 参数 → ② 输出位置 → ③ 登录）→ 开浏览器（最小化）→ 导航 → 等页面就绪
    → 槽位 1 prepare_page  → 槽位 2 read_baseline → 槽位 3 after_baseline
    → 逐个提交/等收尾/取值/落盘 → 输出结果 → 删本次会话 → 关浏览器

三个槽位对应各平台现有的插入点，位置**与原代码逐一核对过**（挪动会改行为，别随手调）：

    槽位 1 prepare_page    页面就绪之后、读会话基线之前
                           doubao/deepseek 放 dismiss_dialogs；qwen 放 ensure_space + ensure_mode；
                           yuanbao 放 ensure_mode；kimi 不用
    槽位 2 read_baseline   记下「提交前就已经存在」的会话，收尾时只删之外那条
    槽位 3 after_baseline  读基线之后。deepseek 的 select_deep_think 原本就在这个位置

## 结果写去哪

`--dir` 与 `--file` 二选一（argparse 互斥组强制，缺一个或都给都报错退出）：

    --dir=out/           一个 prompt 一个文件：out/1.md、out/2.md …
    --file=out/汇总.md   本次所有回答写进这一个文件：第 1 个 prompt **覆盖写**
                         （重跑时把上一次的整份结果换掉），之后逐个**追加**
                         （追加时前面补一个空行，各回答在 Markdown 里才分得开）

两种模式都等第一个回答取回来才动文件：登录没过、页面没就绪这类早退不会留下空文件。
详见 resolve_output() 与 write_result()。

## 子类要写什么

**必须声明**：PLATFORM / LOG_PREFIX / DESCRIPTION / URL_LABEL / LOGIN_FAILED_TEMPLATE /
INPUT_SELECTOR / ROUND_SELECTOR / BODY_SELECTOR / CONVERSATION_URL_RE。

DESCRIPTION / URL_LABEL / LOGIN_FAILED_TEMPLATE 这三条文案各平台自己写整句——
中文名与英文名在中文句子里的空格排版不一样（「豆包未登录」对「Kimi 未登录」），
插值拼不出来，索性各自写全。

**必须实现**：`page_state_js()` `probe_js(index)` `submit_js(text)`
`delete_conversation_js(id)` `convert_html(html)`。

**按需覆盖**（基类已有默认实现）：`prepare_page` `after_baseline` `read_baseline`
`is_round_done` `status_detail` `heartbeat_detail` `dismiss_dialogs` `read_box_js`
`looks_logged_out` `submit_failure_message` `cleanup_skip_reason` `delete_conversation_js`
`fetch_round_js` `add_platform_args`。

## page_state_js 的返回契约

基类的 `wait_page_ready` 要读这三个键，子类的 JS 必须给出来：

    {"input_ready": bool,   # 输入框渲染出来了没
     "rounds": int,         # 页面上已有几轮回答
     ...}                   # 其余键随便加，登录判据由 looks_logged_out 自己认
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# 公共层放在同目录，其中 playwright-cli.py 文件名带连字符，普通 import 语句写不了，
# 只能靠 importlib 按名字加载——先把 scripts/ 放到 sys.path 最前面
sys.path.insert(0, str(Path(__file__).resolve().parent))
config = importlib.import_module("config")
pwc = importlib.import_module("playwright-cli")

# playwright-cli 的调用统一走公共层，下面留别名，调用处少写点前缀
run_pw = pwc.run_pw
eval_js = pwc.eval_js
run_code = pwc.run_code

# 登录校验脚本（同目录）。各脚本不自己判登录，交给它，见 run_login_check()
VALIDATOR_PATH = Path(__file__).resolve().parent / "platform-logined-validator.py"

# 追加在每条 prompt 末尾，锁死回答格式：网页端默认就输出 Markdown，
# 显式要求是为了免得被压成纯文本
MARKDOWN_HINT = "。请用 Markdown 格式回答。"

# 输入框出现后再等这一拍才动手：页面随后还有一轮重渲染，立刻操作的话
# 刚拿到的焦点会被冲掉（豆包脚本实测踩过，表现为提交静默失败）
PAGE_SETTLE_SECONDS = 1.5


@dataclass(frozen=True)
class OutputTarget:
    """本次运行的结果写去哪。--dir 与 --file 二选一，恰好有一个不是 None。

    两种模式互斥是 argparse 保证的（互斥组 required=True），所以拿到这个对象时
    不用再判「都没给」，只看哪个不是 None 就知道走哪条路。
    """

    dir: Path | None = None  # --dir：每个 prompt 一个 <dir>/<序号>.md
    file: Path | None = None  # --file：本次全部回答写进这一个文件


class ChatScript:
    """一个平台的批量提问脚本。子类声明差异、实现钩子，流程由 main() 固定。"""

    # ------------------------------------------------------------ 子类必须声明

    PLATFORM: config.Platform  # 平台身份（会话名、入口地址），来自 config.py
    LOG_PREFIX: str  # 日志前缀，形如 [doubao]
    DESCRIPTION: str  # argparse 的描述整句（中英混排的空格各平台自己排）
    URL_LABEL: str  # -u 的 help 开头，如「豆包地址」
    # 登录校验没过时的终止文案；可用 {prefix}（日志前缀）与 {code}（退出码）两个占位
    LOGIN_FAILED_TEMPLATE: str
    INPUT_SELECTOR: str  # 输入框
    ROUND_SELECTOR: str  # 轮次容器
    BODY_SELECTOR: str  # 正文容器
    CONVERSATION_URL_RE: re.Pattern[str]  # 从 URL 里抠会话 ID 的正则

    # 提交这个动作在文案里怎么称呼。元宝是点「发送」按钮、不认回车，覆写成「点发送后」。
    SUBMIT_ACTION_LABEL = "回车后"

    def __init__(self) -> None:
        self.log: Callable[[str], None] = config.make_logger(self.LOG_PREFIX)
        self.args = argparse.Namespace()

    # ---------------------------------------------------------------- 页面探测

    def page_state_js(self) -> str:
        """一次取回页面状态。**必须包含 `input_ready` 与 `rounds` 两个键**（见模块 docstring）。

        登录判据另外加键（登录按钮数、是否在登录页……），由 looks_logged_out() 认。
        """
        raise NotImplementedError

    def probe_js(self, index: int) -> str:
        """读第 index 轮（0 起）的收尾状态，返回一个状态字符串（`done` 表示已收尾）。

        为什么盯住第 index 个容器而不是「最后一条」：多轮连续提交时，回车后新容器
        还没出现，页面上的最后一条仍是上一轮的已完成状态，看最后一条会把「还没开始」
        误判成「已收尾」。钉死下标才准。
        """
        raise NotImplementedError

    def fetch_round_js(self, index: int) -> str:
        """取第 index 轮的全部正文容器 HTML（一轮可能挂多个，交给 Python 拼接）。"""
        return (
            "(() => {"
            f"  const msgs = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)});"
            f"  if (msgs.length <= {index}) return [];"
            f"  return [...msgs[{index}].querySelectorAll({json.dumps(self.BODY_SELECTOR)})]"
            "    .map(e => e.outerHTML);"
            "})()"
        )

    def read_box_js(self) -> str:
        """读回输入框现有文本。返回 `{text: ...}` 形状——fill 不回显填入的内容，
        要校验只能读回来；`text` 为空串（或 null）即视为输入框已清空。

        平台特有的「怎么判空」放这里（Slate 的 placeholder 是真实文本节点、
        Quill 靠 ql-blank 类），归一成这个契约，submit_prompt 才不用分平台。
        """
        return (
            "(() => {"
            f"  const ce = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            "  return JSON.stringify({text: ce ? ce.innerText : null});"
            "})()"
        )

    def read_box_text(self, session: str) -> str:
        """读回输入框里剩余的文本（已按各平台的判空规则归一，空串 = 已清空）。"""
        raw = eval_js(session, self.read_box_js())
        if isinstance(raw, dict):
            return str(raw.get("text") or "")
        return str(raw or "")

    # ------------------------------------------------------------------ 三步验证

    def run_login_check(self) -> None:
        """③ 登录校验：交给 platform-logined-validator.py，没过就终止流程。

        validator 自己会开浏览器、判断登录、必要时把窗口交给用户登（等到登完或
        超时），本脚本只要它最后给的是不是「已登录」。

        两处调用细节：

        - `--keep-open`：让它别关窗口——紧跟着本脚本要接着用同一个会话跑提问，
          关掉再开既多一次窗口闪烁，也可能撞上 profile 锁还没释放的空档。
        - stdout 转投 stderr：validator 的结论行走 stdout，而本脚本的 stdout 要留给
          最终结果；不转投的话，重定向 stdout 时会混进这一行。stderr 保持继承，
          登录等待的实时进度照常打给用户看。

        注意：validator 只认 config.py 里的默认会话，本脚本用 -s 换过会话时，
        校验的仍是默认那个会话（main 里会提醒一句）。
        """
        if not VALIDATOR_PATH.exists():
            sys.exit(f"{self.LOG_PREFIX} 找不到登录校验脚本：{VALIDATOR_PATH}")

        platform = self.PLATFORM.key
        self.log(f"③ 验证登录状态：platform-logined-validator.py --platform={platform}")
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), f"--platform={platform}", "--keep-open"],
            stdout=sys.stderr,
        )
        if proc.returncode != 0:
            sys.exit(
                self.LOGIN_FAILED_TEMPLATE.format(
                    prefix=self.LOG_PREFIX, code=proc.returncode
                )
            )
        self.log("登录校验通过")

    def resolve_output(self, raw_dir: str | None, raw_file: str | None) -> OutputTarget:
        """② 验证输出位置：--dir 与 --file 二选一，给哪个就校验哪个。

        argparse 的互斥组已经保证恰好给了一个，这里只管它指向的位置能不能用。
        """
        if raw_file is not None:
            return OutputTarget(file=self.resolve_out_file(raw_file))
        assert raw_dir is not None  # 互斥组 required=True 保证
        return OutputTarget(dir=self.resolve_out_dir(raw_dir))

    def resolve_out_dir(self, raw: str) -> Path:
        """② 验证文件夹（--dir）：必须是个已经存在的目录。

        不自动建目录：路径写错了却静默生成一整棵目录树，比直接报错难查得多。
        """
        out_dir = Path(raw).expanduser()
        if not out_dir.exists():
            sys.exit(
                f"{self.LOG_PREFIX} ② 文件夹验证未通过，目录不存在：{out_dir}\n"
                f"  请先建好目录（mkdir -p {raw}）再重跑本脚本。"
            )
        if not out_dir.is_dir():
            sys.exit(
                f"{self.LOG_PREFIX} ② 文件夹验证未通过，这不是个目录：{out_dir}\n"
                "  --dir 要给目录，不是文件；换一个（或删掉它建同名目录）。"
            )
        return out_dir

    def resolve_out_file(self, raw: str) -> Path:
        """② 验证输出文件（--file）：父目录得是现成的目录，文件本身不必存在。

        文件不存在不用管——写第一个结果时自动创建（所以早退不会留下空文件）。
        父目录也要求先建好，理由同 resolve_out_dir。

        注意：文件已经存在的话，第一个 prompt 的结果会把它**整个覆盖**掉，
        这是 --file 的既定语义（重跑同一批 prompt 时旧结果本来就该换掉）。
        """
        out_file = Path(raw).expanduser()
        if out_file.is_dir():
            sys.exit(
                f"{self.LOG_PREFIX} ② 输出位置验证未通过，这是个目录：{out_file}\n"
                "  --file 要给文件，不是目录；换一个（或删掉它建同名文件）。"
            )
        if not out_file.parent.is_dir():
            sys.exit(
                f"{self.LOG_PREFIX} ② 输出位置验证未通过，文件的父目录不可用：{out_file.parent}\n"
                f"  父目录须是已存在的目录（mkdir -p {out_file.parent}），"
                "文件本身不存在会自动创建。"
            )
        return out_file

    # -------------------------------------------------------------------- 浏览器

    def open_browser(self, session: str) -> None:
        """步骤 1 · 打开浏览器。

        --headed 显示窗口：登录、验证码要肉眼确认（窗口开完就由 ensure_browser 收起）。
        --persistent 持久化 profile：默认是内存模式，不持久化关掉就丢登录态。
        """
        self.log(f"打开浏览器（会话 {session}，持久化 profile）")
        run_pw(session, "open", "--persistent", "--headed")

    def ensure_browser(self, session: str, no_open: bool, show: bool) -> None:
        """确保浏览器会话可用，并让窗口待在后台（默认最小化）。

        会话来源两种，两种都得收起窗口：

        - **复用登录校验留下的那个**——校验判定「本来就已登录」时它一直是最小化的；
          判定「未登录」时它把窗口恢复出来交给用户登，登完窗口就那么开着，这里补收一次。
        - **自己新开的**——开完立刻收起。

        最小化只是把窗口收起来，脚本该干的照干：导航、填字、提交、取值都在后台完成。
        排查时想看页面就加 --show，窗口留在前台。
        """
        if session in pwc.list_sessions():
            self.log(f"复用已存在的会话 {session}")
        elif no_open:
            sys.exit(
                f"{self.LOG_PREFIX} 指定了 --no-open，但会话 {session} 不存在，无法继续。\n"
                "  去掉 --no-open 让脚本自己打开浏览器，或先手动把会话跑起来。"
            )
        else:
            self.open_browser(session)

        if show:
            self.log("按 --show 保留窗口显示（排查用）")
            pwc.restore(session)
        else:
            pwc.minimize(session)
            self.log("窗口已最小化，提问在后台进行")

    def goto_chat(self, session: str, url: str) -> None:
        self.log(f"导航到 {url}")
        run_pw(session, "goto", url)

    def close_browser(self, session: str) -> None:
        """步骤 9 · 关闭浏览器。

        只有流程正常走完才走到这儿，中途终止的那几处都绕开了它——那些情况下窗口
        要留给用户人工核对（未登录时那个窗口更是 validator 交还给用户的登录窗口）。

        关窗失败不中断：结果文件已经写完，为关不上一个窗口而报错不值当。
        登录态不受影响：open 用了 --persistent，profile 在磁盘上，下次还在。
        """
        run_pw(session, "close", check=False)
        self.log("已关闭浏览器")

    # ------------------------------------------------------------------ 等页面就绪

    def read_page_state(self, session: str) -> dict[str, Any]:
        state = eval_js(session, self.page_state_js())
        if not isinstance(state, dict):
            sys.exit(f"{self.LOG_PREFIX} 读取页面状态失败，返回：{state!r}")
        return state

    def looks_logged_out(self, state: dict[str, Any]) -> bool:
        """这一份页面状态看起来「登录态丢了」吗？判据各平台不同，覆写这个方法。

        基类默认：页面上挂着登录按钮。各平台的细节差异（豆包看「登录」按钮、
        Kimi 还要看侧栏用户菜单在不在、DeepSeek 看是否停在登录页）都写在自己的覆写里。

        注意**判据里通常要带 `input_ready`**：页面刚加载时状态栏还没渲染完，
        这时候读到的东西不作数（deepseek 是例外——它未登录时输入框根本不渲染，
        所以反过来只看「是否停在登录页」）。
        """
        return int(state.get("login_button", 0) or 0) > 0

    def logout_recheck_seconds(self) -> float:
        """复核「登录态丢了」之前先等这一拍，免得撞上页面切换的瞬间（各平台实测值不同）。"""
        return 1.5

    def wait_page_ready(self, session: str, timeout: int, interval: int) -> int:
        """步骤 2 · 等页面就绪（输入框出现），返回页面上已有的回答轮数。

        登录不在这里判断：进来之前已经由 platform-logined-validator.py 确认过。
        这里只兜一道底——万一页面又显示未登录，说明登录态意外丢了（profile 被换、
        账号被登出之类），直接终止让用户重跑，不带着错状态往下走。
        """
        deadline = time.monotonic() + timeout
        last_state: dict[str, Any] = {}

        while True:
            last_state = self.read_page_state(session)

            if self.looks_logged_out(last_state):
                # 复核一次再下结论，免得撞上页面切换的瞬间
                time.sleep(self.logout_recheck_seconds())
                again = self.read_page_state(session)
                if self.looks_logged_out(again):
                    sys.exit(
                        f"{self.LOG_PREFIX} 页面显示未登录（登录校验之后登录态又丢了），"
                        "流程终止。\n"
                        "  请重跑本脚本，会重新走一遍登录校验。"
                    )
                continue

            # 输入框还没渲染出来 = 页面在加载中，这时候读什么状态都不作数。
            if last_state.get("input_ready"):
                rounds = int(last_state.get("rounds", 0))
                # 输入框冒出来不等于页面折腾完了：后面还跟着一轮重渲染，
                # 这时候动手，刚拿到的焦点会被冲掉。给一拍再往下走。
                time.sleep(PAGE_SETTLE_SECONDS)
                self.log(f"页面已就绪，页面上已有 {rounds} 轮历史回答")
                return rounds

            if time.monotonic() >= deadline:
                sys.exit(
                    f"{self.LOG_PREFIX} 等待页面就绪超时（{timeout} 秒）。\n"
                    f"  最后一次读到的页面状态：{last_state}\n"
                    "  请检查浏览器窗口里的页面是否正常加载。"
                )
            time.sleep(interval)

    # -------------------------------------------------------------------- 提交

    def submit_js(self, text: str) -> str:
        """聚焦 → 填入 → 提交，全部塞进同一次 run-code。

        为什么不能拆成 fill / click / press 几条独立命令（实测踩过）：每条命令是独立
        进程，命令之间的空档正好够页面完成一次重渲染，刚拿到的焦点会被冲掉，提交
        落空。症状是「命令条条成功、页面纹丝不动」，prompt 还留在输入框里没发出去。
        塞进同一个 Playwright 上下文连续执行，焦点才保得住。
        """
        raise NotImplementedError

    def submit_failure_message(self, result: dict[str, Any]) -> str | None:
        """提交动作没成功时，按结果给一条「怎么排查」的文案；不认识的返回 None。

        收整个 result 而不是只收 stage，是因为有的平台要把整份结果打进报错里
        （元宝的「文本没填进输入框（{...}）」）。

        返回 None 的话，submit_prompt 会走「隔两秒复核输入框」那条通用路径
        （提交可能只是清空慢了一拍）。各平台的 stage 取值不同，覆写时照抄原有文案。
        """
        if result.get("stage") == "fill":
            return (
                f"{self.LOG_PREFIX} 文本没填进输入框（命令报成功但页面没反应，"
                "多半是输入框没就绪）。请检查页面后重试。"
            )
        return None

    def submit_prompt(self, session: str, prompt: str, markdown_hint: bool = True) -> None:
        """步骤 4 · 填入 prompt 并提交，提交后确认真的落地。

        提交落地这一步不能省：静默失败时页面看不出任何异常，只等不查会一路耗到超时，
        最后拿到空结果。判据是「输入框已清空」——提交前它装着 prompt。
        """
        text = prompt.rstrip() + MARKDOWN_HINT if markdown_hint else prompt
        if "\n" in text:
            self.log("注意：prompt 里含换行，填入输入框时可能被吞掉或提前触发发送")

        result = run_code(session, self.submit_js(text))
        if not isinstance(result, dict):
            sys.exit(f"{self.LOG_PREFIX} 提交动作返回的结果无法解析：{result!r}")
        if result.get("ok"):
            return
        message = self.submit_failure_message(result)
        if message:
            sys.exit(message)

        # 输入框还有内容：可能真没发出去，也可能发出去了、只是清空慢了一拍。
        # 隔两秒复核一次（只读，不会重复发送），确认没发出去才判失败——
        # 这里不自动重发，重复投递一条问题比报错麻烦得多。
        time.sleep(2.0)
        left = self.read_box_text(session)
        if not left.strip():
            self.log("复核：输入框已清空，提交其实成功了")
            return

        sys.exit(
            f"{self.LOG_PREFIX} {self.SUBMIT_ACTION_LABEL}输入框里还留着内容，"
            "这一轮没发出去。\n"
            f"  输入框残留：{left[:80]!r}\n"
            "  请到浏览器窗口人工确认后再重跑脚本。"
        )

    # ---------------------------------------------------------------- 等本轮收尾

    def probe_status(self, session: str, index: int, memory: dict[str, Any]) -> str:
        """探一次本轮状态，归一化成字符串；需要跨次记录的东西写进 memory。

        基类默认：probe_js() 的返回值本身就是状态字符串（多数平台如此）。
        DeepSeek 的探针返回的是个对象（状态 + 字数 + 停止按钮），它覆写这个方法，
        把字数存进 memory、只回状态——**别把字数编进状态字符串**，否则每轮长度一变
        就算「状态变了」，长回答会把日志刷满。
        """
        return str(eval_js(session, self.probe_js(index)))

    def is_round_done(self, status: str, memory: dict[str, Any], index: int) -> bool:
        """这一轮收尾了吗？默认：状态就是 `done`。

        要「连读 N 次才采信」的平台覆写这个方法（豆包要 suspect 连读 2 次、
        DeepSeek 要字数连续 2 次不变）。平台特有的收尾日志也在覆写里打——
        默认实现不打日志，免得给别的平台凭空多出一行。
        """
        return status == "done"

    def status_detail(self, memory: dict[str, Any]) -> str:
        """状态日志的尾巴（默认没有）。如 DeepSeek 的「（1234 字符）」。"""
        return ""

    def heartbeat_detail(self, memory: dict[str, Any]) -> str:
        """心跳日志的尾巴（默认没有）。如 DeepSeek 的「，当前 1234 字符」。"""
        return ""

    def wait_round(self, session: str, index: int, timeout: int, interval: int) -> bool:
        """步骤 5 · 等第 index 轮回答收尾。

        返回 True = 已收尾，可以取值；False = 到点仍未收尾，按「未生成完」处理。

        骨架固定为「探询 → 状态变了才打日志 → 判完成 → 判超时 → 心跳 → 等一拍」，
        各平台的判据差异在 probe_status / is_round_done 两个钩子里。
        """
        deadline = time.monotonic() + timeout
        heartbeat_at = time.monotonic() + 30
        last_status = ""
        memory: dict[str, Any] = {}

        while True:
            status = self.probe_status(session, index, memory)
            if status != last_status:
                self.log(f"第 {index + 1} 轮状态：{status}{self.status_detail(memory)}")
                last_status = status

            if self.is_round_done(status, memory, index):
                return True

            now = time.monotonic()
            if now >= deadline:
                self.log(f"第 {index + 1} 轮等待超时（{timeout} 秒），按「未生成完」处理")
                return False
            if now >= heartbeat_at:
                self.log(
                    f"仍在生成，已等 {int(timeout - (deadline - now))} 秒"
                    f"{self.heartbeat_detail(memory)}"
                )
                heartbeat_at = now + 30

            time.sleep(interval)

    def fetch_round_markdown(self, session: str, index: int) -> str:
        """步骤 6 · 取第 index 轮的 HTML 并还原成 Markdown。"""
        blocks = eval_js(session, self.fetch_round_js(index))
        if not isinstance(blocks, list):
            sys.exit(f"{self.LOG_PREFIX} 取回答 HTML 失败，返回：{str(blocks)[:200]}")
        return self.render_round([str(b) for b in blocks])

    def convert_html(self, html: str) -> str:
        """把一段正文 HTML 还原成 Markdown。**各平台自己实现**（见文件里的 HTML→Markdown 段）。"""
        raise NotImplementedError

    def render_round(self, blocks: list[str]) -> str:
        """一轮里的多个正文容器按顺序拼接；空容器直接丢掉，不影响下标。"""
        parts = [b for b in (self.convert_html(html) for html in blocks) if b]
        return "\n\n".join(parts)

    # ---------------------------------------------------------------- 会话清理

    def read_conversation_id(self, session: str) -> str | None:
        """从当前页面 URL 里抠出会话 ID；不在某个会话页上就返回 None。"""
        url = str(eval_js(session, "location.href"))
        match = self.CONVERSATION_URL_RE.search(url)
        return match.group(1) if match else None

    def read_baseline(self, session: str) -> Any:
        """槽位 2 · 记下「提交前就已经存在」的会话，收尾时只删之外那条。

        默认只记当前会话 ID。元宝多记一份侧栏名单（它打开页面就已经站在会话页上，
        光看 URL 认不出新旧），覆写时返回自己的基线对象，cleanup_skip_reason 里认得就行。
        """
        return self.read_conversation_id(session)

    def delete_conversation_js(self, conversation_id: str) -> str:
        """删掉左侧列表里指定会话，返回 `{ok, stage, ...}` 形状的结果。

        各平台的 DOM 操作差异最大（hover 显形、菜单开合、确认弹窗……），
        所以各写各的；每一步都要先验证入口存在再点，并把卡住的步骤名带回去。
        """
        raise NotImplementedError

    def cleanup_skip_reason(self, session: str, current_id: str | None, baseline: Any) -> str | None:
        """该不该出手删？返回原因文字就跳过（照原样打日志），返回 None 才动手。

        默认两道保险：URL 里读不到会话 ID、当前会话提交前就存在。元宝另加两道
        （它得先确认目标确实进了侧栏名单），覆写时保持判据顺序不变。
        """
        if current_id is None:
            return "页面不在某个会话里（URL 里读不到会话 ID），没有可删的记录，跳过"
        if current_id == baseline:
            return (
                f"会话 {current_id} 提交前就存在，不是本次新建的，不敢删——"
                "需要清理请到页面里手动删"
            )
        return None

    def cleanup_conversation(self, session: str, baseline: Any) -> None:
        """步骤 8 · 删除左侧会话列表里本次交互记录。

        只认「提交前还不存在」的那条会话：拿提交前的基线做对照，对不上就不动手。
        删除不可逆，宁可留一条记录，也不能删到用户的历史会话。

        删不掉不中断流程：结果文件已经写完，为一条记录报错不值当；警告里带上
        会话 ID，用户照着手动删。
        """
        current_id = self.read_conversation_id(session)
        reason = self.cleanup_skip_reason(session, current_id, baseline)
        if reason:
            self.log(reason)
            return
        assert current_id is not None  # cleanup_skip_reason 保证过

        result = run_code(session, self.delete_conversation_js(current_id))
        if isinstance(result, dict) and result.get("ok"):
            self.log(f"已删除左侧本次交互记录（会话 {current_id}）")
            return
        if isinstance(result, dict):
            self.log(f"删除没走通，卡在「{result.get('stage')}」这一步：{result}")
        else:
            self.log(f"删除动作返回的结果无法解析：{result!r}")
        self.log(f"会话仍留在左侧列表（{current_id}），请在页面里手动删除")

    # -------------------------------------------------------------- 平台特有槽位

    def prepare_page(self, session: str, baseline: int) -> int:
        """槽位 1 · 页面就绪之后的平台特有准备步（默认什么都不做）。

        返回（可能被重置的）轮数基线——比如千问切空间会整页重载，切完得重新等
        页面就绪、把基线换成新的，否则后面按旧基线算下标会取错轮次。
        """
        return baseline

    def after_baseline(self, session: str, baseline: Any) -> None:
        """槽位 3 · 读会话基线之后的平台特有步骤（默认什么都不做）。

        DeepSeek 的「深度思考」开关在这里开：它原本就排在读基线之后，位置别挪。
        """
        return

    def dismiss_dialogs(self, session: str) -> None:
        """关掉挡路的模态弹窗（默认没有这回事，静默通过）。"""
        return

    # -------------------------------------------------------------------- 输出

    def write_result(self, target: OutputTarget, seq: int, markdown: str) -> Path:
        """把一个 prompt 的回答落盘，返回写好的路径。

        --dir 模式：写进 <dir>/<seq>.md。文件名叫什么就是它的全部身份：
        序号即 prompt 的提交顺序，第 1 个 prompt 的回答是 1.md，第 11 个是 11.md，
        不补零。同名文件直接覆盖——重跑同一批 prompt 时，旧结果本来也该换掉。

        --file 模式：本次每个回答都写进同一个文件。第 1 个**覆盖写**（重跑时把
        上一次的整份结果换掉），之后逐个**追加**。追加时前面补一个空行：两次回答
        紧挨着的话，Markdown 会把它们当成同一段接着排。
        """
        text = markdown.rstrip() + "\n"
        if target.file is not None:
            if seq == 1:
                target.file.write_text(text, encoding="utf-8")
            else:
                with target.file.open("a", encoding="utf-8") as fh:
                    fh.write("\n" + text)
            return target.file

        assert target.dir is not None  # 互斥组保证二选一
        path = target.dir / f"{seq}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def emit(self, results: list[dict[str, Any]], as_json: bool) -> None:
        """结果输出到 stdout；进度日志已走 stderr，这里可直接重定向。"""
        if as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
            return

        chunks = []
        for r in results:
            flag = "" if r["complete"] else "（未生成完）"
            chunks.append(
                f"## 第 {r['index']} 轮{flag}\n\n**问**：{r['prompt']}\n\n**答**：\n\n{r['response']}"
            )
        if chunks:
            print("\n\n".join(chunks))

    # -------------------------------------------------------------------- 命令行

    def add_platform_args(self, parser: argparse.ArgumentParser) -> None:
        """挂上平台特有的参数（默认没有）。比如千问的 --fast、DeepSeek 的 --no-deep-think。"""
        return

    def parse_args(self) -> argparse.Namespace:
        session_default = self.PLATFORM.session
        url_default = self.PLATFORM.url
        parser = argparse.ArgumentParser(
            description=self.DESCRIPTION,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "-p",
            "--prompt",
            action="append",
            required=True,
            metavar="TEXT",
            help="要提交的 prompt，必填，可重复出现，按出现顺序依次提交",
        )
        # --dir 与 --file 二选一（required=True 的互斥组，一个不给、两个都给都报错）
        output = parser.add_mutually_exclusive_group(required=True)
        output.add_argument(
            "--dir",
            metavar="DIR",
            help="输出目录（与 --file 二选一），须已存在：每个 prompt 的回答按序号写进 1.md、2.md …",
        )
        output.add_argument(
            "--file",
            metavar="FILE",
            help="输出文件（与 --dir 二选一）：本次所有回答都写进这一个文件，"
            "第 1 个覆盖写、之后追加写；父目录须已存在，文件本身会自动创建",
        )
        parser.add_argument(
            "-s",
            "--session",
            default=session_default,
            help=f"playwright-cli 会话名（默认 {session_default}）",
        )
        parser.add_argument(
            "-u",
            "--url",
            default=url_default,
            help=f"{self.URL_LABEL}（默认 {url_default}）",
        )
        parser.add_argument("--timeout", type=int, default=300, help="单轮等待上限秒数（默认 300）")
        parser.add_argument("--interval", type=int, default=5, help="轮询间隔秒数（默认 5）")
        parser.add_argument(
            "--page-timeout", type=int, default=60, help="等待页面就绪的上限秒数（默认 60）"
        )
        parser.add_argument(
            "--json", action="store_true", help="结果以 JSON 输出（默认输出 Markdown）"
        )
        parser.add_argument(
            "--no-open", action="store_true", help="跳过打开浏览器（浏览器已经在跑时用）"
        )
        parser.add_argument(
            "--show",
            action="store_true",
            help="不最小化窗口，留在前台（默认最小化，排查时才用）",
        )
        parser.add_argument(
            "--no-markdown-hint", action="store_true", help="不追加「请用 Markdown 格式回答。」"
        )
        # 平台特有参数插在这个位置（不是末尾）：各脚本原本就把 --fast / --no-deep-think
        # 排在 --keep-conversation 前面，放末尾会让 --help 的条目顺序与旧版对不上。
        self.add_platform_args(parser)
        parser.add_argument(
            "--keep-conversation", action="store_true", help="跑完不删左侧本次对话记录（默认会删）"
        )
        return parser.parse_args()

    # ------------------------------------------------------------ 模板方法本体

    def main(self) -> None:
        """模板方法：固定流程，子类不覆写。"""
        # 三步验证，按固定顺序走完，才轮到开浏览器干正事：
        #   ① 验证参数 → ② 验证文件夹 → ③ 验证登录状态
        # 每步各打一行日志，走到哪一步一目了然。
        # 顺序不能换：前两步是本地判断，出结果只要一瞬间；登录校验要开浏览器、
        # 可能还要等用户登，最费时间，所以它排最后——前两步没过，用户不必白等这一趟。

        # ① 验证参数：argparse 管类型、取值与必填（--prompt 必填、--dir 与 --file
        #   二选一，缺一个或都给都在这儿报错退出）
        args = self.parse_args()
        self.args = args
        self.log("① 参数验证通过")

        session_default = self.PLATFORM.session
        if args.session != session_default:
            self.log(
                f"注意：-s 指定了会话 {args.session}，登录校验走的仍是默认会话 {session_default}"
            )

        # ② 验证输出位置：--dir 必须已经存在，--file 的父目录必须已经存在
        target = self.resolve_output(args.dir, args.file)
        if target.file is not None:
            self.log(f"② 输出文件验证通过：{target.file}")
        else:
            self.log(f"② 文件夹验证通过：{target.dir}")

        # ③ 验证登录状态：未登录由 validator 交给用户登，登不上直接终止，后面都不开始
        self.run_login_check()

        # 三步全过，才轮到真正干活的流程
        self.ensure_browser(args.session, args.no_open, args.show)

        self.goto_chat(args.session, args.url)
        baseline = self.wait_page_ready(args.session, args.page_timeout, args.interval)
        # 槽位 1：平台特有准备步（弹窗、空间/模式切换……）
        baseline = self.prepare_page(args.session, baseline)
        # 槽位 2：记下提交前的会话状态，收尾时只删「提交后才出现」的那条
        conv_baseline = self.read_baseline(args.session)
        # 槽位 3：读基线之后的平台特有步骤
        self.after_baseline(args.session, conv_baseline)

        self.log(f"本次提交 {len(args.prompt)} 个 prompt，从第 {baseline + 1} 轮开始计量")

        results: list[dict[str, Any]] = []
        for i, prompt in enumerate(args.prompt):
            index = baseline + i
            self.log(f"[{i + 1}/{len(args.prompt)}] 提交：{prompt}")
            self.submit_prompt(args.session, prompt, markdown_hint=not args.no_markdown_hint)

            complete = self.wait_round(args.session, index, args.timeout, args.interval)
            answer = self.fetch_round_markdown(args.session, index)
            results.append(
                {
                    "index": index + 1,
                    "prompt": prompt,
                    "response": answer,
                    "complete": complete,
                }
            )
            self.log(f"[{i + 1}/{len(args.prompt)}] 取回回答 {len(answer)} 字符")

            # 拿到一个就存一个：中途断了，前面已取回的回答也留在盘上
            path = self.write_result(target, i + 1, answer)
            action = "已写入" if target.file is None or i == 0 else "已追加到"
            self.log(f"[{i + 1}/{len(args.prompt)}] {action} {path}")

            if not complete:
                self.log("本轮到点仍未收尾，为避免页面状态错乱，后续 prompt 不再提交")
                break

        self.emit(results, as_json=args.json)

        if args.keep_conversation:
            self.log("按 --keep-conversation 保留左侧会话记录")
        else:
            self.cleanup_conversation(args.session, conv_baseline)
        self.close_browser(args.session)
