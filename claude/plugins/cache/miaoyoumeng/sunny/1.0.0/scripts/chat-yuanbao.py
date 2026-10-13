#!/usr/bin/env python3
"""
chat-yuanbao.py — 用 playwright-cli 驱动腾讯元宝网页版，批量提交 prompt 并取回 Markdown 回答

用法（在插件根目录执行，即 pyproject.toml 所在那一层）：

    # 提交两个 prompt，回答分别写进 out/1.md、out/2.md
    uv run python scripts/chat-yuanbao.py \
        --prompt="问题一" --prompt="问题二" --dir=out

    # 也可以只给一个文件：本次所有回答全写进它，第 1 个覆盖写、之后追加写
    uv run python scripts/chat-yuanbao.py \
        --prompt="问题一" --prompt="问题二" --file=out/汇总.md

    # 结果以 JSON 输出到 stdout，便于上层程序解析
    uv run python scripts/chat-yuanbao.py --prompt="问题" --dir=out --json

输出：进度日志走 stderr，最终结果走 stdout——重定向时能拿到干净的结果。
落盘位置 --dir 与 --file 二选一：--dir 给目录，每个 prompt 的回答写进目录下以序号
命名的 Markdown 文件（1.md、2.md …）；--file 给文件，本次所有回答都写进这一个文件
（第 1 个覆盖写、之后逐个追加）。顺序就是 prompt 的提交顺序。

流程（按顺序）：

1. 三步验证，每步各打一行日志（①②③），全过才开浏览器：
   ① 验证参数（--prompt 必填；--dir 与 --file 二选一，缺一个或都给都报错退出）→
   ② 验证输出位置（--dir 须已存在；--file 的父目录须已存在）→ ③ 验证登录状态。
   登录校验交给 platform-logined-validator.py --platform=yuanbao：未登录由它把
   窗口交给用户登，登不上（或超时）本脚本直接终止。
2. 打开（或复用）浏览器 → **窗口最小化** → 等页面就绪 → 确认模式 → 逐个提交
   prompt、等收尾、取回 Markdown。确认登录之后浏览器就不再占前台，全流程在后台跑；
   要看页面加 --show。
3. 每个回答写进 --dir/1.md、--dir/2.md …（或按 --file 追加进同一个文件），
   序号从 1 开始，就是 prompt 的提交顺序。
4. 删掉左侧列表里「本次交互」那条会话记录，再关闭浏览器。只删脚本自己新建的
   （提交前就存在的会话不动，免得误删历史）；想留着记录加 --keep-conversation。

**流程骨架在 `chat_base.py`**（模板方法模式）：三步验证、开浏览器、等页面就绪、
提交、等收尾、落盘、删会话、关浏览器都是那边写好的，本文件只写元宝的差异——
选择器、页面探测、提交方式（点发送不认回车）、收尾判据、删会话的 DOM 操作、
模式确认，以及页面特有的 HTML → Markdown 转换。要改公共流程请去改 chat_base.py，
改一处五个平台都生效。

与 yuanbao-picker 技能（sunny 插件）流程的差异，五处：

1. **一次会话提交多个 prompt**——按「提交 → 等本轮收尾 → 取本轮回答」串行推进，
   每个 prompt 对应一条响应，下标严格对齐。串行是必须的：并行提交会让两轮回答
   在页面上交叉，谁也认不出哪条回答属于哪个问题。
2. **登录交给 platform-logined-validator.py**——本脚本不自己判断登录、也不等
   用户登录，只认那个脚本的结论；它说没登上，这里立刻终止，后面都不开始。
3. **结果落盘**——技能要求把回答输出到控制台（不写文件），本脚本按批量提问的
   需要改成写文件（--dir 一个回答一个 .md，或 --file 全写进一个），拿文件走人
   即可，不必解析 stdout。
4. **模式显式确认**——技能要求提交前切到「深度思考」，本脚本每次都现查一遍，
   不是就切过去（已经是就不动）。只认这一种模式，不给别的留开关，理由见下面
   第 3 条平台特性。
5. **收尾多一步删会话**——技能里没这一步，见 chat_base.py 的 cleanup_conversation()。

元宝的五个平台特性（2026-10-12 实测），都直接决定选择器怎么写：

- **正文必须用直接子级选择器 `.hyc-component-deepsearch-cot > .hyc-content-md`**：
  思考过程里也挂着一份 `.hyc-content-md`，用后代选择器会把思考过程一起捞出来。
  这就是技能里那句「必须用 `>`」的由来。
- **提交不认回车，得点「发送」按钮**——`fill` 完文字留在输入框里，页面看不出
  任何异常，得点 `div[aria-label="发送"]` 才算发出（技能里专门警告过）。
- **会话 ID 藏在 URL 的第二段**：地址形如 `/chat/<智能体 ID>/<会话 ID>`，第一段
  是智能体 ID、同一个账号下所有会话都一样，拿它认会话会认错。侧栏条目上同理——
  要读 `data-conversation-id`，**别读 `dt-agent-id`**（那是智能体 ID，2026-10-12
  实测三条会话的这个属性完全相同）。id 长相是 base62 短串（形如 `0RBUlHABrkW`），
  与豆包的纯数字、deepseek / Kimi 的 UUID、千问的 32 位十六进制都不同。
  另外元宝**打开页面就在 /chat/<智能体 ID> 上**、提交后才跳进具体会话，
  所以「提交前侧栏没有、提交后有了」才是「本次新建」的判据，见 read_baseline()。
- **只走「深度思考」这一种模式**：技能点名要的就是它，本脚本不给「快速回答」
  留开关——实测快速模式的页面结构完全是另一套（正文不在 `.hyc-component-deepsearch-cot`
  里，见下条），而且会把一次提问渲染成**两个候选回答**的对比界面（「您更喜欢哪个
  回答」），一个 prompt 一条结果的约定在那儿根本不成立。切模式的代码留在
  ensure_mode() 里，只为把跑偏的模式拨回「深度思考」。
- **完成判据是「正文带上 hyc-content-md-done 且停止按钮消失」**：技能说 done 类
  不可靠，那是针对「全页搜这个类」的写法说的——思考过程那份也带这个类。圈定到
  正文容器上，实测它和停止按钮同步翻转（2026-10-12 实测：流式期间 done=false、
  停止按钮在；完成那一刻 done=true、停止按钮消失）。
- **「更多」按钮是开合开关（toggle）且悬停才显形**：平时 `display:none`，鼠标
  悬停到会话条目上才变成 `display:flex`。点它开菜单，再点会关——清理时若菜单
  已是开着的，第一次点击会把菜单关掉，所以点完要确认菜单在不在，不在就再点一次。

红线：不代用户登录、不触碰 cookie 与 token；写文件只写 --dir 目录下或 --file 指定的结果文件。
"""

