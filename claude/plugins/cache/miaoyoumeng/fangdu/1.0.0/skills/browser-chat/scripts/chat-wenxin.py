#!/usr/bin/env python3
"""
chat-wenxin.py — 用 playwright-cli 驱动文心一言网页版，批量提交 prompt 并取回 Markdown 回答

用法（在插件根目录执行，即 pyproject.toml 所在那一层）：

    # 提交两个 prompt，回答分别写进 out/1.md、out/2.md
    uv run python scripts/chat-wenxin.py \
        --prompt="问题一" --prompt="问题二" --dir=out

    # 也可以只给一个文件：本次所有回答全写进它，第 1 个覆盖写、之后追加写
    uv run python scripts/chat-wenxin.py \
        --prompt="问题一" --prompt="问题二" --file=out/汇总.md

    # 结果以 JSON 输出到 stdout，便于上层程序解析
    uv run python scripts/chat-wenxin.py --prompt="问题" --dir=out --json

输出：进度日志走 stderr，最终结果走 stdout——重定向时能拿到干净的结果。
落盘位置 --dir 与 --file 二选一：--dir 给目录，每个 prompt 的回答写进目录下以序号
命名的 Markdown 文件（1.md、2.md …）；--file 给文件，本次所有回答都写进这一个文件
（第 1 个覆盖写、之后逐个追加）。顺序就是 prompt 的提交顺序。

流程（按顺序）：

1. 三步验证，每步各打一行日志（①②③），全过才开浏览器：
   ① 验证参数（--prompt 必填；--dir 与 --file 二选一，缺一个或都给都报错退出）→
   ② 验证输出位置（--dir 须已存在；--file 的父目录须已存在）→ ③ 验证登录状态。
   登录校验交给 platform-logined-validator.py --platform=wenxin：未登录由它把
   窗口交给用户登，登不上（或超时）本脚本直接终止。
2. 打开（或复用）浏览器 → **窗口最小化** → 等页面就绪 → 把模型切到「自动」→
   逐个提交 prompt、等收尾、取回 Markdown。确认登录之后浏览器就不再占前台，
   全流程在后台跑；要看页面加 --show。
3. 每个回答写进 --dir/1.md、--dir/2.md …（或按 --file 追加进同一个文件），
   序号从 1 开始，就是 prompt 的提交顺序。
4. 关闭浏览器。想留/删左侧会话记录见下面「已知限制」。

**流程骨架在 `chat_base.py`**（模板方法模式）：三步验证、开浏览器、等页面就绪、
提交、等收尾、落盘、删会话、关浏览器都是那边写好的，本文件只写文心一言的差异——
选择器、页面探测、提交方式、收尾判据、「自动」模型切换，以及页面特有的
HTML → Markdown 转换。要改公共流程请去改 chat_base.py，改一处所有平台都生效。

与 deepseek 版的差异（页面本身不一样，流程骨架一模一样）：

1. **提交后跳到搜索结果页**——入口是 `https://wenxin.baidu.com/`，发出第一条提问后
   URL 变成 `/search/<对话ID>?enter_type=chat_url`，对话 ID 就是那串数字。侧栏
   会话项里挂在 `data-show-ext` 上的 `lid` 字段与它是同一个值。
2. **模式是两层的**——选择器按钮上显示的是**大类**（快速 / 工作任务），真正的模型
   藏在面板底部「模型」那一行的级联里（自动 / 文心 5.1）。两者会脱钩：实测把大类
   从「快速」切到「工作任务」再切回来，按钮文字一直是「快速」，而模型可能已经变了。
   所以判据读的是 `[data-model-name=smartMode]` 的 `aria-checked`，不是按钮文字。
   默认切到「自动」，`--no-auto-mode` 可关。
3. **回答区自带联网搜索**——「自动」模型会先搜一轮资料再作答，那一大段
   「搜索关键词 / 共参考 N 篇资料 / 引用列表」挂在回答容器里但与正文并列。正文容器
   `.cosd-markdown-content` 把它隔在外面，所以取正文是干净的，不会混进搜索结果。

实测记录（2026-10-14，页面结构以那天为准）：

- 输入框是 `textarea.ci-textarea`（带 placeholder）。页面上还有第二个无类名的
  textarea，**别用通用的 `textarea` 兜底去抓**，那个抓到的是它。
- **回车即发送**，页面上没有常驻的发送按钮（底部那排「图片生成 / 帮我写作 / PPT生成」
  是功能入口，不是发送）。输入框清空即提交成功。
- 一轮对话 = 一个 `div.answer-box`，**提问与回答都在这一个容器里**：提问在
  `[class*=answer-ask-container]`，回答在 `[class*=chat-search-answer-generate]`。
  多次提交时 `.answer-box` 逐个追加，下标与 prompt 顺序严格对齐。
- **回答正文是 `.cosd-markdown-content`**。必须限定到这一层：外层还套着
  `chat-search-answer-generate`（含思考过程与搜索资料）和 `cos-swiper`（分页控件），
  整块取会把这些一起写进正文。
- **收尾判据只能看长度**：正文长度连续 2 个轮询间隔不变才算收尾。**不能用正文容器
  上的 `cosd-markdown-content-typingall` 类**——实测（2026-10-14，两秒一采样跑了
  64 秒）它从第一个字出现起就一直在：4 秒 11 字符时有、64 秒 261 字符时还有，
  那是「内容由打字机效果渲染」的标记，不是收尾标记。拿它当判据会在第一个字落笔时
  就宣告完成，取回一段只有开头的残答（第一版就这么丢了一整段回答）。
- **正文里的 ZWNJ**：文心用 U+200C（零宽非连接符）包住 `<strong>` 之类的强调标签，
  原样转换会在 Markdown 里留下看不见的字符，所以 `_text()` 里把它清掉。
- 代码块是 `<pre>` 里包 `code-header`（语言名 + 复制按钮）、`code-left`（行号列）、
  `code-right > <code class="hljs language-python">`。**只从 `<code>` 里取文本**：
  行号与「复制」按钮都在它的兄弟节点里，整块取会把它们写进正文。语言名从
  `<code>` 的 `language-xxx` 类读。
- 表格同理：外面套着 `cosd-markdown-table`，它的标题栏（「表格」二字 + 复制 /
  下载按钮）与 `<table>` 是兄弟。要拦在容器这一层、只下探 `<table>`，否则正文里
  会凭空多出一行「表格」。

已知限制（2026-10-14 实测，未解决）：

- **侧栏的会话记录删不掉**。文心一言这一版的会话项没有可自动化触发的删除入口：
  各项都挂着 `no-hover` 类，hover（真实鼠标逐点移动、窗口前台/后台都试过）不出任何
  图标；上下文菜单 `history-more-panel`（含「置顶 / 收藏 / 重命名 / 删除」）在 DOM 里
  常驻但恒为 `visibility: hidden`，用改 DOM 的方式强制显形后点「删除」不生效——
  它的点击处理器依赖菜单由正常交互打开时记下的会话 ID，绕过去就成了空转。
  所以本脚本走完不再删会话，`--keep-conversation` 对它没有实际作用；跑完请到侧栏
  手动清理。这条限制一旦解除（页面上出现可点的删除入口），补上
  delete_conversation_js 即可，其余不用动。
- 联网搜索是模型自己的行为，`--no-markdown-hint` 之类开关影响不到它；只想关掉附带的
  搜索可以改用「文心 5.1」模型，但本脚本默认切的是「自动」。

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
# 正文由页面的 markdown 渲染器产出，骨架规整：段落 marklang-paragraph、代码块
# <pre><code class="hljs language-xxx">、标准 table/ul/ol/h1-h6。套着的界面元素有三处
# 必须拦下：代码块横幅里的语言标签与「复制」按钮、代码块左侧的行号列、以及包在
# 强调标签外面的 ZWNJ。
#
# 为什么不用第三方 Markdown 转换库：这些界面文字它一个都不认，会原样写进正文。

# 语言标签只认这种长相的短标识，免得把「复制」「下载」这类按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")
# 从 <code class="hljs language-python"> 里抠语言名
CODE_LANG_RE = re.compile(r"language-([\w+#.-]{1,20})")

# 零宽非连接符：文心用它包住 <strong> 之类的强调标签来标记高亮范围，
# 原样转换会在 Markdown 里留下看不见的字符（复制到别处才发现）。
ZWNJ = "‌"


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
    """文本节点取值：清掉零宽非连接符，不换行空格拉回普通空格。"""
    return str(node).replace("\xa0", " ").replace(ZWNJ, "")


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
        # 块级代码由下面的 pre 分支接走，走到这里只可能是行内代码
        return "`" + node.get_text() + "`"

    if tag == "pre":
        # 文心的代码块：pre 里并排着 code-header（语言标签 + 复制按钮）与
        # code-wrapper（左边行号列 code-left、右边代码本体 code-right > code）。
        #
        # **取文本只从 <code> 里取**：行号和「复制」按钮是它的兄弟节点，整块走
        # textContent 会把「1 2 3 … python 复制」一起写进正文。代码本体里的换行
        # 是真实 \n（页面用 marklang 渲染，不是 <br>），所以 get_text() 拿到的
        # 就是带换行的源码。
        code_el = node.find("code")
        if code_el is None:
            return "\n\n```\n" + _text(node.get_text()).rstrip("\n") + "\n```\n\n"
        classes = " ".join(code_el.get("class") or [])
        found = CODE_LANG_RE.search(classes)
        lang = found.group(1) if found and LANG_RE.fullmatch(found.group(1)) else ""
        return f"\n\n```{lang}\n{_text(code_el.get_text()).rstrip(chr(10))}\n```\n\n"

    # 表格容器：标题栏（「表格」二字 + 复制 / 下载按钮）与表格本体是兄弟，整块下探
    # 会把那两个字写进正文（实测正文里凭空多出一行「表格」）。只取 <table>。
    if _has_class(node, "cosd-markdown-table"):
        table = node.find("table")
        return walk(table) if table is not None else ""

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


class WenxinChat(chat_base.ChatScript):
    """文心一言网页版的批量提问脚本。流程见 chat_base.ChatScript.main()。

    本文件只负责文心一言的差异：选择器、探测 JS、提交方式、收尾判据、
    「自动」模型切换，以及上面那段 HTML → Markdown。
    """

    PLATFORM = config.WENXIN
    LOG_PREFIX = "[wenxin]"
    DESCRIPTION = (
        "用 playwright-cli 驱动文心一言网页版，批量提交 prompt 并取回 Markdown 回答"
    )
    URL_LABEL = "文心一言地址"
    LOGIN_FAILED_TEMPLATE = (
        "{prefix} 文心一言未登录（登录校验退出码 {code}），流程终止。\n"
        "  请在浏览器窗口里登好文心一言再重跑本脚本；登录由你本人完成，脚本不代登。"
    )

    # 一轮对话 = 一个 .answer-box（提问与回答同一个容器）。
    # 用精确类名而不是 [class*=answer-box]：后者会把修饰类 last-answer-box 也算进来。
    #
    # **但它只装得住回答的第一块**：文心会把一次回答拆成多块（先一句开场白，
    # 长任务型的产物另开一块），第二块起挂在 .answer-box 之外的兄弟容器里，
    # 两块共用一个 .chat-qa-container 祖先层级、且提问文本完全相同。
    # 所以计数按 .answer-box（它与提问严格 1:1），取正文时再按「同一提问」
    # 把后续兄弟块并进来——见 round_blocks_js()。
    ROUND_SELECTOR = ".answer-box"

    # 一块问答的容器。合并相邻块时按它划界（见 round_blocks_js）。
    QA_CONTAINER_SELECTOR = ".chat-qa-container"

    # 回答正文。限定到最内层这一级是必须的——外层套着 chat-search-answer-generate
    # （含思考过程与联网搜索资料）和 cos-swiper（分页控件），整块取会一起写进正文。
    BODY_SELECTOR = ".cosd-markdown-content"

    # 输入框。首选带类名的那个：页面上另有一个无类名的 textarea，通用兜底会抓错。
    INPUT_SELECTORS: ClassVar[list[str]] = [
        "textarea.ci-textarea",
        "textarea",
        "[contenteditable=true]",
    ]

    # 登录态判据：侧栏用户位。未登录时它写着「请登录」，已登录换成用户名。
    # 与 platform-logined-validator.py 的 wenxin 探针保持同一个信号。
    USER_INFO_SELECTOR = "[class*=chat-aside-user-info]"
    SIGN_IN_TEXT = "请登录"

    # 模式控件。data-testid 比类名稳（类名带 CSS Modules 哈希）。
    MODE_SELECTOR = "[data-testid=chat-mode-selector]"
    MODE_MODEL_ROW = "[data-testid=chat-mode-model-row]"
    MODEL_AUTO = "[data-model-name=smartMode]"  # 「自动」子模型，选中态看 aria-checked
    CASCADE_PANEL = "[class*=cascade-panel]"

    # 回答区长度连续几次探询不变才认作收尾。
    #
    # **这里是 4，不是别处用的 2。** 文心在长任务模式下会「先说一句、再埋头干活」：
    # 实测开场白落笔后要停顿 6 秒以上才吐第二块（问「输出一张对比表格」时，前 10 秒
    # 只有一句「大概需要 1-2min」，16 秒才把表格补进来）。10 秒的窗口恰好卡在这段
    # 空档里，会把开场白当成整个回答收走。20 秒（4 次 × 默认 5 秒间隔）留了三倍余量。
    #
    # 页面上没有能替代它的信号：「任务已完成」那句文字比内容定型还早 6 秒，
    # `_sk-loading-generating` 之类的加载标记则从头到尾恒定存在，都不作数。
    STABLE_ROUNDS = 4

    # 会话页 URL 形如 /search/852505014913549900?enter_type=chat_url
    CONVERSATION_URL_RE = re.compile(r"/search/(\d+)")

    # ---------------------------------------------------------- 平台特有槽位

    def after_baseline(self, session: str, baseline: Any) -> None:
        """槽位 3 · 把模型切到「自动」。

        它是会话级的设置，提第一个问题前设一次就够。位置与 deepseek 的
        select_deep_think、xunfei 的 select_auto_mode 一致（读会话基线之后），别挪。
        """
        if self.args.no_auto_mode:
            self.log("按 --no-auto-mode 保持页面上当前的模型")
        else:
            self.select_auto_mode(session)

    def add_platform_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--no-auto-mode",
            action="store_true",
            help="不切「自动」模型，保持页面上当前的模型（默认会切到自动）",
        )

    # -------------------------------------------------------------- 页面探测

    def page_state_js(self) -> str:
        """一次取回三件事：登录态丢没丢、输入框在不在、页面上已有几轮对话。

        登录判据与 platform-logined-validator.py 的 wenxin 探针一致：侧栏用户位
        写着「请登录」就是登录态丢了。文心不改 URL（未登录也停在根路径或会话页），
        所以看元素，不看 URL。
        """
        return (
            "(() => {"
            f"  const boxes = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)});"
            f"  const input = document.querySelector({json.dumps(self.INPUT_SELECTORS[0])});"
            f"  const info = document.querySelector({json.dumps(self.USER_INFO_SELECTOR)});"
            "  const name = info ? (info.textContent || '').trim() : '';"
            f"  const out = name.includes({json.dumps(self.SIGN_IN_TEXT)});"
            "  return JSON.stringify({sign_in: out, input_ready: !!input,"
            " rounds: boxes.length});"
            "})()"
        )

    def looks_logged_out(self, state: dict[str, Any]) -> bool:
        """侧栏用户位写着「请登录」就是登录态丢了。"""
        return bool(state.get("sign_in"))

    def read_box_js(self) -> str:
        """读回输入框现有文本（fill 不回显填入的内容，要校验只能读回来）。

        找元素的方式要和 submit_js 完全一致——同样按 INPUT_SELECTORS 的顺序、
        同样取最后一个可见的。两边不一致就会读错元素：提交填的是这一个、复核读的是
        那一个，于是「输入框已清空」这个判据全是假的。
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

    def round_blocks_js(self, index: int) -> str:
        """「取出第 index 轮的全部正文容器」那段 JS，探收尾与取正文两处共用。

        共用是为了两处认的是同一批容器：一处数长度、一处拿 HTML，一旦走样，
        收尾判据盯的是 A 块、取回来的是 B 块，结果就对不上。

        **为什么不能只取第 index 个 .answer-box 里的**：文心会把一次回答拆成多块，
        第二块起挂在这个 box **之外**的兄弟 `.chat-qa-container` 里。实测：问「输出
        一张对比表格」，先流式吐一句「大概需要 1-2min」的开场白（这就是 box 里的
        全部内容），真正的表格另起一块渲染在下方。只认 box 会取回那句开场白。

        并块靠 **.answer-box 的有无**认亲：一次提问只产生一个 box，它落在本轮第一块里，
        后续补上的块都不含 box。所以从本轮那块往后并，碰到下一个带 box 的块就停
        ——那已经是下一轮了。

        （别改用「提问文本逐字相同」来认亲：实测 .chat-qa-container 里查不到任何
        提问元素，`[class*=answer-ask-container]` 命中数为 0，认亲会永远认不出来。）
        """
        return (
            f"  const boxes = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)});"
            f"  if (boxes.length <= {index}) return [];"
            f"  const qas = [...document.querySelectorAll("
            f"{json.dumps(self.QA_CONTAINER_SELECTOR)})];"
            f"  const qa = boxes[{index}].closest({json.dumps(self.QA_CONTAINER_SELECTOR)});"
            f"  const scope = qa ? [qa] : [boxes[{index}]];"
            "  if (qa) {"
            "    const start = qas.indexOf(qa);"
            "    for (let i = start + 1; i < qas.length; i++) {"
            f"      if (qas[i].querySelector({json.dumps(self.ROUND_SELECTOR)})) break;"
            "      scope.push(qas[i]);"
            "    }"
            "  }"
            "  const blocks = [];"
            "  for (const s of scope)"
            f"    blocks.push(...s.querySelectorAll({json.dumps(self.BODY_SELECTOR)}));"
        )

    def probe_js(self, index: int) -> str:
        """读第 index 轮（0 起）的收尾状态：这一轮回答正文的总字符数。

        为什么盯住第 index 个容器而不是「最后一个」：多轮连续提交时，回车后新容器
        还没出现，页面上的最后一个仍是上一轮的已完成状态，看最后一个会把「还没开始」
        误判成「已收尾」。钉死下标才准。

        「自动」模型会先联网搜一轮资料再作答，那段时间正文容器可能还没挂上（下标
        越界，按 wait:no-message 处理），或者挂上了但一个字没写（长度为 0）——
        两种都由 is_round_done 那条「长度非零」的规则兜住。

        **不读正文容器的类名**：那上面的 typingall 是打字机效果的标记，从第一个字
        起就一直在，认它等于一见开头就收工。理由详见 is_round_done。同理也不看
        `_answer-finished_`：它挂在思考步骤容器上，不是每个回答都有（长任务模式实测
        不出现），拿它当判据会一路等到超时。
        """
        return (
            "(() => {"
            + self.round_blocks_js(index)
            + "  const text = blocks.map(e => (e.textContent || '').trim()).join('');"
            "  return JSON.stringify({state: blocks.length ? 'ok' : 'wait:no-message',"
            " length: text.length});"
            "})()"
        )

    def fetch_round_js(self, index: int) -> str:
        """取第 index 轮的全部正文 HTML。

        覆写基类：基类只取第 index 个 .answer-box 里的正文，那拿不到文心拆出去的
        后续块（见 round_blocks_js）。这里交给共用的取块逻辑，几块都取回来，
        由 render_round 按顺序拼接。
        """
        return (
            "(() => {"
            + self.round_blocks_js(index)
            + "  return blocks.map(e => e.outerHTML);"
            + "})()"
        )

    # -------------------------------------------------------------- 模型切换

    def auto_mode_js(self) -> str:
        """读模型 → 不是「自动」才切 → 复核，全部塞进同一次 run-code。

        判据读的是**子模型**而不是选择器按钮上的文字：按钮显示的是大类（快速 /
        工作任务），子模型（自动 / 文心 5.1）藏在面板底部「模型」那一行的级联里，
        两者会脱钩——实测把大类切走再切回来，按钮文字一直是「快速」，模型却可能变了。

        切法三步：打开面板 → 点「模型」行展开级联 → 点「自动」。级联是收起状态时
        子项元素虽在 DOM 里但 display:none，Playwright 点不动，所以展开那一步不能省。

        收尾一律把面板关掉：不关的话它会盖在输入框上，紧接着的提交动作点不着。
        """
        sel = json.dumps(self.MODE_SELECTOR)
        row = json.dumps(self.MODE_MODEL_ROW)
        auto = json.dumps(self.MODEL_AUTO)
        cascade = json.dumps(self.CASCADE_PANEL)
        return (
            "async page => {"
            f"  const trigger = page.locator({sel}).first();"
            "  if (!(await trigger.count()))"
            "    return JSON.stringify({ok: false, action: 'not-found'});"
            "  const open = async () => {"
            "    if ((await trigger.getAttribute('aria-expanded')) !== 'true') {"
            "      await trigger.click(); await page.waitForTimeout(1200);"
            "    }"
            "  };"
            "  const close = async () => {"
            "    if ((await trigger.getAttribute('aria-expanded')) === 'true') {"
            "      await trigger.click(); await page.waitForTimeout(700);"
            "    }"
            "  };"
            "  const readAuto = async () => {"
            f"    const el = page.locator({auto}).first();"
            "    if (!(await el.count())) return null;"
            "    return await el.getAttribute('aria-checked');"
            "  };"
            "  await open();"
            "  if ((await readAuto()) === 'true') {"
            "    await close();"
            "    return JSON.stringify({ok: true, action: 'already'});"
            "  }"
            f"  const modelRow = page.locator({row}).first();"
            "  if (!(await modelRow.count())) {"
            "    await close();"
            "    return JSON.stringify({ok: false, action: 'row-missing'});"
            "  }"
            f"  const cascadeEl = page.locator({cascade}).first();"
            "  if (!(await cascadeEl.count()) || !(await cascadeEl.isVisible())) {"
            "    await modelRow.click(); await page.waitForTimeout(1200);"
            "  }"
            f"  const autoEl = page.locator({auto}).first();"
            "  if (!(await autoEl.count()) || !(await autoEl.isVisible())) {"
            "    await close();"
            "    return JSON.stringify({ok: false, action: 'cascade-missing'});"
            "  }"
            "  await autoEl.click();"
            "  await page.waitForTimeout(1500);"
            "  const after = await readAuto();"
            "  await close();"
            "  return JSON.stringify({ok: after === 'true', action: 'clicked',"
            " checked: after});"
            "}"
        )

    def select_auto_mode(self, session: str) -> None:
        """把模型切到「自动」。

        找不到控件不算错：页面改版可能换掉这些 data-testid，为它中断整个流程不值当，
        照常提问就是，日志里说一声。点了没切过来同理——那说明判据或层级又变了，
        值得记一笔，但不该拦下提问。
        """
        result = run_code(session, self.auto_mode_js())
        if not isinstance(result, dict):
            sys.exit(f"{self.LOG_PREFIX} 模型检查结果无法解析：{result!r}")

        action = result.get("action")
        if action == "already":
            self.log("模型已经是「自动」")
        elif result.get("ok"):
            self.log("已把模型切到「自动」")
        elif action == "not-found":
            self.log("页面上没找到模型选择器，跳过这一步（不影响提问）")
        elif action == "row-missing":
            self.log("模型选择器里没有「模型」这一行，跳过这一步（不影响提问）")
        elif action == "cascade-missing":
            self.log("展开后没找到「自动」这一项，跳过这一步（不影响提问）")
        else:
            self.log(
                f"点了「自动」但没切过来（aria-checked={result.get('checked')!r}），"
                "继续往下走"
            )

    # ------------------------------------------------------------------ 提交

    def submit_js(self, text: str) -> str:
        """聚焦 → 填入 → 回车，全部塞进同一次 run-code。

        为什么不能拆成 fill / click / press 三条独立命令（实测踩过）：每条命令是独立
        进程，命令之间的空档正好够页面完成一次重渲染，刚拿到的焦点会被冲掉，Enter
        落空。症状是「命令条条成功、页面纹丝不动」，prompt 还留在输入框里没发出去。
        塞进同一个 Playwright 上下文连续执行，焦点才保得住。

        **回车即发送**：文心页面上没有常驻的发送按钮，所以这里按 Enter，不点按钮。

        输入框按选择器顺序试、每个选择器内从后往前找**可见的**那个：页面上另有一个
        无类名的 textarea，取「最后一个」会取错。
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
            "  const read = async () => isField ? await box.inputValue()"
            " : await box.innerText();"
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
        """文心多一种失败：输入框选择器一个都没命中（或者命中的都不可见）。"""
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

        **不能认正文容器上的 typingall 类**（实测 2026-10-14 踩过）：那个类从第一个字
        出现起就一直在——4 秒 11 字符时有，64 秒 261 字符时还有。它是「内容由打字机
        效果渲染」的标记，不是收尾标记；认它会在第一个字落笔时就宣告完成，取回一段
        只有开头的残答。

        要连续两次不变而不是一次，是为了跨过流式输出中途的短暂停顿（联网搜索、分段
        吐字）。长度为 0 不算「稳定」：「自动」模型先跑搜索，正文容器可能已经挂上、
        一个字还没写，连着读到几次 0 就取，会取回一个空回答。
        """
        if status == "wait:stable" and int(memory.get("stable", 0)) >= self.STABLE_ROUNDS:
            self.log(
                f"第 {index + 1} 轮已收尾（长度连续 {self.STABLE_ROUNDS} 次不变，"
                f"{memory.get('length', 0)} 字符）"
            )
            return True
        return False

    def status_detail(self, memory: dict[str, Any]) -> str:
        return f"（{memory.get('length', 0)} 字符）"

    def heartbeat_detail(self, memory: dict[str, Any]) -> str:
        return f"，当前 {memory.get('length', 0)} 字符"

    # -------------------------------------------------------------- 会话清理

    def delete_conversation_js(self, conversation_id: str) -> str:
        """删掉左侧列表里指定会话。

        **这一版文心没有可自动化触发的删除入口，本方法注定走不通**（见文件头
        「已知限制」）。保留它是因为流程骨架里有这一步，且一旦页面改出可点的入口，
        这里是唯一的落点；在那之前，每一步都先验证入口存在再往下走，认不出就如实
        返回卡在哪一步，由 cleanup_conversation 打日志提示用户手动删除——不硬闯。

        定位会话项用的是 data-show-ext 里的 lid 字段，它与 URL 里的会话 ID 是同一个值。
        不能靠标题文本匹配：同名会话、标题被截断都会认错，删错会话不可逆。
        """
        item_sel = json.dumps(f'[data-show-ext*=\'"{conversation_id}"\']')
        more_sel = json.dumps(".history-item-more")
        panel_sel = json.dumps(".history-more-panel")
        return (
            "async page => {"
            f"  const item = page.locator({item_sel}).first();"
            "  if (!(await item.count())) return JSON.stringify({ok: false, stage: 'locate'});"
            "  await item.hover();"
            "  await page.waitForTimeout(700);"
            f"  const more = page.locator({more_sel}).first();"
            "  if (!(await more.count()))"
            "    return JSON.stringify({ok: false, stage: 'more-missing'});"
            "  if (!(await more.isVisible()))"
            "    return JSON.stringify({ok: false, stage: 'more-hidden'});"
            "  await more.click();"
            "  await page.waitForTimeout(900);"
            f"  const panel = page.locator({panel_sel}).first();"
            "  if (!(await panel.count()) || !(await panel.isVisible()))"
            "    return JSON.stringify({ok: false, stage: 'menu'});"
            "  const del = panel.locator('[class*=menu-item]')"
            ".filter({ hasText: '删除' }).first();"
            "  if (!(await del.count())) return JSON.stringify({ok: false, stage: 'menu-item'});"
            "  await del.click();"
            "  await page.waitForTimeout(1000);"
            "  const ok = page.locator('button, [class*=btn]')"
            ".filter({ hasText: /^\\s*(确\\s*定|删\\s*除)\\s*$/ }).first();"
            "  if (await ok.count() && await ok.isVisible()) {"
            "    await ok.click(); await page.waitForTimeout(1500);"
            "  }"
            f"  const remains = await page.locator({item_sel}).count();"
            "  return JSON.stringify({ok: remains === 0, stage: 'verify', remains});"
            "}"
        )

    def cleanup_skip_reason(
        self, session: str, current_id: str | None, baseline: Any
    ) -> str | None:
        """该不该出手删？除了基类的两道保险，这里再加一道：本版页面没有删除入口。

        写死这一条不是偷懒——实测（2026-10-14）hover 不出图标、上下文菜单强制显形后
        点击无效，硬走一遍只会得到一句「卡在 more-hidden」的日志，反而让人以为页面
        出了故障。不如把话说清楚。
        """
        reason = super().cleanup_skip_reason(session, current_id, baseline)
        if reason:
            return reason
        return (
            f"本版文心一言侧栏没有可自动化的删除入口，会话 {current_id} 留在列表里——"
            "请到侧栏手动删除（详见本脚本文件头「已知限制」）"
        )

    # --------------------------------------------------------- HTML → Markdown

    def convert_html(self, html: str) -> str:
        """把一段正文 HTML 还原成 Markdown——转交本文件的 convert()（见上面那段）。"""
        return convert(html)


if __name__ == "__main__":
    WenxinChat().main()
