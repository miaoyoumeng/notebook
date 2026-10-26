#!/usr/bin/env python3
"""
chat-xunfei.py — 用 playwright-cli 驱动讯飞星火网页版，批量提交 prompt 并取回 Markdown 回答

用法（在插件根目录执行，即 pyproject.toml 所在那一层）：

    # 提交两个 prompt，回答分别写进 out/1.md、out/2.md
    uv run python scripts/chat-xunfei.py \
        --prompt="问题一" --prompt="问题二" --dir=out

    # 也可以只给一个文件：本次所有回答全写进它，第 1 个覆盖写、之后追加写
    uv run python scripts/chat-xunfei.py \
        --prompt="问题一" --prompt="问题二" --file=out/汇总.md

    # 结果以 JSON 输出到 stdout，便于上层程序解析
    uv run python scripts/chat-xunfei.py --prompt="问题" --dir=out --json

输出：进度日志走 stderr，最终结果走 stdout——重定向时能拿到干净的结果。
落盘位置 --dir 与 --file 二选一：--dir 给目录，每个 prompt 的回答写进目录下以序号
命名的 Markdown 文件（1.md、2.md …）；--file 给文件，本次所有回答都写进这一个文件
（第 1 个覆盖写、之后逐个追加）。顺序就是 prompt 的提交顺序。

流程（按顺序）：

1. 三步验证，每步各打一行日志（①②③），全过才开浏览器：
   ① 验证参数（--prompt 必填；--dir 与 --file 二选一，缺一个或都给都报错退出）→
   ② 验证输出位置（--dir 须已存在；--file 的父目录须已存在）→ ③ 验证登录状态。
   登录校验交给 platform-logined-validator.py --platform=xunfei：未登录由它把窗口交给
   用户登，登不上（或超时）本脚本直接终止。
2. 打开（或复用）浏览器 → **窗口最小化** → 等页面就绪 → 把模式切到「自动模式」→
   逐个提交 prompt、等收尾、取回 Markdown。确认登录之后浏览器就不再占前台，
   全流程在后台跑；要看页面加 --show。
3. 每个回答写进 --dir/1.md、--dir/2.md …（或按 --file 追加进同一个文件），
   序号从 1 开始，就是 prompt 的提交顺序。
4. 删掉侧栏「最近对话」里本次这一条，再关闭浏览器。只删脚本自己新建的
   （提交前就存在的会话不动，免得误删历史）；想留着记录加 --keep-conversation。

**流程骨架在 `chat_base.py`**（模板方法模式）：三步验证、开浏览器、等页面就绪、
提交、等收尾、落盘、删会话、关浏览器都是那边写好的，本文件只写星火的差异——
选择器、页面探测、提交方式、收尾判据、删会话的 DOM 操作、「自动模式」切换，
以及页面特有的 HTML → Markdown 转换。要改公共流程请去改 chat_base.py，
改一处所有平台都生效。

与 deepseek 版的差异（都是页面本身不一样，流程一模一样）：

1. **入口是「工作台」**——https://xinghuo.xfyun.cn/desk，不是独立的聊天站。
   未登录时**不改 URL**（停在 /desk），所以登录判据只能看元素，见 page_state_js。
2. **多一个模式开关**——deepseek 切「深度思考」，星火切「自动 / 推理 / 快速」三档，
   默认就是「自动模式」，不是才动（见 select_auto_mode）。
3. **删会话多一步**——星火**不允许删除当前正在看的那个会话**（点了会弹
   「对话进行中，请稍后再试」），所以得先切到别的会话再删。详见 delete_conversation_js。

实测记录（2026-10-13，页面结构以那天为准）：

- 输入框页面上有**两个 textarea**：可见的那个才是聊天框，另一个 `.ant-input` 是隐藏
  备用。所以定位规则是「按选择器顺序试、每个选择器内只取可见的」（见 read_box_js）。
  欢迎页的输入框类名是 AskWindow_empty_welcome_caret，提交后整页换成对话布局，
  类名会变——因此选择器只写 `textarea`，不写那个带 empty_welcome 的类名。
- **回车即发送**，页面上没有常驻的发送按钮，也没有「停止生成」按钮（生成全程实测
  无此按钮），所以收尾判据只看回答区的字符数（见 is_round_done）。
- 一轮对话 = 一个 `article.new-line-content_turn`，里面包着用户提问
  （new-line-content_userMessage）与回答（new-line-content_assistantMessage）。
- **回答正文是 new-line-content_result 里的 .markdown-body**。这一层必须限定住：
  回答区还有个折叠的「思考过程」（new-line-content_process，details 元素），
  它里面也有一个 .markdown-body，不限定就会把思考过程当成正文一起取回来
  （实测一轮里 .markdown-body 有两个）。
- 提交后 URL 变成 `/desk?chatId=<数字>`，会话**会落库**、出现在左侧「最近对话」里，
  每条的 DOM id 就是 `list-item-<chatId>`。
- 模式控件是 DeepthinkButton：触发器 `[class*=deep_think_switch]`，当前档位显示在
  里面的 `[class*=deep_think_label]`（「自动」）。点开弹层 `[class*=deepthink_choice_popover]`，
  选项是 `div[class*=choice_item]`（排除标题用的 `choice_item_title`），
  三档分别是「自动模式 / 推理模式 / 快速模式」，选中项多一个 active 类。

红线：不代用户登录、不触碰 cookie 与 token；写文件只写 --dir 目录下或 --file 指定的结果文件。
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any, ClassVar

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# 公共层放在同目录，其中 playwright-cli.py 文件名带连字符，普通 import 语句写不了，
# 只能靠 importlib 按名字加载——先把 scripts/ 放到 sys.path 最前面
sys.path.insert(0, str(Path(__file__).resolve().parent))
config = importlib.import_module("config")
chat_base = importlib.import_module("chat_base")

# playwright-cli 的调用统一走公共层，下面留别名，调用处少写点前缀
eval_js = chat_base.eval_js
run_code = chat_base.run_code


# ------------------------------------------------------- HTML → Markdown
# 正文由页面的 markdown 渲染器产出，标签语义规整：代码块是 <pre><code
# class="language-xxx">，没有 deepseek 那种横幅式代码块组件。
#
# 为什么不用第三方 Markdown 转换库：通用的库认不出页面塞在正文里的界面元素——
# KaTeX 的孪生节点（katex-mathml 与 katex-html 各渲染一份，直接下探会读到重复且
# 错乱的公式）、代码块上的「复制」按钮。这些都会混进正文，所以沿 DOM 反向推回
# Markdown 语法，公式与代码块两处显式截断。
#
# deepseek 那套 .md-code-block 分支也留着：星火现在不用它，但两边结构真重合时
# 这段代码不用改就能吃下——多一个分支的代价远小于改版时现调。

# 语言标签只认这种长相的短标识，免得把「复制」「下载」这类按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")
# 从 <code class="language-python"> 里抠语言名
CODE_LANG_RE = re.compile(r"language-([\w+#.-]{1,20})")


def _has_class(node: Tag, name: str) -> bool:
    return name in (node.get("class") or [])


def _tex_of(node: Tag) -> str:
    """取公式原文。KaTeX 把 LaTeX 存在 annotation 里，MathJax 存在 script 里。"""
    ann = node.find("annotation", attrs={"encoding": "application/x-tex"})
    if ann:
        return ann.get_text().strip()
    script = node.find("script", attrs={"type": re.compile(r"^math/tex")})
    if script:
        return script.get_text().strip()
    return node.get_text().strip()


def _text(node: object) -> str:
    """文本节点取值，顺手把不换行空格拉回普通空格，输出更干净。"""
    return str(node).replace("\xa0", " ")


def walk(node: object) -> str:
    if isinstance(node, NavigableString):
        # 注释、doctype 之类不是正文，丢掉
        return "" if isinstance(node, Comment) else _text(node)
    if not isinstance(node, Tag):
        return ""

    tag = node.name.lower()

    def kids() -> str:
        return "".join(walk(c) for c in node.children)

    # 公式必须在遍历子节点之前截断：KaTeX 渲染后会同时留下 katex-mathml
    # 与 katex-html 两份孪生内容，继续下探只会得到重复且错乱的文本。
    if _has_class(node, "katex-display"):
        return f"\n\n$$\n{_tex_of(node)}\n$$\n\n"
    if _has_class(node, "katex"):
        return f"${_tex_of(node)}$"
    if tag == "script" and (node.get("type") or "").startswith("math/tex"):
        return f"${node.get_text().strip()}$"

    # deepseek 风格的代码块容器（带横幅、语言标签、「复制」「下载」按钮）。星火不用，
    # 留着是为了结构撞车时不改代码。整块拦下来的理由：横幅里的界面文字不属于代码。
    if _has_class(node, "md-code-block"):
        pre = node.find("pre")
        code = (pre.get_text() if pre else node.get_text()).rstrip("\n")
        label = node.select_one(".md-code-block-banner span")
        raw = label.get_text().strip() if label else ""
        lang = raw if LANG_RE.fullmatch(raw) else ""
        return f"\n\n```{lang}\n{code}\n```\n\n"

    if tag in ("script", "style", "button", "svg", "noscript"):
        return ""

    if tag == "br":
        return "  \n"  # 行尾两个空格 = Markdown 硬换行

    if tag == "hr":
        return "\n\n---\n\n"

    if tag == "p":
        return "\n\n" + kids().strip() + "\n\n"

    if re.fullmatch(r"h[1-6]", tag):
        return "\n\n" + "#" * int(tag[1]) + " " + kids().strip() + "\n\n"

    if tag in ("strong", "b"):
        inner = kids()
        return f"**{inner}**" if inner.strip() else inner

    if tag in ("em", "i"):
        inner = kids()
        return f"*{inner}*" if inner.strip() else inner

    if tag in ("del", "s", "strike"):
        inner = kids()
        return f"~~{inner}~~" if inner.strip() else inner

    if tag == "code":
        # 块级代码由上层 pre 分支接走，走到这里只可能是行内代码
        return "`" + node.get_text() + "`"

    if tag == "pre":
        # 星火的代码块：<pre class="code-block-wrapper"> 里包着 <code>，语言名的正主是
        # code 上的 **data-lang 属性**（class 里那串 "hljs code-block-body python"
        # 是 highlight.js 留下的，语言名夹在中间，按 language-xxx 反过来抠不到——
        # 实测第一版就栽在这儿，围栏写成了空的）。所以先读 data-lang，再退回
        # class="language-x"，最后退回从 class 里找那个像语言名的词。
        #
        # 取文本只从 <code> 里取：pre 里还有个头部横幅，蹲着语言标签和「复制 / 下载 /
        # 运行」三个按钮（实测确认存在）。整块走 textContent 会把它们一起写进正文。
        code_el = node.find("code")
        if code_el is None:
            return "\n\n```\n" + node.get_text().rstrip("\n") + "\n```\n\n"
        raw = str(code_el.get("data-lang") or "").strip()
        if not raw:
            classes = " ".join(code_el.get("class") or [])
            found = CODE_LANG_RE.search(classes)
            raw = found.group(1) if found else ""
        lang = raw if LANG_RE.fullmatch(raw) else ""
        return f"\n\n```{lang}\n{code_el.get_text().rstrip('\n')}\n```\n\n"

    if tag == "a":
        href = node.get("href") or ""
        text = kids().strip()
        return f"[{text}]({href})" if href and text else text

    if tag == "img":
        return f"![{node.get('alt') or ''}]({node.get('src') or ''})"

    if tag == "blockquote":
        body = kids().strip()
        quoted = "\n".join("> " + line for line in body.split("\n"))
        return f"\n\n{quoted}\n\n"

    if tag in ("ul", "ol"):
        items = [c for c in node.children if isinstance(c, Tag) and c.name == "li"]
        ordered = tag == "ol"
        try:
            start = int(node.get("start") or 1)
        except ValueError:
            start = 1
        lines = []
        for i, li in enumerate(items):
            text = "".join(walk(c) for c in li.children).strip()
            marker = f"{start + i}. " if ordered else "- "
            # 嵌套列表换行后缩进三格，保证子项挂在父项之下
            lines.append(marker + text.replace("\n", "\n   "))
        return "\n\n" + "\n".join(lines) + "\n\n"

    if tag == "li":
        return kids()  # 脱离 ul/ol 的孤立 li，按普通文本处理

    if tag == "table":

        def cell(td: Tag) -> str:
            text = "".join(walk(c) for c in td.children).strip()
            # 单元格里的竖线要转义，否则撑破表格；换行压成空格
            return text.replace("|", r"\|").replace("\n", " ")

        rows = [
            [cell(td) for td in tr.children if isinstance(td, Tag)] for tr in node.find_all("tr")
        ]
        rows = [r for r in rows if r]
        if not rows:
            return ""
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        header, *body = rows
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(["---"] * width) + " |",
        ]
        lines += ["| " + " | ".join(r) + " |" for r in body]
        return "\n\n" + "\n".join(lines) + "\n\n"

    return kids()


def convert(html: str) -> str:
    # 收尾压掉多余空行。代码块内部的连续空行也会被一起压掉——Markdown 里
    # 块内空行不承载语义，这个代价换实现更简单，划算。
    return re.sub(r"\n{3,}", "\n\n", walk(BeautifulSoup(html, "html.parser"))).strip()


# ----------------------------------------------------------------- 脚本


class XunfeiChat(chat_base.ChatScript):
    """讯飞星火网页版（xinghuo.xfyun.cn/desk）的批量提问脚本。流程见 chat_base.ChatScript.main()。

    本文件只负责星火的差异：选择器、探测 JS、提交方式、收尾判据、删会话的 DOM 操作、
    「自动模式」切换，以及上面那段 HTML → Markdown。
    """

    PLATFORM = config.XUNFEI
    LOG_PREFIX = "[xunfei]"
    DESCRIPTION = (
        "用 playwright-cli 驱动讯飞星火网页版，批量提交 prompt 并取回 Markdown 回答"
    )
    URL_LABEL = "讯飞星火地址"
    LOGIN_FAILED_TEMPLATE = (
        "{prefix} 讯飞星火未登录（登录校验退出码 {code}），流程终止。\n"
        "  请在浏览器窗口里登好讯飞星火再重跑本脚本；登录由你本人完成，脚本不代登。"
    )

    # 一轮对话 = 一个 article（用户提问与回答都在里面）。
    ROUND_SELECTOR = "article[class*=new-line-content_turn]"

    # 回答正文。**限定在 new-line-content_result 里面**是必须的：回答区还有一个
    # 折叠的「思考过程」（new-line-content_process），它内部也挂着一个 .markdown-body，
    # 不限定就会把思考过程当正文取回来（实测一轮里 .markdown-body 有两个）。
    BODY_SELECTOR = "div[class*=new-line-content_result] div.markdown-body"

    # 输入框按顺序试，每个选择器内取最后一个**可见的**。
    # 页面上有两个 textarea：可见的那个才是聊天框，另一个 .ant-input 是隐藏备用
    # （实测）。所以「可见」这个条件不能省，否则会往隐藏框里填字，然后提交静默失败。
    INPUT_SELECTORS: ClassVar[list[str]] = [
        "textarea",
        "[contenteditable='true']",
    ]

    # 模式控件（DeepthinkButton）：触发器 / 当前档位 / 弹层 / 选项 / 选项标题。
    # 全是 CSS Modules 的类名，尾巴带哈希，所以一律用 [class*=前缀] 匹配。
    MODE_SWITCH_SELECTOR = "[class*=deep_think_switch]"
    MODE_LABEL_SELECTOR = "[class*=deep_think_label]"
    MODE_POPOVER_SELECTOR = "[class*=deepthink_choice_popover]"
    MODE_OPTION_SELECTOR = "div[class*=choice_item]"
    MODE_OPTION_TITLE_SELECTOR = "[class*=choice_item_title]"
    # 目标档位。触发器上显示简称「自动」，弹层里那一条写的是「自动模式」，
    # 取共同的部分「自动」，两边都能匹配上。
    MODE_TARGET = "自动"

    # 侧栏会话项、删除按钮、确认框。会话项的 id 就是 list-item-<chatId>，
    # 直接按 id 定位既稳又不用管列表顺序。
    ITEM_ID_PREFIX = "list-item-"
    ITEM_SELECTOR = "[class*=dialogList_list_item]"
    DELETE_BUTTON_SELECTOR = "[class*=dialogList_img_wrap]"

    # 回答区长度连续几次探询不变才认作收尾。2 表示要跨两个轮询间隔（默认 5 秒 → 10 秒），
    # 要两次而不是一次，是为了跨过流式输出中途那几秒停顿。
    #
    # 这里**不认「停止生成」按钮**：星火页面上根本没有这个按钮（2026-10 实测，
    # 生成全程都没有），所以只在长度上做判据。空回答不算数（见 is_round_done），
    # 所以「自动模式」先跑思考、正文一个字没写那几秒不会被误判成收尾。
    STABLE_ROUNDS = 2

    # 会话页 URL 形如 /desk?chatId=1168638379，收尾时按这个 ID 去侧栏认本次那条会话
    CONVERSATION_URL_RE = re.compile(r"chatId=(\d+)")

    # ---------------------------------------------------------- 平台特有槽位

    def after_baseline(self, session: str, baseline: Any) -> None:
        """槽位 3 · 把模式切到「自动模式」。

        它是会话级的设置，提第一个问题前设一次就够。位置与 deepseek 的
        select_deep_think、glm 的 select_max_thinking 一致（读会话基线之后），别挪。
        """
        if self.args.no_auto_mode:
            self.log("按 --no-auto-mode 保持页面上当前的模式")
        else:
            self.select_auto_mode(session)

    def add_platform_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--no-auto-mode",
            action="store_true",
            help="不切「自动模式」，保持页面上当前的模式（默认会切到自动）",
        )

    # -------------------------------------------------------------- 页面探测

    def page_state_js(self) -> str:
        """一次取回三件事：登录态丢没丢、输入框在不在、页面上已有几轮对话。

        登录判据与 platform-logined-validator.py 的 xunfei 探针保持一致：未登录时
        右上角有「登录 / 注册」按钮、侧栏用户位写着「未登录」。**星火不改 URL**
        （未登录也停在 /desk），所以这里看元素，不看 URL——这是它与 deepseek / glm 的
        不同之处，那两家的未登录会把整页跳走。

        判据只往「未登录」方向认：认不出就当登录着。理由同 validator——报未登录最多
        白跑一趟登录校验，漏报才会让流程带着一个用不了的页面往下走。
        """
        sels = json.dumps(", ".join(self.INPUT_SELECTORS))
        return (
            "(() => {"
            "  const vis = e => !!e && e.getClientRects().length > 0;"
            f"  const hits = [...document.querySelectorAll({sels})].filter(vis);"
            "  const loginBtn = document.querySelector('[class*=login_btn]');"
            "  const sideName = document.querySelector('[class*=LeftSide_user_name]');"
            "  const loggedOut = (vis(loginBtn) && (loginBtn.textContent || '').includes('登录'))"
            "    || (vis(sideName) && (sideName.textContent || '').includes('未登录'));"
            "  return JSON.stringify({sign_in: loggedOut, input_ready: hits.length > 0,"
            f" rounds: document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)}).length}});"
            "})()"
        )

    def looks_logged_out(self, state: dict[str, Any]) -> bool:
        """页面上挂着「登录 / 注册」按钮或侧栏写着「未登录」就是登录态丢了。"""
        return bool(state.get("sign_in"))

    def read_box_js(self) -> str:
        """读回输入框现有文本（fill 不回显填入的内容，要校验只能读回来）。

        找元素的方式要和 submit_js 完全一致——同样按 INPUT_SELECTORS 的顺序、同样
        取最后一个**可见的**。两边不一致就会读错元素：提交填的是这一个、复核读的是
        那一个，于是「输入框已清空」这个判据全是假的。

        「可见」这个条件对星火尤其要紧：页面上有两个 textarea，不可见的那个排在
        DOM 后面，随手取最后一个就取错了。
        """
        return (
            "(() => {"
            f"  const sels = {json.dumps(self.INPUT_SELECTORS)};"
            "  const visible = el => { const r = el.getBoundingClientRect();"
            " return r.width > 0 && r.height > 0; };"
            "  let el = null;"
            "  for (const s of sels) {"
            "    const hits = [...document.querySelectorAll(s)].filter(visible);"
            "    if (hits.length) { el = hits[hits.length - 1]; break; }"
            "  }"
            "  if (!el) return JSON.stringify({text: null});"
            "  const isField = el.tagName === 'TEXTAREA' || el.tagName === 'INPUT';"
            "  return JSON.stringify({text: isField ? el.value : el.innerText});"
            "})()"
        )

    def probe_js(self, index: int) -> str:
        """读第 index 轮（0 起）的收尾状态：这一轮回答正文的字符数。

        为什么盯住第 index 个轮次容器而不是「最后一个」：多轮连续提交时，回车后
        新容器还没出现，页面上的最后一条仍是上一轮的已完成状态，看最后一个会把
        「还没开始」误判成「已收尾」。钉死下标才准。

        正文还没挂上（.markdown-body 不存在）时长度按 0 算，由 is_round_done 那条
        「长度为 0 不算稳定」的规则兜住。
        """
        return (
            "(() => {"
            f"  const turns = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)});"
            f"  if (turns.length <= {index})"
            " return JSON.stringify({state: 'wait:no-message', length: 0});"
            f"  const body = turns[{index}].querySelector({json.dumps(self.BODY_SELECTOR)});"
            "  const text = body ? (body.textContent || '').trim() : '';"
            "  return JSON.stringify({state: 'ok', length: text.length});"
            "})()"
        )

    # ---------------------------------------------------------------- 模式切换

    def auto_mode_js(self) -> str:
        """读当前模式 → 不是自动才展开弹层 → 点「自动模式」→ 复核。

        四步塞进同一次 run-code：分成多条命令的话，命令之间的空档够页面重渲染，
        读完状态再点，读到的可能已经是过期的（理由同 submit_js）。

        当前档位读的是触发器里的简称（「自动」），比读弹层里那一条的 active 类稳——
        弹层没展开时也在 DOM 里，但它的类名和结构随版本变得更快。弹层是 toggle，
        所以先看一眼它是不是已经展开，展开了就直接点选项，别把弹层点关。
        """
        switch = json.dumps(self.MODE_SWITCH_SELECTOR)
        label = json.dumps(self.MODE_LABEL_SELECTOR)
        popover = json.dumps(self.MODE_POPOVER_SELECTOR)
        option = json.dumps(self.MODE_OPTION_SELECTOR)
        title = json.dumps(self.MODE_OPTION_TITLE_SELECTOR)
        target = json.dumps(self.MODE_TARGET)
        return (
            "async page => {"
            f"  const trigger = page.locator({switch}).first();"
            "  if (!(await trigger.count())) return JSON.stringify({ok: false, action: 'not-found'});"
            f"  const labelEl = page.locator({label}).first();"
            "  const cur = (await labelEl.count()) ? (await labelEl.innerText()).trim() : '';"
            f"  if (cur.includes({target}))"
            "    return JSON.stringify({ok: true, action: 'already', name: cur});"
            "  const shown = await page.evaluate(sel => {"
            "    const p = document.querySelector(sel);"
            "    return !!p && !p.className.includes('ant-popover-hidden');"
            f"  }}, {popover});"
            "  if (!shown) {"
            "    await trigger.click();"
            "    await page.waitForTimeout(900);"
            "  }"
            f"  const items = page.locator({popover} + ' ' + {option});"
            "  const n = await items.count();"
            "  let picked = false;"
            "  for (let i = 0; i < n; i++) {"
            "    const el = items.nth(i);"
            "    const cls = (await el.getAttribute('class')) || '';"
            "    if (cls.includes('choice_item_title')) continue;"
            f"    const titleEl = el.locator({title});"
            "    if (!(await titleEl.count())) continue;"
            "    const t = (await titleEl.first().innerText()).trim();"
            f"    if (t.includes({target})) {{ await el.click(); picked = true; break; }}"
            "  }"
            "  if (!picked) return JSON.stringify({ok: false, action: 'option-not-found'});"
            "  await page.waitForTimeout(1000);"
            f"  const after = (await labelEl.count()) ? (await labelEl.innerText()).trim() : '';"
            f"  return JSON.stringify({{ok: after.includes({target}),"
            " action: 'clicked', name: after});"
            "}"
        )

    def select_auto_mode(self, session: str) -> None:
        """把模式切到「自动模式」。

        读的是触发器上的简称（「自动」）而不是弹层里 li 的 active 类：触发器一直在，
        弹层没展开时读也准，不用为了确认当前档位先把弹层点开一次。

        找不到控件不算错：页面改版可能换类名或去掉这个开关，为它中断整个流程不值当，
        照常提问就是，日志里说一声。点了没切过来同理。
        """
        result = run_code(session, self.auto_mode_js())
        if not isinstance(result, dict):
            sys.exit(f"{self.LOG_PREFIX} 模式检查结果无法解析：{result!r}")

        action = result.get("action")
        if action == "already":
            self.log(f"模式已经是「{result.get('name')}模式」")
        elif result.get("ok"):
            self.log(f"已把模式切到「{result.get('name')}模式」")
        elif action == "not-found":
            self.log("页面上没找到模式控件，跳过这一步（不影响提问）")
        elif action == "option-not-found":
            self.log(f"弹层里没有「{self.MODE_TARGET}模式」这一档，跳过这一步（不影响提问）")
        else:
            self.log(f"模式点了但没切过来（当前 {result.get('name')!r}），继续往下走")

    # ------------------------------------------------------------------ 提交

    def submit_js(self, text: str) -> str:
        """聚焦 → 填入 → 回车，全部塞进同一次 run-code。

        为什么不能拆成 fill / click / press 三条独立命令（实测踩过）：每条命令是独立
        进程，命令之间的空档正好够页面完成一次重渲染，刚拿到的焦点会被冲掉，Enter
        落空。症状是「命令条条成功、页面纹丝不动」，prompt 还留在输入框里没发出去。
        塞进同一个 Playwright 上下文连续执行，焦点才保得住。

        **回车即发送**：星火页面上没有常驻的发送按钮，所以这里按 Enter，不点按钮。

        输入框按选择器顺序试、每个选择器内从后往前找**可见的**那个：页面上有两个
        textarea，不可见的那个排在 DOM 后面，取「最后一个」会取错（实测踩点）。
        """
        sels = json.dumps(self.INPUT_SELECTORS)
        return (
            "async page => {"
            f"  const sels = {sels};"
            "  let box = null;"
            "  for (const s of sels) {"
            "    const hits = page.locator(s);"
            "    const n = await hits.count();"
            "    for (let i = n - 1; i >= 0; i--) {"
            "      const cand = hits.nth(i);"
            "      if (await cand.isVisible()) { box = cand; break; }"
            "    }"
            "    if (box) break;"
            "  }"
            "  if (!box) return JSON.stringify({ok: false, stage: 'locate'});"
            "  const tag = await box.evaluate(el => el.tagName.toLowerCase());"
            "  const isField = tag === 'textarea' || tag === 'input';"
            "  const read = async () => isField ? await box.inputValue() : await box.innerText();"
            "  await box.click();"
            f"  await box.fill({json.dumps(text, ensure_ascii=False)});"
            "  const filled = await read();"
            "  if (!filled.trim()) return JSON.stringify({ok: false, stage: 'fill'});"
            "  await page.keyboard.press('Enter');"
            "  await page.waitForTimeout(1500);"
            "  const left = await read();"
            "  return JSON.stringify({ok: !left.trim(), stage: 'submit', left: left});"
            "}"
        )

    def submit_failure_message(self, result: dict[str, Any]) -> str | None:
        """星火多一种失败：输入框选择器一个都没命中（或者命中的都不可见）。"""
        if result.get("stage") == "locate":
            return (
                f"{self.LOG_PREFIX} 页面上找不到可用的输入框。\n"
                f"  找过的选择器：{', '.join(self.INPUT_SELECTORS)}\n"
                "  请检查浏览器窗口里的页面是否正常，必要时对着页面调选择器。"
            )
        return super().submit_failure_message(result)

    # ------------------------------------------------------------ 收尾判据

    def probe_status(self, session: str, index: int, memory: dict[str, Any]) -> str:
        """探一次本轮状态，并把字数与稳定计数存进 memory。

        探针返回的是个对象（状态 + 字数），这里把它归一成**有限的几个状态字符串**——
        字数只进 memory，不进状态串。把字数编进状态字符串的话，每轮长度一变就算
        「状态变了」，长回答会把日志刷满。
        """
        info = eval_js(session, self.probe_js(index))
        if not isinstance(info, dict):
            sys.exit(f"{self.LOG_PREFIX} 读取第 {index + 1} 轮状态失败，返回：{info!r}")

        state = str(info.get("state") or "")
        length = int(info.get("length") or 0)
        memory["length"] = length

        if state == "wait:no-message":
            # 新容器还没出现，页面上还是上一轮的残留
            memory["stable"] = 0
            memory["last_length"] = -1
            return "wait:no-message"
        if length > 0 and length == memory.get("last_length"):
            memory["stable"] = int(memory.get("stable", 0)) + 1
            return "wait:stable"
        memory["stable"] = 0
        memory["last_length"] = length
        return "wait:growing"

    def is_round_done(self, status: str, memory: dict[str, Any], index: int) -> bool:
        """回答区长度连续 STABLE_ROUNDS 次不变才算收尾。

        要求两次而不是一次，是因为流式输出中途常有几秒停顿（思考阶段、分段吐字）。
        长度为 0 不算「稳定」：「自动模式」先跑思考，正文容器可能已经挂上但一个字
        没写，连着读到几次 0 就认作收尾的话，会取回一个空回答。
        """
        if status == "wait:stable" and int(memory.get("stable", 0)) >= self.STABLE_ROUNDS:
            self.log(f"第 {index + 1} 轮已收尾（{memory.get('length', 0)} 字符）")
            return True
        return False

    def status_detail(self, memory: dict[str, Any]) -> str:
        return f"（{memory.get('length', 0)} 字符）"

    def heartbeat_detail(self, memory: dict[str, Any]) -> str:
        return f"，当前 {memory.get('length', 0)} 字符"

    # -------------------------------------------------------------- 会话清理

    def delete_conversation_js(self, conversation_id: str) -> str:
        """删掉左侧列表里指定会话：先切走 → hover → 点删除图标 → 确认框点「确 定」。

        **为什么第一步是「切走」**：星火不允许删除当前正在看的那个会话——它是当前
        会话时点删除，页面只弹一句「对话进行中，请稍后再试」，什么都不发生（实测，
        等 20 秒也不变）。而脚本跑完时页面上停的正好就是本次这条会话，所以不切走
        必定删不掉。

        切走的优先顺序也是实测定的：

        1. **切到侧栏里另一条已有会话**——零副作用，是首选。
        2. 侧栏里再没有别的会话时才点「新对话」——这会留下一条空的「新对话窗口」
           记录（实测它会落库、刷新后还在），属于有代价的兜底。之所以仍然接受它：
           走到这一步说明用户账号里一条历史都没有，多一条空记录不会挤掉任何东西；
           而留着本次那条带真实内容的会话，比留一条空记录更碍事。

        每一步都先验证入口存在再点，并把卡住的步骤名带回去。
        """
        target = json.dumps(f"#{self.ITEM_ID_PREFIX}{conversation_id}")
        item_sel = json.dumps(self.ITEM_SELECTOR)
        del_sel = json.dumps(self.DELETE_BUTTON_SELECTOR)
        return (
            "async page => {"
            f"  const target = page.locator({target});"
            "  if (!(await target.count())) return JSON.stringify({ok: false, stage: 'locate'});"
            # 1) 切到别的会话（当前会话删不掉）
            f"  const items = page.locator({item_sel});"
            "  const n = await items.count();"
            "  let moved = false;"
            "  const targetId = await target.first().getAttribute('id');"
            "  for (let i = 0; i < n; i++) {"
            "    const it = items.nth(i);"
            "    if ((await it.getAttribute('id')) === targetId) continue;"
            "    await it.click();"
            "    await page.waitForTimeout(1800);"
            "    moved = true;"
            "    break;"
            "  }"
            # 2) 没有别的会话可切，只能新建一个空的腾位置
            "  let created = false;"
            "  if (!moved) {"
            "    const nc = page.getByText('新对话', { exact: true }).first();"
            "    if (await nc.count()) {"
            "      await nc.click();"
            "      await page.waitForTimeout(1800);"
            "      created = true;"
            "    }"
            "  }"
            # 3) hover 出删除按钮 → 点它
            "  await target.first().hover();"
            "  await page.waitForTimeout(700);"
            f"  const delBtn = target.first().locator({del_sel}).first();"
            "  if (!(await delBtn.count())) return JSON.stringify({ok: false, stage: 'hover'});"
            "  await delBtn.click();"
            "  await page.waitForTimeout(1200);"
            # 4) 确认框
            "  const okBtn = page.locator('.ant-modal button').filter("
            "    { hasText: /确\\s*定/ }).first();"
            "  if (!(await okBtn.count()))"
            "    return JSON.stringify({ok: false, stage: 'confirm', moved: moved,"
            " created: created});"
            "  await okBtn.click();"
            "  await page.waitForTimeout(1800);"
            # 5) 复核：那条 id 还在不在
            f"  const remains = await page.locator({target}).count();"
            "  return JSON.stringify({ok: remains === 0, stage: 'verify', remains: remains,"
            " moved: moved, created: created});"
            "}"
        )

    # --------------------------------------------------------- HTML → Markdown

    def convert_html(self, html: str) -> str:
        """把一段正文 HTML 还原成 Markdown——转交本文件的 convert()（见上面那段）。"""
        return convert(html)


if __name__ == "__main__":
    XunfeiChat().main()