from __future__ import annotations

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
# 这一段内联自 yuanbao-picker 技能的 scripts/extract_markdown.py（2026-10-10 实测版本）。
#
# 为什么不用第三方 Markdown 转换库：元宝页面有它特有的结构——段落是 div.ybc-p
# 而不是 p 标签（不按段落拦，段间换行会丢）、每个列表项前面挂一个装饰圆点
# span（内容就是 ∙，会被当成正文捞出来）、代码块的横幅里装着语言名和「复制」
# 按钮（不摘掉，语言名会和代码首行黏成「pythondef bubble_sort」）。通用库不认
# 这些，所以沿 DOM 反向推回 Markdown 语法。

# 语言标签只认这种长相的短标识，免得把「复制」「下载」这类按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")

# 元宝代码块：pre.ybc-pre-component。语言名在横幅里，横幅叫 .hyc-common-markdown__code__hd
CODE_BLOCK_CLASS = "ybc-pre-component"
CODE_LANG_SELECTOR = ".hyc-common-markdown__code__langComponent__text"
CODE_BANNER_SELECTOR = ".hyc-common-markdown__code__hd"

# 列表项前的装饰圆点（内容就是 ∙，纯装饰）
LIST_DOT_CLASSES = ("ybc-li-component_dot", "ybc-li-component__dot-wp")


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


