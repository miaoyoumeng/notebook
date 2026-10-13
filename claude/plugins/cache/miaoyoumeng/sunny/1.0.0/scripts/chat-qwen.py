#!/usr/bin/env python3
"""
chat-qwen.py — 用 playwright-cli 驱动千问网页版，批量提交 prompt 并取回 Markdown 回答

用法（在插件根目录执行，即 pyproject.toml 所在那一层）：

    # 提交两个 prompt，回答分别写进 out/1.md、out/2.md
    uv run python scripts/chat-qwen.py \
        --prompt="问题一" --prompt="问题二" --dir=out

    # 也可以只给一个文件：本次所有回答全写进它，第 1 个覆盖写、之后追加写
    uv run python scripts/chat-qwen.py \
        --prompt="问题一" --prompt="问题二" --file=out/汇总.md

    # 结果以 JSON 输出到 stdout，便于上层程序解析
    uv run python scripts/chat-qwen.py --prompt="问题" --dir=out --json

输出：进度日志走 stderr，最终结果走 stdout——重定向时能拿到干净的结果。
落盘位置 --dir 与 --file 二选一：--dir 给目录，每个 prompt 的回答写进目录下以序号
命名的 Markdown 文件（1.md、2.md …）；--file 给文件，本次所有回答都写进这一个文件
（第 1 个覆盖写、之后逐个追加）。顺序就是 prompt 的提交顺序。

流程（按顺序）：

1. 三步验证，每步各打一行日志（①②③），全过才开浏览器：
   ① 验证参数（--prompt 必填；--dir 与 --file 二选一，缺一个或都给都报错退出）→
   ② 验证输出位置（--dir 须已存在；--file 的父目录须已存在）→ ③ 验证登录状态。
   登录校验交给 platform-logined-validator.py --platform=qwen：未登录由它把
   窗口交给用户登，登不上（或超时）本脚本直接终止。
2. 打开（或复用）浏览器 → **窗口最小化** → 等页面就绪 → **确认待在「日常」空间**
   → 确认模式 → 逐个提交 prompt、等收尾、取回 Markdown。确认登录之后浏览器就不再
   占前台，全流程在后台跑；要看页面加 --show。
3. 每个回答写进 --dir/1.md、--dir/2.md …（或按 --file 追加进同一个文件），
   序号从 1 开始，就是 prompt 的提交顺序。
4. 删掉左侧列表里「本次交互」那条会话记录，再关闭浏览器。只删脚本自己新建的
   （提交前就存在的会话不动，免得误删历史）；想留着记录加 --keep-conversation。

**流程骨架在 `chat_base.py`**（模板方法模式）：三步验证、开浏览器、等页面就绪、
提交、等收尾、落盘、删会话、关浏览器都是那边写好的，本文件只写千问的差异——
选择器、页面探测、提交方式、收尾判据、删会话的 DOM 操作、空间与模式的确认，
以及页面特有的 HTML → Markdown 转换。要改公共流程请去改 chat_base.py，
改一处五个平台都生效。

与 qwen-picker 技能（sunny 插件）流程的差异，五处：

1. **一次会话提交多个 prompt**——按「提交 → 等本轮收尾 → 取本轮回答」串行推进，
   每个 prompt 对应一条响应，下标严格对齐。串行是必须的：并行提交会让两轮回答
   在页面上交叉，谁也认不出哪条回答属于哪个问题。
2. **登录交给 platform-logined-validator.py**——本脚本不自己判断登录、也不等
   用户登录，只认那个脚本的结论；它说没登上，这里立刻终止，后面都不开始。
3. **结果落盘**——每个回答写进 --dir 下一个以序号命名的 .md 文件（或按 --file
   追加进同一个文件），拿文件走人即可，不必解析 stdout。
4. **空间与模式都显式确认**——千问分「日常」「工作」两个空间，本脚本只在「日常」
   里跑（工作空间的模式菜单是另一套，没有「思考研究」），每次现查、不在就切；
   技能要求提交前切到「思考研究」，本脚本默认照做（已经是就不动），想用「快速」
   加 --fast。模式按对话存，所以每次跑都现查，不靠记忆。
5. **收尾多一步删会话**——技能里没这一步，见 chat_base.py 的 cleanup_conversation()。

千问的四个平台特性（2026-10-12 实测），都直接决定选择器怎么写：

- **分「日常」「工作」两个空间，本脚本只认「日常」**：两个空间的页面是两套——
  工作空间下模式按钮显示的是「云端」之类的模型名，压根没有「思考研究」，正文容器
  与侧栏会话列表也不一样。千问会记住上次待过的空间，goto 根路径可能被它直接带进
  「工作」，所以每次跑都先查一遍：`[role=tablist][aria-label=对话模式]` 下的一对
  `button[role=tab]`，认 `aria-selected` 认当前在哪儿，不在「日常」就切过去；
  切空间是整页重载，切完得重新等页面就绪。
- **正文得靠 .answer-common-card 圈定，不能单看 .qk-markdown**：技能按
  .qk-markdown 取回答，那是「快速」模式下的样子。切到「思考研究」后思考过程也挂
  这个类，一轮问答会变成两个（第 1 个是思考、第 2 个才是正文），按下标取必然错位。
  正文住在 .answer-common-card 里、思考过程在 .thinking-content-* 里，用前者圈定，
  两种模式都准。
- **会话 ID 是 32 位十六进制**（无连字符），与豆包的纯数字、另两家的 UUID 都不同。
- **输入框是 Slate 富文本**：空着时 placeholder 是一段真实文本节点（带 BOM），
  所以判断输入框空没空不能只看 trim 后是否为空，得拿 placeholder 文本比对。

红线：不代用户登录、不触碰 cookie 与 token；写文件只写 --dir 目录下或 --file 指定的结果文件。
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

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
# 这一段内联自 qwen-picker 技能的 scripts/extract_markdown.py（2026-10-10 实测版本）。
#
# 为什么不用第三方 Markdown 转换库：千问页面有它特有的结构——代码块每行开头带
# 行号（react-syntax-highlighter 渲染）、代码横幅里有语言标签与「复制」「下载」
# 按钮、表格上方挂着工具栏。通用库不认这些，会把界面文字混进正文、把行号粘进
# 代码里。所以沿 DOM 反向推回 Markdown 语法。

# 语言标签只认这种长相的短标识，免得把「复制」「下载」这类按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")

# 代码块容器类名
CODE_BLOCK_CLASSES = ["qw-md-code"]
# 代码块里的语言标签。横幅里唯一带 mr-auto 的 span（复制等按钮在它右侧）
CODE_BANNER_SELECTOR = ".qw-md-code span.mr-auto"
# 表格工具栏的容器类名，里面放着「表格」标题和下载/导出按钮的文字
TABLE_TOOLBAR_CLASSES = ["qk-md-table-action"]


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


def _code_text(node: Tag) -> str:
    """取代码原文，顺手丢掉行号。

    不能直接用 get_text()：千问用 react-syntax-highlighter 渲染代码，每行开头
    塞一个行号 span（类名 linenumber），get_text() 会把它一起捞出来，
    取回的代码就变成「1def quick_sort(arr):」，粘进编辑器直接报错。
    """
    parts = []
    for child in node.children:
        if isinstance(child, NavigableString):
            parts.append("" if isinstance(child, Comment) else str(child))
        elif isinstance(child, Tag):
            if _has_class(child, "linenumber"):
                continue
            parts.append(_code_text(child))
    return "".join(parts)


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

    # 代码块容器。语言标签和「复制」「下载」按钮都蹲在横幅里，是整个容器中唯一
    # 不属于代码的文本；不整块拦下来，这些界面文字会混进正文（实测会凭空多出
    # 「python复制下载」一行）。顺手把语言从标签取回来，填进围栏。
    if any(_has_class(node, c) for c in CODE_BLOCK_CLASSES):
        pre = node.find("pre")
        code = (_code_text(pre) if pre is not None else _code_text(node)).rstrip("\n")
        label = node.select_one(CODE_BANNER_SELECTOR) if CODE_BANNER_SELECTOR else None
        raw = label.get_text().strip() if label is not None else ""
        lang = raw if LANG_RE.fullmatch(raw) else ""
        return f"\n\n```{lang}\n{code}\n```\n\n"

    # 表格上方的工具栏——「表格」标题加下载/导出按钮。整块丢掉，否则表格前面
    # 会凭空多出「表格下载为表格导出为图片」一行。（按钮文字藏在 div 里，
    # 下面那条按标签过滤的规则拦不住。）
    if any(_has_class(node, c) for c in TABLE_TOOLBAR_CLASSES):
        return ""

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
        # 块级代码由上层代码块容器 / pre 接走，走到这里只可能是行内代码
        return "`" + node.get_text() + "`"

    if tag == "pre":
        # 兜底：正常路径已被代码块容器分支接走，走到这里说明页面结构变了。
        # 语言信息拿不到，只保证代码本体不丢。
        return "\n\n```\n" + _code_text(node).rstrip("\n") + "\n```\n\n"

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
    text = walk(BeautifulSoup(html, "html.parser"))
    # 压掉多余空行。代码块内部的连续空行也会被一起压掉——Markdown 里
    # 块内空行不承载语义，这个代价换实现更简单，划算。
    return re.sub(r"\n{3,}", "\n\n", text).strip()


# ----------------------------------------------------------------- 脚本


class QwenChat(chat_base.ChatScript):
    """千问网页版的批量提问脚本。流程见 chat_base.ChatScript.main()。

    本文件只负责千问的差异：选择器、探测 JS、提交方式、收尾判据、删会话、
    「日常」空间与模式的确认，以及上面那段 HTML → Markdown。
    """

    PLATFORM = config.QWEN
    LOG_PREFIX = "[qwen]"
    DESCRIPTION = "用 playwright-cli 驱动千问网页版，批量提交 prompt 并取回 Markdown 回答"
    URL_LABEL = "千问地址"
    LOGIN_FAILED_TEMPLATE = (
        "{prefix} 千问未登录（登录校验退出码 {code}），流程终止。\n"
        "  请在浏览器窗口里登好千问再重跑本脚本；登录由你本人完成，脚本不代登。"
    )

    # 输入框：Slate 富文本。用选择器定位，不受 ref 失效影响（技能里用的是 snapshot + ref，
    # 那套要求每条命令前重新 snapshot，脚本里没法照搬）
    INPUT_SELECTOR = "[data-slate-editor]"

    # 轮次容器 / 正文容器 / 收尾标志（2026-10-12 实测）
    #
    # 一轮问答一个 .answer-common-card，下标即轮次——这是本脚本定位「第几轮」的唯一依据。
    # 别退回去数 .qk-markdown：思考研究模式下思考过程也带这个类，一轮会数出两个。
    ROUND_SELECTOR = ".answer-common-card"
    BODY_SELECTOR = ".qk-markdown"

    # 正文容器带上这个类 = 这一轮生成完了。实测生成中不带、完成时带上，两种模式一致。
    COMPLETE_CLASS = "qk-markdown-complete"

    # 千问分「日常」「工作」两个空间，页面、模式菜单、会话列表各是一套。本脚本只认
    # 「日常」：工作空间下模式按钮显示的是「云端」之类的模型名，压根没有「思考研究」
    # 这个选项，模式那一套选择器全对不上。千问会记住上次待过的空间，所以每次跑都得
    # 现查一遍——不然上次在工作空间待过，这次 goto 根路径会被它带回去。
    #
    # 切换控件是 [role=tablist][aria-label=对话模式] 里的一对 button[role=tab]，
    # 认 aria-selected（比看类名里的 bg-primary 稳当）。
    SPACE_TAB_SELECTOR = "button[role=tab]"
    SPACE_DAILY = "日常"
    SPACE_WORK = "工作"

    # 输入框下方的模式按钮，按钮文字就是当前模式名（「快速」/「思考研究」）。
    # 页面同时挂两份响应式副本，两份状态同步，取第一份即可。
    MODE_BUTTON_SELECTOR = "button[aria-haspopup=menu][aria-pressed]"
    MODE_DEEP = "思考研究"  # 深度搜索、深度研究——技能要求默认走这个
    MODE_FAST = "快速"  # 适用于大多数情况，跑得快

    # 会话页 URL 形如 /chat/<32 位十六进制>，收尾时按这个 ID 去左侧列表认本次那条会话。
    # 限死 32 位正好把 /chat（删除会话后落到的地址）这类固定页面挡在外面。
    CONVERSATION_URL_RE = re.compile(r"/chat/([0-9a-fA-F]{32})")

    # ---------------------------------------------------------- 平台特有槽位

    def prepare_page(self, session: str, baseline: int) -> int:
        """槽位 1 · 先确认待在「日常」空间，再把模式调成「思考研究」（或 --fast 的「快速」）。

        千问会记住上次待过的空间，goto 根路径可能被它带进「工作」。本脚本只在
        「日常」里跑：工作空间的模式菜单、取值选择器全是另一套。切过空间是整页
        重载，得重新等一次页面就绪，**轮数基线也跟着重读**——所以这里返回的是
        最后一次 wait_page_ready 的轮数，返回错了后面按旧基线算下标会取错轮次。
        """
        if self.ensure_space(session, self.SPACE_DAILY):
            baseline = self.wait_page_ready(
                session, self.args.page_timeout, self.args.interval
            )

        # 模式按对话存，所以每次跑都现查一次再提交（技能里的危险信号：想当然沿用上次）
        self.ensure_mode(session, self.MODE_FAST if self.args.fast else self.MODE_DEEP)
        return baseline

    def add_platform_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--fast",
            action="store_true",
            help=f"用「{self.MODE_FAST}」模式（默认切「{self.MODE_DEEP}」，不用这个开关）",
        )

    # -------------------------------------------------------------- 页面探测

    def read_box_js(self) -> str:
        """读出输入框里的真实内容，返回 `{text: ...}`（空串 = 输入框是空的）。

        Slate 空着时会把 placeholder 当普通文本节点塞进编辑器（还带一个 BOM），
        直接读 innerText 会读出「向千问提问」，看着像用户输入。所以拿 placeholder
        文本比对：读出来正好等于它，就算空。

        返回契约是 {text: ...}：判空规则不变，只是包了一层，好让 chat_base 的
        submit_prompt 用同一套取值代码（原来是裸字符串，那边得单独写一套）。
        """
        return (
            "(() => {"
            f"  const el = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            "  if (!el) return JSON.stringify({text: null});"
            "  const ph = (el.getAttribute('data-placeholder') || '').trim();"
            "  const t = (el.innerText || '').replace(/\\ufeff/g, '').trim();"
            "  return JSON.stringify({text: t === ph ? '' : t});"
            "})()"
        )

    def page_state_js(self) -> str:
        """一次取回四件事：有没有「登录」按钮、输入框在不在、页面上已有几轮回答、
        当前是哪个模式。

        登录判据只认「登录」按钮——千问未登录也能提问，输入框照样在，看输入框分不出
        登没登录（validator 用的也是这条判据，两边保持一致）。
        """
        return (
            "(() => {"
            "  const login = [...document.querySelectorAll('button')]"
            "    .filter(b => (b.textContent || '').trim() === '登录').length;"
            f"  const input = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            f"  const cards = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)}).length;"
            f"  const modes = [...document.querySelectorAll("
            f"{json.dumps(self.MODE_BUTTON_SELECTOR)})];"
            "  return JSON.stringify({login_buttons: login, input_ready: !!input,"
            "    rounds: cards, mode: modes.length ? (modes[0].textContent || '').trim() : null});"
            "})()"
        )

    def looks_logged_out(self, state: dict[str, Any]) -> bool:
        """页面上挂着「登录」按钮，就算登录态丢了。

        未登录也能提问，但那条对话不进侧栏，收尾时删不掉，等于留下一笔收拾不了的
        记录——所以宁可当场停下。带上 input_ready：页面正在加载时读到的东西不作数。
        """
        return bool(state.get("input_ready")) and int(state.get("login_buttons", 0) or 0) > 0

    def probe_js(self, index: int) -> str:
        """读第 index 轮（0 起）的收尾状态。

        为什么盯住第 index 个容器而不是「最后一条」：多轮连续提交时，回车后新容器
        还没出现，页面上的最后一条仍是上一轮的已完成状态，看最后一条会把「还没开始」
        误判成「已收尾」。钉死下标才准。

        判据只有一个：本轮正文带上 qk-markdown-complete。实测生成中不带、生成完才带
        （实测样本：提交后 2 秒读到 complete=0，再 2 秒读到 complete=1）。
        """
        return (
            "(() => {"
            f"  const cards = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)});"
            f"  if (cards.length <= {index}) return 'wait:no-message';"
            f"  const card = cards[{index}];"
            f"  if (!card.querySelector({json.dumps(self.BODY_SELECTOR)})) return 'wait:no-body';"
            f"  if (!card.querySelector({json.dumps('.' + self.COMPLETE_CLASS)}))"
            " return 'wait:streaming';"
            "  return 'done';"
            "})()"
        )

    def fetch_round_js(self, index: int) -> str:
        """取第 index 轮的全部正文容器 HTML（交给 Python 转 Markdown）。

        只在本轮卡片内部找 .qk-markdown，思考过程不在卡片里，天然被挡在外面。
        """
        return (
            "(() => {"
            f"  const cards = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)});"
            f"  if (cards.length <= {index}) return [];"
            f"  return [...cards[{index}].querySelectorAll({json.dumps(self.BODY_SELECTOR)})]"
            "    .map(e => e.outerHTML);"
            "})()"
        )

    # ---------------------------------------------------------------- 空间

    def space_state_js(self) -> str:
        """读「日常 / 工作」两个空间 tab 谁被选中；页面上没有这组控件就返回 null。

        认 aria-selected，不认类名：选中态那个类名（bg-primary font-600）是业务
        样式，改版最先动它；aria-selected 是语义属性，平台自己也得维护。
        """
        return (
            "(() => {"
            f"  const tabs = [...document.querySelectorAll({json.dumps(self.SPACE_TAB_SELECTOR)})];"
            "  const named = tabs.filter(t => {"
            "    const s = (t.textContent || '').trim();"
            f"    return s === {json.dumps(self.SPACE_DAILY, ensure_ascii=False)}"
            f"        || s === {json.dumps(self.SPACE_WORK, ensure_ascii=False)};"
            "  });"
            "  if (!named.length) return null;"
            "  const out = {};"
            "  for (const t of named) {"
            "    out[(t.textContent || '').trim()] = t.getAttribute('aria-selected') === 'true';"
            "  }"
            "  return JSON.stringify(out);"
            "})()"
        )

    def switch_space_js(self, want: str) -> str:
        """点目标空间那个 tab，再读回 aria-selected 复核。

        走 Playwright 的真实点击，不用页面里的 el.click()：这组 tab 是
        button[role=tab]，普通 click 就够，但真实点击少一层赌注——万一它们也像千问
        的菜单那样挂在 pointerdown 上，JS 点击会静默失效（模式菜单那边实测栽过）。

        定位用「先在页面里算出第几个、再按 nth 点」，不用 locator 的文字过滤：
        filter({hasText}) 这类匹配在不同平台上的表现不一（元宝的 li 上实测匹配不上），
        按下标点最实在。
        """
        return (
            "async page => {"
            "  const idx = await page.evaluate(() => {"
            f"    const want = {json.dumps(want, ensure_ascii=False)};"
            "    return [...document.querySelectorAll('button[role=tab]')]"
            "      .findIndex(t => (t.textContent || '').trim() === want);"
            "  });"
            "  if (idx < 0) return JSON.stringify({ok: false, stage: 'locate'});"
            f"  const tab = page.locator({json.dumps(self.SPACE_TAB_SELECTOR)}).nth(idx);"
            "  try {"
            "    await tab.click({timeout: 8000});"
            "  } catch (e) {"
            "    return JSON.stringify({ok: false, stage: 'click', err: String(e).slice(0, 120)});"
            "  }"
            "  await page.waitForTimeout(1500);"
            "  return JSON.stringify(await page.evaluate(() => {"
            # page.evaluate 的回调被序列化送进页面执行，外层变量在页面那边看不见
            f"    const want = {json.dumps(want, ensure_ascii=False)};"
            "    const tabs = [...document.querySelectorAll('button[role=tab]')];"
            "    const hit = tabs.find(t => (t.textContent || '').trim() === want);"
            "    return {ok: !!hit && hit.getAttribute('aria-selected') === 'true',"
            "      stage: 'verify'};"
            "  }));"
            "}"
        )

    def ensure_space(self, session: str, want: str) -> bool:
        """确保待在 want 空间（本脚本只传「日常」），返回是否真的切过。

        切过就得重等页面：切空间是整页重载，输入框、侧栏、模式菜单全换一套，
        调用方拿返回值决定要不要重新 wait_page_ready。

        不同于模式——空间不对就**终止**，不将就：工作空间下的模式按钮显示的是
        「云端」之类的模型名，没有「思考研究」这个选项，后面每一步的选择器都会
        落空。与其带着错状态跑完一批 prompt 交出错的回答，不如当场停下。

        读不到这组 tab 只警告、不终止：可能只是页面结构改了，而「读不到」不等于
        「在工作空间」，没必要为此掐掉整批任务。
        """
        state = eval_js(session, self.space_state_js())
        if not isinstance(state, dict):
            self.log("页面上读不到「日常 / 工作」切换控件，跳过空间检查（页面结构可能变了）")
            return False
        if state.get(want):
            self.log(f"已在「{want}」空间")
            return False

        current = next((k for k, on in state.items() if on), "未知")
        self.log(f"当前在「{current}」空间，切换到「{want}」")
        try:
            result = run_code(session, self.switch_space_js(want))
        except SystemExit as e:
            sys.exit(
                f"{self.LOG_PREFIX} 切换空间失败（{e}）。本脚本只在「{want}」空间里提问，"
                "流程终止。"
            )
        if isinstance(result, dict) and result.get("ok"):
            self.log(f"已切到「{want}」空间")
            return True
        sys.exit(
            f"{self.LOG_PREFIX} 切换空间没走通：{result}\n"
            f"  本脚本只在「{want}」空间里提问，流程终止，请检查页面后重试。"
        )

    # ---------------------------------------------------------------- 模式

    def switch_mode_js(self, want: str) -> str:
        """点开模式菜单 → 选目标项 → 读回按钮文字复核。

        菜单项是 [role=menuitemcheckbox]，文字比按钮上长（「思考研究深度搜索、深度研究」），
        所以用 includes 匹配，不要求全等。

        **开菜单那一下必须走 Playwright 的 click，不能用 JS 的 el.click()**——页面用的是
        Radix（千问的模式菜单、会话菜单都是它），Radix 的 Trigger 挂在 pointerdown 上，
        JS 的 click() 只派发 click 事件、不派发指针事件，菜单根本不开。2026-10-12
        端到端实测踩过：JS click 点完按钮，下一步找不到 menuitemcheckbox，报 stage='menu'。
        菜单项本身倒是认 el.click()（Radix 的 MenuItem 走 click），所以点开之后仍用 JS。
        """
        sel_js = json.dumps(self.MODE_BUTTON_SELECTOR)
        return (
            "async page => {"
            f"  const btn = page.locator({sel_js}).first();"
            "  try {"
            "    await btn.click({timeout: 8000});"
            "  } catch (e) {"
            "    return JSON.stringify({ok: false, stage: 'button', err: String(e).slice(0, 120)});"
            "  }"
            "  return JSON.stringify(await page.evaluate(async () => {"
            # page.evaluate 的回调是被序列化后送进页面执行的，外层 Playwright 上下文里的
            # 变量在页面那边看不见（实测报 ReferenceError: want is not defined），
            # 所以字面量得在回调里面再声明一次。
            f"    const want = {json.dumps(want, ensure_ascii=False)};"
            "    await new Promise(r => setTimeout(r, 900));"
            "    const item = [...document.querySelectorAll('[role=menuitemcheckbox]')]"
            "      .find(e => (e.textContent || '').includes(want));"
            "    if (!item) return {ok: false, stage: 'menu'};"
            "    item.click();"
            "    await new Promise(r => setTimeout(r, 1200));"
            f"    const btns = [...document.querySelectorAll({sel_js})];"
            "    const cur = btns.length ? (btns[0].textContent || '').trim() : '';"
            "    return {ok: cur === want, stage: 'verify', current: cur};"
            "  }));"
            "}"
        )

    def ensure_mode(self, session: str, want: str) -> None:
        """把模式调成 want（「思考研究」或「快速」）。

        模式按对话独立保存，所以每次跑都现查，不沿用上次的记忆（技能里的危险信号
        之一就是「上次选过这次不查」）。已经是目标模式就什么都不点。

        切不动只警告、不终止：模式影响的是回答深度，不影响这份结果能不能取回来；
        为它掐掉整批 prompt 不值当。
        """
        state = self.read_page_state(session)
        current = str(state.get("mode") or "")
        if not current:
            self.log("页面上读不到模式按钮，跳过模式检查（页面结构可能变了）")
            return
        if current == want:
            self.log(f"模式已是「{want}」，无需切换")
            return

        self.log(f"当前模式「{current}」，切换到「{want}」")
        try:
            result = run_code(session, self.switch_mode_js(want))
        except SystemExit as e:
            # run_pw 判定命令失败时会 sys.exit（见 playwright-cli.py 的 run_pw），
            # 这里接住：模式只是回答深度的偏好，不该把整批 prompt 拖垮。
            self.log(f"模式切换没走通（{e}）——按现状继续，回答深度可能不是你要的")
            return
        if isinstance(result, dict) and result.get("ok"):
            self.log(f"模式已切换到「{want}」")
            return
        self.log(f"模式切换没走通：{result}——按现状继续，回答深度可能不是你要的")

    # ------------------------------------------------------------------ 提交

    def submit_js(self, text: str) -> str:
        """聚焦 → 填入 → 回车 → 复核输入框已清空，全部塞进同一次 run-code。

        为什么不能拆成 fill / press 两条独立命令（豆包脚本实测踩过，同款架构同款坑）：
        每条命令是独立进程，命令之间的空档正好够页面完成一次重渲染，刚拿到的焦点
        会被冲掉，Enter 落空。症状是「命令条条成功、页面纹丝不动」，prompt 还留在
        输入框里没发出去。塞进同一个 Playwright 上下文连续执行，焦点才保得住。

        不先 click 输入框：fill 自己会聚焦，少一步就少一个失败点。这里的判空是
        **内联**的（不调 read_box_js），因为它跑在页面上下文里，读一次就够。
        """
        return (
            "async page => {"
            f"  const box = page.locator({json.dumps(self.INPUT_SELECTOR)});"
            f"  await box.fill({json.dumps(text, ensure_ascii=False)});"
            "  const filled = await box.innerText();"
            "  if (!filled.trim()) return JSON.stringify({ok: false, stage: 'fill'});"
            "  await page.keyboard.press('Enter');"
            "  await page.waitForTimeout(1500);"
            "  const left = await page.evaluate(() => {"
            f"    const el = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            "    if (!el) return '';"
            "    const ph = (el.getAttribute('data-placeholder') || '').trim();"
            "    const t = (el.innerText || '').replace(/\\ufeff/g, '').trim();"
            "    return t === ph ? '' : t;"
            "  });"
            "  return JSON.stringify({ok: !left, stage: 'submit', left: left});"
            "}"
        )

    # -------------------------------------------------------------- 会话清理

    def delete_conversation_js(self, conversation_id: str) -> str:
        """删掉左侧列表里指定会话：更多按钮 → 菜单「删除此对话」→ 确认框「确定」。

        开菜单那一下走 Playwright 的 click、不开菜单之后的步骤走 JS click，理由与
        switch_mode_js 同源：千问的会话菜单是 Radix 的，Trigger 只认 pointerdown，
        JS 的 el.click() 打不开它（2026-10-12 端到端实测：卡在 stage='menu-open'）；
        而 Trigger 之后的菜单项、确认按钮认 el.click()，用 JS 点就够。

        点「更多」之前先 hover 一下条目：那个按钮平时是收着的（实测非当前会话的条目上
        width=0、visibility:hidden），悬停才显形。hover 失败不致命，兜住继续走——
        删除的目标就是当前会话，它的按钮本来就是显形的。

        选择器一律钉上 aside 前缀：主内容区那个包装容器也带 data-session-id（值相同），
        不限定就会认错元素。

        每一步都先验证入口存在再点，并把卡住的步骤名带回去——菜单、确认框都是点完
        才渲染的，得等它们出现；哪一步没等到，日志里说得出是哪一步。
        """
        return (
            "async page => {"
            f"  const ID = {json.dumps(conversation_id)};"
            '  const itemSel = `aside [data-session-id="${ID}"]`;'
            "  if (!(await page.locator(itemSel).count()))"
            "    return JSON.stringify({ok: false, stage: 'locate'});"
            "  try {"
            "    await page.locator(itemSel).first().hover({timeout: 3000});"
            "  } catch (e) { /* 只是为了让「更多」显形，失败就按原样点 */ }"
            "  const moreSel = `aside button[data-session-switch-target=session-tools]"
            '[data-session-id="${ID}"]`;'
            "  try {"
            "    await page.locator(moreSel).click({timeout: 8000});"
            "  } catch (e) {"
            "    return JSON.stringify({ok: false, stage: 'more-button', err: String(e).slice(0, 120)});"
            "  }"
            "  return JSON.stringify(await page.evaluate(async () => {"
            # 同 switch_mode_js：回调被序列化送进页面执行，ID 得在回调里重新声明
            f"    const ID = {json.dumps(conversation_id)};"
            "    await new Promise(r => setTimeout(r, 1000));"
            "    const menu = document.querySelector('[role=menu][data-state=open]');"
            "    if (!menu) return {ok: false, stage: 'menu-open'};"
            "    const del = [...menu.querySelectorAll('[role=menuitem]')]"
            "      .find(i => (i.textContent || '').trim() === '删除此对话');"
            "    if (!del) return {ok: false, stage: 'menu-item'};"
            "    del.click();"
            "    await new Promise(r => setTimeout(r, 1200));"
            "    const dlg = document.querySelector('[role=dialog]');"
            "    if (!dlg) return {ok: false, stage: 'dialog'};"
            "    const sure = [...dlg.querySelectorAll('button')]"
            "      .find(b => (b.textContent || '').trim() === '确定');"
            "    if (!sure) return {ok: false, stage: 'confirm-button'};"
            "    sure.click();"
            # 侧栏列表更新是异步的，轮询到它消失为止，最多等 10 秒（实测通常 1 秒内就没了，
            # 但 kimi 那边固定等一拍会读早，这里索性统一用轮询）。
            '    const sel = `aside [data-session-id="${ID}"]`;'
            "    let remains = -1;"
            "    for (let i = 0; i < 20; i++) {"
            "      await new Promise(r => setTimeout(r, 500));"
            "      remains = document.querySelectorAll(sel).length;"
            "      if (remains === 0) break;"
            "    }"
            "    return {ok: remains === 0, stage: 'verify', remains};"
            "  }));"
            "}"
        )

    # --------------------------------------------------------- HTML → Markdown

    def convert_html(self, html: str) -> str:
        """把一段正文 HTML 还原成 Markdown——转交本文件的 convert()（见上面那段）。"""
        return convert(html)


if __name__ == "__main__":
    QwenChat().main()
