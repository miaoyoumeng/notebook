#!/usr/bin/env python3
"""
chat-deepseek.py — 用 playwright-cli 驱动 DeepSeek 网页版，批量提交 prompt 并取回 Markdown 回答

用法（在插件根目录执行，即 pyproject.toml 所在那一层）：

    # 提交两个 prompt，回答分别写进 out/1.md、out/2.md
    uv run python scripts/chat-deepseek.py \
        --prompt="问题一" --prompt="问题二" --dir=out

    # 也可以只给一个文件：本次所有回答全写进它，第 1 个覆盖写、之后追加写
    uv run python scripts/chat-deepseek.py \
        --prompt="问题一" --prompt="问题二" --file=out/汇总.md

    # 结果以 JSON 输出到 stdout，便于上层程序解析
    uv run python scripts/chat-deepseek.py --prompt="问题" --dir=out --json

输出：进度日志走 stderr，最终结果走 stdout——重定向时能拿到干净的结果。
落盘位置 --dir 与 --file 二选一：--dir 给目录，每个 prompt 的回答写进目录下以序号
命名的 Markdown 文件（1.md、2.md …）；--file 给文件，本次所有回答都写进这一个文件
（第 1 个覆盖写、之后逐个追加）。顺序就是 prompt 的提交顺序。

流程（按顺序）：

1. 三步验证，每步各打一行日志（①②③），全过才开浏览器：
   ① 验证参数（--prompt 必填；--dir 与 --file 二选一，缺一个或都给都报错退出）→
   ② 验证输出位置（--dir 须已存在；--file 的父目录须已存在）→ ③ 验证登录状态。
   登录校验交给 platform-logined-validator.py --platform=deepseek：未登录由它把
   窗口交给用户登，登不上（或超时）本脚本直接终止。
2. 打开（或复用）浏览器 → **窗口最小化** → 等页面就绪 → 选中「深度思考」→
   逐个提交 prompt、等收尾、取回 Markdown。确认登录之后浏览器就不再占前台，
   全流程在后台跑；要看页面加 --show。
3. 每个回答写进 --dir/1.md、--dir/2.md …（或按 --file 追加进同一个文件），
   序号从 1 开始，就是 prompt 的提交顺序。
4. 删掉左侧列表里「本次交互」那条会话记录，再关闭浏览器。只删脚本自己新建的
   （提交前就存在的会话不动，免得误删历史）；想留着记录加 --keep-conversation。

**流程骨架在 `chat_base.py`**（模板方法模式）：三步验证、开浏览器、等页面就绪、
提交、等收尾、落盘、删会话、关浏览器都是那边写好的，本文件只写 DeepSeek 的差异——
选择器、页面探测、提交方式、收尾判据、删会话的 DOM 操作、「深度思考」开关，
以及页面特有的 HTML → Markdown 转换。要改公共流程请去改 chat_base.py，
改一处五个平台都生效。

与 deepseek-picker 技能（sunny 插件）流程的差异，三处：

1. **一次会话提交多个 prompt**——按「提交 → 等本轮收尾 → 取本轮回答」串行推进，
   每个 prompt 对应一条响应，下标严格对齐。串行是必须的：并行提交会让两轮回答
   在页面上交叉，谁也认不出哪条回答属于哪个问题。
2. **登录交给 platform-logined-validator.py**——本脚本不自己判断登录、也不等
   用户登录，只认那个脚本的结论；它说没登上，这里立刻终止，后面都不开始。
3. **结果落盘**——每个回答写进 --dir 下一个以序号命名的 .md 文件（或按 --file
   追加进同一个文件），拿文件走人即可，不必解析 stdout。

「深度思考」照技能步骤 4 走：先读 aria-pressed 判断选没选，没选才点——按钮是 toggle，
无条件点会把已选中的关掉。默认选上，`--no-deep-think` 可关。

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
# 这一段内联自 deepseek-picker 的 scripts/extract_markdown.py（实测踩坑版本）。
#
# 为什么不用第三方 Markdown 转换库：DeepSeek 页面有它特有的结构——公式的 KaTeX
# 孪生节点（katex-mathml 与 katex-html 各渲染一份）、代码块横幅里的语言标签与
# 「复制 / 下载」按钮。通用库不认这些，会把界面文字混进正文、把公式读成重复乱码。
# 所以沿 DOM 反向推回 Markdown 语法。

# 语言标签只认这种长相的短标识，免得把「复制」「下载」这类按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")


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

    # 代码块容器。语言标签和「复制」「下载」按钮都蹲在横幅里，是整个容器中唯一
    # 不属于代码的文本；不整块拦下来，这些界面文字会混进正文（实测会凭空多出
    # 「python复制下载」一行）。顺手把语言从标签取回来，填进围栏。
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
        # 块级代码由上层 .md-code-block 接走，走到这里只可能是行内代码
        return "`" + node.get_text() + "`"

    if tag == "pre":
        # 兜底：正常路径已被 .md-code-block 分支接走，走到这里说明页面结构变了。
        # 语言信息拿不到，只保证代码本体不丢。
        return "\n\n```\n" + node.get_text().rstrip("\n") + "\n```\n\n"

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


class DeepSeekChat(chat_base.ChatScript):
    """DeepSeek 网页版的批量提问脚本。流程见 chat_base.ChatScript.main()。

    本文件只负责 DeepSeek 的差异：选择器、探测 JS、提交方式、收尾判据、删会话、
    「深度思考」开关，以及上面那段 HTML → Markdown。
    """

    PLATFORM = config.DEEPSEEK
    LOG_PREFIX = "[deepseek]"
    DESCRIPTION = (
        "用 playwright-cli 驱动 DeepSeek 网页版，批量提交 prompt 并取回 Markdown 回答"
    )
    URL_LABEL = "DeepSeek 地址"
    LOGIN_FAILED_TEMPLATE = (
        "{prefix} DeepSeek 未登录（登录校验退出码 {code}），流程终止。\n"
        "  请在浏览器窗口里登好 DeepSeek 再重跑本脚本；登录由你本人完成，脚本不代登。"
    )

    # 轮次容器（deepseek-picker 2026-10 实测）：先试语义化类名，再回退 .ds-markdown，
    # 与技能里 extract_markdown.py 的取法一致。用户提问不带这两个类名，不会串进回答。
    ROUND_SELECTORS: ClassVar[list[str]] = [".ds-assistant-message-main-content", ".ds-markdown"]

    # 输入框：DeepSeek 是 textarea；#chat-input 是它在旧版里的 id，留着当首选。
    # contenteditable 是它的备用形态——三个都不认时 submit 会明确报错，不会静默失败。
    INPUT_SELECTORS: ClassVar[list[str]] = [
        "#chat-input",
        "textarea",
        "[contenteditable='true']",
    ]

    # 输入框与轮次容器都是「按顺序试」的候选列表，所以这里不声明基类那三个单值属性
    # （INPUT_SELECTOR / ROUND_SELECTOR / BODY_SELECTOR），用到它们的方法全部覆写。

    # 登录态判据：未登录时整页就是登录表单，连输入框都没有（见 validator 里同名探针）
    SIGN_IN_CLASS_HINT = "[class*=ds-sign-in-form]"
    SIGN_IN_PATH = "/sign_in"

    # 「深度思考」开关：.ds-toggle-button 里文字含「深度思考」的那个，选中态看 aria-pressed
    TOGGLE_SELECTOR = ".ds-toggle-button"
    DEEP_THINK_LABEL = "深度思考"

    # 回答区长度连续几次探询不变才认作收尾。2 表示要跨两个轮询间隔（默认 5 秒 → 10 秒），
    # 要两次而不是一次，是为了跨过流式输出中途那几秒停顿（工具调用、思考切换）
    STABLE_ROUNDS = 2

    # 会话页 URL 形如 /a/chat/s/<uuid>，收尾时按这个 ID 去左侧列表认本次那条会话
    CONVERSATION_URL_RE = re.compile(r"/a/chat/s/([0-9a-fA-F-]+)")

    # 挡路的模态弹窗。deepseek 目前没实测撞上过（豆包访问 /chat 必弹「下载电脑版」），
    # 留着这道是为了页面改版时能自愈：认不出来就什么都不做，静默通过。
    # 关闭按钮用 JS 直接 .click()：不走指针事件，绕开遮罩拦截。
    DISMISS_DIALOGS_JS = (
        "(() => {"
        "  const dialogs = [...document.querySelectorAll('[role=dialog][data-state=open]')];"
        "  let closed = 0;"
        "  for (const d of dialogs) {"
        "    const btns = [...d.querySelectorAll('button')];"
        "    const pick = btns.find(b => ['关闭', '知道了', '跳过'].includes((b.innerText || '')"
        ".trim()))"
        "      || btns.find(b => (b.getAttribute('aria-label') || '').trim() === '关闭');"
        "    if (pick) { pick.click(); closed += 1; }"
        "  }"
        "  return JSON.stringify({dialogs: dialogs.length, closed: closed});"
        "})()"
    )

    # ---------------------------------------------------------- 平台特有槽位

    def dismiss_dialogs(self, session: str) -> None:
        """关掉挡路的模态弹窗；没有弹窗时静默通过。"""
        result = eval_js(session, self.DISMISS_DIALOGS_JS)
        if isinstance(result, dict) and result.get("closed"):
            self.log(f"关掉了 {result['closed']} 个挡路的弹窗")

    def prepare_page(self, session: str, baseline: int) -> int:
        """槽位 1 · 页面就绪之后先清一次挡路的弹窗。轮数基线不受影响，原样返回。"""
        self.dismiss_dialogs(session)
        return baseline

    def after_baseline(self, session: str, baseline: Any) -> None:
        """槽位 3 · 选中「深度思考」模式。

        它是会话级的开关，提第一个问题前设一次就够。**原本就排在读会话基线之后**，
        位置别挪（这是它与其他平台不同的地方）。
        """
        if self.args.no_deep_think:
            self.log("按 --no-deep-think 跳过「深度思考」")
        else:
            self.select_deep_think(session)

    def add_platform_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--no-deep-think", action="store_true", help="不选「深度思考」模式（默认会选上）"
        )

    # -------------------------------------------------------------- 页面探测

    def round_nodes_js(self) -> str:
        """「取出全部轮次容器」那段 JS，三处共用。

        抽出来是为了让三处选择器永远一致：数轮次、探收尾、取 HTML 认的是同一组容器。
        任何一处走样，下标就会错位——第 2 个 prompt 可能取到第 1 轮的回答。
        """
        return (
            f"  const sels = {json.dumps(self.ROUND_SELECTORS)};"
            "  let nodes = [];"
            "  for (const s of sels) {"
            "    const hits = document.querySelectorAll(s);"
            "    if (hits.length) { nodes = [...hits]; break; }"
            "  }"
        )

    def page_state_js(self) -> str:
        """一次取回三件事：是不是登录页、输入框在不在、页面上已有几轮回答。

        登录判据与 platform-logined-validator.py 的 deepseek 探针保持一致：未登录时
        整页就是登录表单（跳到 /sign_in，或页面上挂着 ds-sign-in-form），输入框还没渲染。
        """
        return (
            "(() => {"
            + self.round_nodes_js()
            + f"  const signIn = location.pathname.startsWith({json.dumps(self.SIGN_IN_PATH)})"
            f" || !!document.querySelector({json.dumps(self.SIGN_IN_CLASS_HINT)});"
            f"  const input = document.querySelector("
            f"{json.dumps(', '.join(self.INPUT_SELECTORS))});"
            "  return JSON.stringify({sign_in: signIn, input_ready: !!input,"
            " rounds: nodes.length});"
            "})()"
        )

    def looks_logged_out(self, state: dict[str, Any]) -> bool:
        """停在登录页就是登录态丢了。

        DeepSeek 未登录时输入框根本不渲染，所以判据**不带 input_ready**——
        只看「是不是停在登录页」；页面还没加载完时 signIn 为假，自然继续等。
        """
        return bool(state.get("sign_in"))

    def logout_recheck_seconds(self) -> float:
        """DeepSeek 实测复核间隔 1.0 秒（其余平台是 1.5，别顺手统一）。"""
        return 1.0

    def read_box_js(self) -> str:
        """读回输入框现有文本（fill 不回显填入的内容，要校验只能读回来）。

        找元素的方式要和 submit_js 完全一致——同样按 INPUT_SELECTORS 的顺序、同样
        取最后一个可见的。两边不一致就会读错元素：提交填的是这一个、复核读的是那一个，
        于是「输入框已清空」这个判据全是假的。输入框形态还不定（textarea 或
        contenteditable），取值方式随之不同。
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
        """读第 index 轮（0 起）的收尾状态。

        为什么盯住第 index 个容器而不是「最后一个」：多轮连续提交时，回车后新容器
        还没出现，页面上的最后一个仍是上一轮的已完成状态，看最后一个会把「还没开始」
        误判成「已收尾」。钉死下标才准。
        """
        return (
            "(() => {"
            + self.round_nodes_js()
            + f"  if (nodes.length <= {index})"
            " return JSON.stringify({state: 'wait:no-message', length: 0, stop: false});"
            + "  const stop = [...document.querySelectorAll('button, [role=button]')]"
            "    .some(b => { const t = (b.textContent || '').trim();"
            "      return t === '停止生成' || t === '停止'; });"
            f"  const text = (nodes[{index}].textContent || '').trim();"
            "  return JSON.stringify({state: 'ok', length: text.length, stop: stop});"
            "})()"
        )

    def fetch_round_js(self, index: int) -> str:
        """取第 index 轮的整轮 HTML（DeepSeek 的正文就在整轮容器里，不再往下细分）。"""
        return (
            "(() => {"
            + self.round_nodes_js()
            + f"  if (nodes.length <= {index}) return [];"
            + f"  return [nodes[{index}].outerHTML];"
            "})()"
        )

    # ------------------------------------------------------------ 深度思考开关

    def deep_think_js(self) -> str:
        """找「深度思考」按钮 → 读 aria-pressed → 没选才点 → 复核。

        四步塞进同一次 run-code：分成多条命令的话，命令之间的空档够页面重渲染，
        读完状态再点，读到的可能已经是过期的（理由同 submit_js）。
        """
        return (
            "async page => {"
            f"  const btns = page.locator({json.dumps(self.TOGGLE_SELECTOR)});"
            "  const n = await btns.count();"
            "  for (let i = 0; i < n; i++) {"
            "    const b = btns.nth(i);"
            "    const text = await b.evaluate(el => (el.textContent || '').trim());"
            f"    if (!text.includes({json.dumps(self.DEEP_THINK_LABEL)})) continue;"
            "    if ((await b.getAttribute('aria-pressed')) === 'true')"
            "      return JSON.stringify({ok: true, action: 'already'});"
            "    await b.click();"
            "    await page.waitForTimeout(800);"
            "    const after = await b.getAttribute('aria-pressed');"
            "    return JSON.stringify({ok: after === 'true', action: 'clicked', pressed: after});"
            "  }"
            "  return JSON.stringify({ok: false, action: 'not-found'});"
            "}"
        )

    def select_deep_think(self, session: str) -> None:
        """选中「深度思考」模式。

        deepseek-picker 的步骤 4，判据原样照搬：snapshot 看不出选没选，只能读
        aria-pressed；而且按钮是 toggle，**必须先判断再点**，无条件点一下会把
        已选中的关掉。

        找不到按钮不算错：页面改版可能换了类名或去掉这个开关，为它中断整个流程不值当，
        照常提问就是，日志里说一声。点了没切过来同理。
        """
        result = run_code(session, self.deep_think_js())
        if not isinstance(result, dict):
            sys.exit(f"{self.LOG_PREFIX} 「深度思考」的检查结果无法解析：{result!r}")

        action = result.get("action")
        if action == "already":
            self.log("「深度思考」已经是选中状态")
        elif result.get("ok"):
            self.log("已选中「深度思考」")
        elif action == "not-found":
            self.log("页面上没找到「深度思考」按钮，跳过这一步（不影响提问）")
        else:
            self.log(
                f"「深度思考」点了但没切到选中状态（aria-pressed={result.get('pressed')}），"
                "继续往下走"
            )

    # ------------------------------------------------------------------ 提交

    def submit_js(self, text: str) -> str:
        """聚焦 → 填入 → 回车，全部塞进同一次 run-code。

        为什么不能拆成 fill / click / press 三条独立命令（实测踩过）：每条命令是独立
        进程，命令之间的空档正好够页面完成一次重渲染，刚拿到的焦点会被冲掉，Enter
        落空。症状是「命令条条成功、页面纹丝不动」，prompt 还留在输入框里没发出去。
        塞进同一个 Playwright 上下文连续执行，焦点才保得住。

        输入框按 #chat-input → textarea → contenteditable 逐个试，取最后一个可见的：
        聊天页的输入框在所有匹配里排最后，用 .last() 而不是 .first() 是为了躲开页面上
        那些隐藏的、别的用途的同名元素。
        """
        sels = json.dumps(self.INPUT_SELECTORS)
        return (
            "async page => {"
            # 弹窗可能在页面加载完之后才弹出来，提交前再清一次，别让它挡住输入框
            f"  await page.evaluate({json.dumps(self.DISMISS_DIALOGS_JS)});"
            f"  const sels = {sels};"
            "  let box = null;"
            "  for (const s of sels) {"
            "    const cand = page.locator(s).last();"
            "    if (await cand.count() && await cand.isVisible()) { box = cand; break; }"
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
        """DeepSeek 多一种失败：三个输入框选择器一个都没命中。"""
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

        DeepSeek 的探针返回的是个对象（状态 + 字数 + 停止按钮），这里把它归一成
        **有限的几个状态字符串**——字数只进 memory，不进状态串。把字数编进状态
        字符串的话，每轮长度一变就算「状态变了」，长回答会把日志刷满。
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
        if bool(info.get("stop")):
            # 停止按钮还在，收尾无从谈起
            memory["stable"] = 0
            memory["last_length"] = length
            return "wait:streaming"
        if length > 0 and length == memory.get("last_length"):
            memory["stable"] = int(memory.get("stable", 0)) + 1
            return "wait:stable"
        memory["stable"] = 0
        memory["last_length"] = length
        return "wait:growing"

    def is_round_done(self, status: str, memory: dict[str, Any], index: int) -> bool:
        """回答区长度连续 STABLE_ROUNDS 次不变才算收尾。

        要求两次而不是一次，是因为流式输出中途常有几秒停顿（工具调用、思考切换），
        停一次就取会截在半截。长度为 0 不算「稳定」：思考阶段正文容器可能已经挂上、
        内容还没开始写，连着读到几次 0 就认作收尾的话，会取回一个空回答。
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
        """删掉左侧列表里指定会话：hover 出「⋯」→ 菜单点「删除」→ 弹窗点「删除该对话」。

        每一步都先验证入口存在再点，并把卡住的步骤名带回去——菜单、弹窗都是点完才
        渲染的，选择器要等它们出现；哪一步没等到，日志里说得出是哪一步。
        """
        link_sel = json.dumps(f'a[href*="/a/chat/s/{conversation_id}"]')
        more_sel = json.dumps('div[role="button"]')
        menu_sel = json.dumps(".ds-dropdown-menu-option__label")
        return (
            "async page => {"
            f"  const link = page.locator({link_sel}).first();"
            "  if (!(await link.count())) return JSON.stringify({ok: false, stage: 'locate'});"
            "  await link.hover();"
            "  await page.waitForTimeout(400);"
            f"  await link.locator({more_sel}).first().click();"
            "  await page.waitForTimeout(700);"
            f"  const del = page.locator({menu_sel})"
            ".getByText('删除', { exact: true }).first();"
            "  if (!(await del.count())) return JSON.stringify({ok: false, stage: 'menu'});"
            "  await del.click();"
            "  await page.waitForTimeout(900);"
            "  const confirm = page.getByText('删除该对话', { exact: true }).last();"
            "  if (!(await confirm.count())) return JSON.stringify({ok: false, stage: 'confirm'});"
            "  await confirm.click();"
            "  await page.waitForTimeout(1500);"
            f"  const remains = await page.locator({link_sel}).count();"
            "  return JSON.stringify({ok: remains === 0, stage: 'verify', remains});"
            "}"
        )

    # --------------------------------------------------------- HTML → Markdown

    def convert_html(self, html: str) -> str:
        """把一段正文 HTML 还原成 Markdown——转交本文件的 convert()（见上面那段）。"""
        return convert(html)


if __name__ == "__main__":
    DeepSeekChat().main()