def _code_block(node: Tag) -> str:
    """元宝的代码块：pre.ybc-pre-component。

    横幅（.hyc-common-markdown__code__hd）里装着语言名和「复制」按钮，是整个
    pre 中唯一不属于代码的文本。不摘掉它，这些界面文字会混进正文——实测会输出
    成「pythondef bubble_sort」这样：语言名和代码首行黏在一起。
    语言名要在摘横幅之前取，取完再摘。
    """
    label = node.select_one(CODE_LANG_SELECTOR)
    raw = label.get_text().strip() if label is not None else ""
    lang = raw if LANG_RE.fullmatch(raw) else ""

    banner = node.select_one(CODE_BANNER_SELECTOR)
    if banner is not None:
        banner.extract()

    code = node.get_text().rstrip("\n")
    return f"\n\n```{lang}\n{code}\n```\n\n"


def walk(node: object) -> str:
    if isinstance(node, NavigableString):
        # 注释、doctype 之类不是正文，丢掉
        return "" if isinstance(node, Comment) else _text(node)
    if not isinstance(node, Tag):
        return ""

    tag = node.name.lower()

    def kids() -> str:
        return "".join(walk(c) for c in node.children)

    # 元宝列表项前的装饰圆点，内容是 ∙，纯装饰。不拦下来会被 walk 当正文捞走，
    # 输出成「- ∙**时间复杂度**」这种带杂符的列表。
    if any(_has_class(node, c) for c in LIST_DOT_CLASSES):
        return ""

    # 公式必须在遍历子节点之前截断：KaTeX 渲染后会同时留下 katex-mathml
    # 与 katex-html 两份孪生内容，继续下探只会得到重复且错乱的文本。
    if _has_class(node, "katex-display"):
        return f"\n\n$$\n{_tex_of(node)}\n$$\n\n"
    if _has_class(node, "katex"):
        return f"${_tex_of(node)}$"
    if tag == "script" and (node.get("type") or "").startswith("math/tex"):
        return f"${node.get_text().strip()}$"

    if tag == "pre":
        if _has_class(node, CODE_BLOCK_CLASS):
            return _code_block(node)
        # 兜底：页面结构变了才会走到这里。语言信息拿不到，只保证代码本体不丢。
        return "\n\n```\n" + node.get_text().rstrip("\n") + "\n```\n\n"

    if tag in ("script", "style", "button", "svg", "noscript"):
        return ""

    if tag == "br":
        return "  \n"  # 行尾两个空格 = Markdown 硬换行

    if tag == "hr":
        return "\n\n---\n\n"

    if tag == "p" or _has_class(node, "ybc-p"):
        # 元宝的段落是 div.ybc-p，不是 p 标签。不按段落拦，段间换行会丢。
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
        # 块级代码由上层 pre 接走，走到这里只可能是行内代码
        return "`" + node.get_text() + "`"

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
            # 列表项内的空行不承载语义，压掉。元宝的嵌套列表前后挂着空白的
            # 文本节点，不压会在父项和子项之间留一串空行。
            text = re.sub(r"\n\s*\n+", "\n", text)
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


class YuanbaoChat(chat_base.ChatScript):
    """腾讯元宝网页版的批量提问脚本。流程见 chat_base.ChatScript.main()。

    本文件只负责元宝的差异：选择器、探测 JS、提交方式（点发送、不认回车）、
    收尾判据、删会话、双基线，以及上面那段 HTML → Markdown。
    """

    PLATFORM = config.YUANBAO
    LOG_PREFIX = "[yuanbao]"
    DESCRIPTION = "用 playwright-cli 驱动腾讯元宝网页版，批量提交 prompt 并取回 Markdown 回答"
    URL_LABEL = "元宝地址"
    LOGIN_FAILED_TEMPLATE = (
        "{prefix} 元宝未登录（登录校验退出码 {code}），流程终止。\n"
        "  请在浏览器窗口里登好元宝再重跑本脚本；登录由你本人完成，脚本不代登。"
    )

    # 元宝是点「发送」按钮提交的，不认回车——报错文案里说的是这一下
    SUBMIT_ACTION_LABEL = "点发送后"

    # 输入框：Quill 富文本编辑器。空着时带 ql-blank 类，占位文本在 data-placeholder。
    # 用选择器定位，不受 ref 失效影响（技能里用的是 snapshot + ref，那套要求每条
    # 命令前重新 snapshot，脚本里没法照搬）
    INPUT_SELECTOR = ".ql-editor"

    # 发送按钮。它不是 <button>，是个 div，文字为空——只能靠 aria-label 认
    SEND_SELECTOR = '[aria-label="发送"]'

    # 轮次容器：一轮问答占两个 item（--human 一个、--ai 一个），所以按 --ai 过滤，
    # 下标即轮次（0 起）。这是本脚本定位「第几轮」的唯一依据。
    ROUND_SELECTOR = ".agent-chat__list__item--ai"

    # 正文容器。必须带直接子级 `>`：思考过程里也挂着一份 .hyc-content-md，
    # 用后代选择器会把思考过程一起捞出来（技能里实测过，全部匹配 2 个）
    BODY_SELECTOR = ".hyc-component-deepsearch-cot > .hyc-content-md"

    # 正文带上这个类 = 这一轮生成完了。实测生成中不带、完成那一刻才带上。
    # 技能说它不可靠，是因为它同时挂在思考过程那一份上——圈定到正文容器就准了
    DONE_CLASS = "hyc-content-md-done"

    # 输入框下方的模式按钮，按钮文字就是当前模式名（「快速回答」/「深度思考」
    # /「专家模式」）。点开是 [role=menuitemradio] 的菜单，aria-checked 标当前项
    MODE_BUTTON_SELECTOR = "[data-thinking-mode-switcher-trigger]"
    MODE_DEEP = "深度思考"  # 深入推理，分析复杂问题——技能点名要的，本脚本只走这一种
    # 菜单里另有「快速回答」和「专家模式」。快速回答不给留开关：实测它的正文不在
    # 深度思考那套容器里，而且会渲染成两个候选回答的对比界面，一个 prompt 一条结果
    # 的约定不成立。常量留着是为了让 ensure_mode() 认得出「现在不是深度思考」。
    MODE_FAST = "快速回答"

    # 侧栏会话条目与它的「更多」按钮。
    #
    # 会话 ID 挂在条目的 data-conversation-id 上。**别拿 dt-agent-id 当会话 ID**：
    # 那是智能体 ID，同一个账号下所有会话都是同一个值（2026-10-12 实测踩过——
    # 侧栏 3 条会话的 dt-agent-id 全是 naQivTmsDa，照着它定位会删错会话）。
    SIDEBAR_ITEM_SELECTOR = ".yb-recent-conv-list__item"
    SIDEBAR_CONV_ATTR = "data-conversation-id"
    SIDEBAR_MORE_SELECTOR = ".yb-recent-conv-list__dropdown-trigger"
    SIDEBAR_MENU_ITEM_SELECTOR = ".yb-dropdown__item"
    DELETE_MENU_TEXT = "删除"
    DELETE_CONFIRM_TEXT = "确认删除"
    CONFIRM_DIALOG_SELECTOR = ".t-dialog"

    # 会话页 URL 形如 /chat/<智能体 ID>/<会话 ID>。**会话 ID 是第二段**——
    # 第一段是智能体 ID，同一个账号下所有会话都一样（见 SIDEBAR_CONV_ATTR 的提醒）。
    # 还在聊首页（/chat 或 /chat/<智能体 ID>）时匹配不上，返回 None，正合语义：
    # 那时还没有会话记录。
    CONVERSATION_URL_RE = re.compile(r"/chat/[A-Za-z0-9_-]+/([A-Za-z0-9_-]+)")

    # ---------------------------------------------------------- 平台特有槽位

    def prepare_page(self, session: str, baseline: int) -> int:
        """槽位 1 · 把模式拨到「深度思考」。

        模式按对话存，所以每次跑都现查一次再提交（技能里的危险信号：想当然沿用上次）。
        只认「深度思考」：别的模式页面结构不一样，取不回完整回答，见 MODE_FAST 的注释。
        轮数基线不受影响，原样返回。
        """
        self.ensure_mode(session, self.MODE_DEEP)
        return baseline

    def read_baseline(self, session: str) -> Any:
        """槽位 2 · 元宝要记两个基线：URL 上的会话 ID + 侧栏里的会话名单。

        它打开页面就已经站在 /chat/<智能体 ID> 上（那时侧栏里还没有本次会话），
        提交之后才跳进具体会话、才在侧栏出现一条记录。所以光看 URL 认不出新旧，
        得连侧栏名单一起记下来——判据见 cleanup_skip_reason()。

        侧栏名单**必须在这儿现读一次**，不能图省事复用 wait_page_ready 里读到的那份：
        那是「输入框就绪那一刻」的名单，比这里早（中间隔着 ensure_mode 的开菜单等待），
        条目若延迟加载，基线会偏小——而「目标不在基线名单里才删」是删除不可逆的
        唯一红线。多跑一趟浏览器命令换这个确定性，值。
        """
        return (self.read_conversation_id(session), set(self.read_sidebar_ids(session)))

    # -------------------------------------------------------------- 页面探测

    def read_sidebar_ids(self, session: str) -> list[str]:
        """读左侧列表里所有会话的 ID（条目上的 data-conversation-id），按显示顺序。

        侧栏收起时条目不在 DOM 里，这时会读到空列表——空列表本身也是有效信息，
        调用方自己判断含义（cleanup_skip_reason 拿它当「没得删」处理）。
        """
        ids = eval_js(
            session,
            f"(() => [...document.querySelectorAll({json.dumps(self.SIDEBAR_ITEM_SELECTOR)})]"
            f"  .map(e => e.getAttribute({json.dumps(self.SIDEBAR_CONV_ATTR)}))"
            ".filter(Boolean))()",
        )
        if not isinstance(ids, list):
            return []
        return [str(i) for i in ids]

    def read_box_js(self) -> str:
        """读出输入框里的真实内容，返回 `{text: ...}`（空串 = 输入框是空的）。

        Quill 空着时会把占位文本渲染进来（.ql-blank 状态），所以判空先看 ql-blank
        类，没有这个类才读文本——比拿 innerText 比对占位符干净。

        返回契约是 {text: ...}：判空规则不变，只是包了一层，好让 chat_base 的
        submit_prompt 用同一套取值代码（原来是裸字符串）。
        """
        return (
            "(() => {"
            f"  const el = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            "  if (!el) return JSON.stringify({text: null});"
            "  if (el.classList.contains('ql-blank')) return JSON.stringify({text: ''});"
            "  return JSON.stringify({text: (el.innerText || '').trim()});"
            "})()"
        )

    def page_state_js(self) -> str:
        """一次取回五件事：有没有「登录」按钮、输入框在不在、页面上已有几轮问答、
        当前是哪个模式、左侧列表里都有哪些会话。

        登录判据只认「登录」按钮 + 侧栏的「未登录」字样——和 validator 的
        YUANBAO_STATE_JS 保持一致。元宝会给匿名访客分一个默认昵称（形如「用户80e4」），
        光看有没有用户名分不出登没登录，所以只往「未登录」方向认。
        """
        return (
            "(() => {"
            "  const login = [...document.querySelectorAll('button')]"
            "    .filter(b => (b.textContent || '').trim() === '登录').length;"
            "  const nav = document.querySelector('[class*=yb-nav__user]');"
            "  const navText = nav ? (nav.textContent || '').trim() : '';"
            f"  const input = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            f"  const rounds = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)}).length;"
            f"  const modeBtn = document.querySelector({json.dumps(self.MODE_BUTTON_SELECTOR)});"
            f"  const sessions = [...document.querySelectorAll("
            f"{json.dumps(self.SIDEBAR_ITEM_SELECTOR)})]"
            f"    .map(e => e.getAttribute({json.dumps(self.SIDEBAR_CONV_ATTR)})).filter(Boolean);"
            "  return JSON.stringify({login_buttons: login,"
            "    logged_out_hint: navText.includes('未登录'),"
            "    input_ready: !!input, rounds: rounds,"
            "    mode: modeBtn ? (modeBtn.textContent || '').trim() : null,"
            "    sessions: sessions});"
            "})()"
        )

    def looks_logged_out(self, state: dict[str, Any]) -> bool:
        """「登录」按钮在、或侧栏写着「未登录」，就算登录态丢了。

        两个信号取或：元宝会给匿名访客分默认昵称，光看有没有用户名分不出登没登录。
        带上 input_ready：页面正在加载时读到的东西不作数。
        """
        return bool(state.get("input_ready")) and (
            bool(state.get("login_buttons")) or bool(state.get("logged_out_hint"))
        )

    def probe_js(self, index: int) -> str:
        """读第 index 轮（0 起，按 --ai 条目数）的收尾状态。

        为什么钉住第 index 个容器而不是「最后一条」：多轮连续提交时，新容器还没出现，
        页面上的最后一条仍是上一轮的已完成状态，看最后一条会把「还没开始」误判成
        「已收尾」。钉死下标才准。

        判据两个信号叠加，都满足才算完：

        1. 正文容器带上 hyc-content-md-done 类；
        2. 页面上没有「停止生成」按钮。

        实测两者同步翻转（2026-10-12：流式期间 done=false 且有停止按钮，完成那一刻
        同时变成 done=true、按钮消失）。叠着用是防止单个信号失灵时取到半截回答。
        """
        return (
            "(() => {"
            f"  const rounds = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)});"
            f"  if (rounds.length <= {index}) return 'wait:no-message';"
            f"  const item = rounds[{index}];"
            f"  const body = item.querySelector({json.dumps(self.BODY_SELECTOR)});"
            "  if (!body) return 'wait:no-body';"
            "  const streaming = [...document.querySelectorAll('[aria-label]')]"
            "    .some(e => /停止/.test(e.getAttribute('aria-label') || ''));"
            f"  const done = body.classList.contains({json.dumps(self.DONE_CLASS)});"
            "  if (!done) return 'wait:streaming';"
            "  if (streaming) return 'wait:stopping';"
            "  return 'done';"
            "})()"
        )

    def fetch_round_js(self, index: int) -> str:
        """取第 index 轮的全部正文容器 HTML（交给 Python 转 Markdown）。

        只在本轮条目内部找正文容器，思考过程那份不在 `>` 约束里，天然被挡在外面。
        """
        return (
            "(() => {"
            f"  const rounds = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)});"
            f"  if (rounds.length <= {index}) return [];"
            f"  return [...rounds[{index}].querySelectorAll({json.dumps(self.BODY_SELECTOR)})]"
            "    .map(e => e.outerHTML);"
            "})()"
        )

    # ---------------------------------------------------------------- 模式

    def switch_mode_js(self, want: str) -> str:
        """点开模式菜单 → 选目标项 → 读回按钮文字复核。

        菜单项是 [role=menuitemradio]，文字比按钮上长（「深度思考深入推理，分析复杂
        问题」），所以用 includes 匹配，不要求全等。菜单里还有一项 [role=menuitem]
        「模型Hy3」是选基础模型的，不是模式，不会误撞。

        开菜单那一下走 Playwright 的 click；菜单项改用页面里的 JS click——元宝这套
        菜单是自定义组件（类名 t-popup / yb-dropdown），实测真实点击开菜单、菜单项
        认 el.click()，两边都稳。**别用 locator 的 hasText 过滤去点菜单项**：实测
        在 [role=menuitemradio] 上 filter({hasText}) 匹配不上，改用页面里 find + click。
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
            # 变量在页面那边看不见（千问脚本实测报过 ReferenceError），所以字面量得在
            # 回调里面再声明一次。
            f"    const want = {json.dumps(want, ensure_ascii=False)};"
            "    await new Promise(r => setTimeout(r, 900));"
            "    const item = [...document.querySelectorAll('[role=menuitemradio]')]"
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
        """把模式调成 want（本脚本只传「深度思考」）。

        模式是按会话独立保存的，所以每次跑都现查，不沿用上次的记忆（技能里的危险
        信号之一就是「上次选过这次不查」）。已经是目标模式就什么都不点。

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
        """聚焦 → 填入 → 点「发送」→ 复核输入框已清空，全部塞进同一次 run-code。

        为什么不能拆成 fill / click 两条独立命令（豆包脚本实测踩过，同款架构同款坑）：
        每条命令是独立进程，命令之间的空档正好够页面完成一次重渲染，刚拿到的焦点
        会被冲掉。塞进同一个 Playwright 上下文连续执行，焦点才保得住。

        **元宝不认回车**：填完只按 Enter，文字会安安静静留在输入框里，页面没有任何
        异常表现（技能里专门警告过）。必须点「发送」——那个按钮不是 <button>，是个
        div，靠 aria-label 认。这里两次判空都是**内联**的（不调 read_box_js），
        因为它们跑在页面上下文里，各读一次就够。
        """
        return (
            "async page => {"
            f"  const box = page.locator({json.dumps(self.INPUT_SELECTOR)}).first();"
            "  try {"
            "    await box.click({timeout: 8000});"
            f"    await box.fill({json.dumps(text, ensure_ascii=False)});"
            "  } catch (e) {"
            "    return JSON.stringify({ok: false, stage: 'fill', err: String(e).slice(0, 120)});"
            "  }"
            "  const filled = await page.evaluate(() => {"
            f"    const el = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            "    if (!el || el.classList.contains('ql-blank')) return '';"
            "    return (el.innerText || '').trim();"
            "  });"
            "  if (!filled) return JSON.stringify({ok: false, stage: 'fill-empty'});"
            f"  const send = page.locator({json.dumps(self.SEND_SELECTOR, ensure_ascii=False)})"
            ".first();"
            "  try {"
            "    await send.click({timeout: 8000});"
            "  } catch (e) {"
            "    return JSON.stringify({ok: false, stage: 'send', err: String(e).slice(0, 120)});"
            "  }"
            "  await page.waitForTimeout(1500);"
            "  const left = await page.evaluate(() => {"
            f"    const el = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            "    if (!el || el.classList.contains('ql-blank')) return '';"
            "    return (el.innerText || '').trim();"
            "  });"
            "  return JSON.stringify({ok: !left, stage: 'submit', left: left});"
            "}"
        )

    def submit_failure_message(self, result: dict[str, Any]) -> str | None:
        """元宝的填字失败有两个阶段名（fill / fill-empty），报错里还带上 err 详情。"""
        if result.get("stage") in ("fill", "fill-empty"):
            return (
                f"{self.LOG_PREFIX} 文本没填进输入框（{result}）。\n"
                "  多半是输入框没就绪，请检查页面后重试。"
            )
        return None

    # -------------------------------------------------------------- 会话清理

    def delete_conversation_js(self, conversation_id: str) -> str:
        """删掉左侧列表里指定会话：悬停条目 → 更多按钮 → 菜单「删除」→ 对话框「确认删除」。

        「更多」按钮的脾气（2026-10-12 实测）：

        - 平时 `display:none`、尺寸为零，**鼠标悬停到会话条目上**才变成 `display:flex`；
          不先悬停就点，Playwright 会一直等「元素可见」直到超时。
        - 它是**开合开关**：菜单开着时再点一下会把菜单关掉。所以点完必须确认菜单在
          不在，不在就再点一次——不然「上一次操作残留的打开状态」会把这次的第一下
          点成关闭（探路时实测踩过：连着两次探查，一次拿到菜单、一次空手）。

        菜单项与确认按钮走页面里的 JS click（真实元素的 click 事件，实测都认）。
        菜单项按**文字全等**找：菜单里还有「批量操作」「移动到分组」「编辑名称」
        「分享」「置顶」，只有「删除」是两个字且完全相等，不会误撞。
        """
        return (
            "async page => {"
            f"  const ID = {json.dumps(conversation_id)};"
            '  const itemSel = `.yb-recent-conv-list__item[data-conversation-id="${ID}"]`;'
            "  if (!(await page.locator(itemSel).count()))"
            "    return JSON.stringify({ok: false, stage: 'locate'});"
            # 先悬停让「更多」显形。悬停失败不致命，兜住继续走。
            "  try {"
            "    await page.locator(itemSel).first().hover({timeout: 5000});"
            "  } catch (e) { /* 只为让「更多」显形，失败就按原样点 */ }"
            "  await page.waitForTimeout(700);"
            f"  const moreSel = `${{itemSel}} {self.SIDEBAR_MORE_SELECTOR}`;"
            "  const countItems = () => page.evaluate(() =>"
            f"    document.querySelectorAll({json.dumps(self.SIDEBAR_MENU_ITEM_SELECTOR)}).length);"
            "  const more = page.locator(moreSel).first();"
            "  try {"
            "    await more.click({timeout: 8000});"
            "  } catch (e) {"
            "    return JSON.stringify({ok: false, stage: 'more-button',"
            " err: String(e).slice(0, 120)});"
            "  }"
            "  let menuItems = 0;"
            "  for (let i = 0; i < 10 && !menuItems; i++) {"
            "    await page.waitForTimeout(300);"
            "    menuItems = await countItems();"
            "  }"
            "  if (!menuItems) {"
            # 「更多」是开合开关：上一状态若是开着的，这一下点成了关闭，补点一次
            "    try {"
            "      await more.click({timeout: 8000});"
            "    } catch (e) { /* 补点失败就走下面的菜单判定报错 */ }"
            "    for (let i = 0; i < 10 && !menuItems; i++) {"
            "      await page.waitForTimeout(300);"
            "      menuItems = await countItems();"
            "    }"
            "  }"
            "  if (!menuItems) return JSON.stringify({ok: false, stage: 'menu-open'});"
            "  return JSON.stringify(await page.evaluate(async () => {"
            # 同 switch_mode_js：回调被序列化送进页面执行，字面量得在回调里重新声明
            f"    const ID = {json.dumps(conversation_id)};"
            f"    const DEL = {json.dumps(self.DELETE_MENU_TEXT, ensure_ascii=False)};"
            f"    const SURE = {json.dumps(self.DELETE_CONFIRM_TEXT, ensure_ascii=False)};"
            f"    const LIST_SEL = {json.dumps(self.SIDEBAR_ITEM_SELECTOR)};"
            f"    const DIALOG_SEL = {json.dumps(self.CONFIRM_DIALOG_SELECTOR)};"
            "    const del = [...document.querySelectorAll('.yb-dropdown__item')]"
            "      .find(e => (e.textContent || '').trim() === DEL);"
            "    if (!del) return {ok: false, stage: 'menu-item'};"
            "    del.click();"
            "    await new Promise(r => setTimeout(r, 1200));"
            "    const dlgs = [...document.querySelectorAll(DIALOG_SEL)];"
            "    const dlg = dlgs.length ? dlgs[dlgs.length - 1] : null;"
            "    if (!dlg) return {ok: false, stage: 'dialog'};"
            "    const sure = [...dlg.querySelectorAll('button, .t-button')]"
            "      .find(b => (b.textContent || '').trim() === SURE);"
            "    if (!sure) return {ok: false, stage: 'confirm-button'};"
            "    sure.click();"
            # 侧栏列表更新是异步的，轮询到它消失为止，最多等 10 秒
            '    const sel = `${LIST_SEL}[data-conversation-id="${ID}"]`;'
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

    def cleanup_skip_reason(
        self, session: str, current_id: str | None, baseline: Any
    ) -> str | None:
        """四道保险，顺序都不能变。

        判据与别家同一个思路：只删「提交前还不存在」的会话。元宝的节奏是——打开
        页面时还没有会话（URL 停在 /chat/<智能体 ID>，不带第二段），提交之后才跳进
        具体会话、才在侧栏出现一条记录。所以拿提交前记下的侧栏名单做对照，收尾时
        多出来的那条就是本次新建的。

        四道：

        1. 侧栏里根本没有条目（侧栏收起或本来就没记录）→ 没得删；
        2. URL 里读不到会话 ID → 认不出哪条是本次的；
        3. 目标不在当前侧栏里 → 没有记录可删；
        4. 目标在提交前的名单里 → 那是用户的历史会话。

        第 4 道是红线：删除不可逆（确认框上写着「该对话内容将被删除无法恢复」），
        宁可留一条记录，也不能删到用户的会话。
        """
        # baseline[0]（URL 上的会话 ID）在这里用不上：元宝打开页面就站在
        # /chat/<智能体 ID> 上，那时 URL 里根本读不到会话 ID；真正的判据是侧栏名单。
        _url_id, baseline_ids = baseline
        sidebar_ids = self.read_sidebar_ids(session)
        if not sidebar_ids:
            return "左侧列表里没有会话条目（可能侧栏收起或本来就没有记录），跳过删除"
        if current_id is None:
            return "页面 URL 里读不到会话 ID，认不出哪条是本次的，跳过删除"
        if current_id not in sidebar_ids:
            return f"会话 {current_id} 还没进左侧列表，没有可删的记录，跳过"
        if current_id in baseline_ids:
            return (
                f"会话 {current_id} 提交前就在左侧列表里，不是本次新建的，不敢删——"
                "需要清理请到页面里手动删"
            )
        return None

    # --------------------------------------------------------- HTML → Markdown

    def convert_html(self, html: str) -> str:
        """把一段正文 HTML 还原成 Markdown——转交本文件的 convert()（见上面那段）。"""
        return convert(html)


if __name__ == "__main__":
    YuanbaoChat().main()
