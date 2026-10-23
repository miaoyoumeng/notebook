#!/usr/bin/env python3
"""
chat-glm.py — 用 playwright-cli 驱动智谱 GLM 网页版，批量提交 prompt 并取回 Markdown 回答

用法（在插件根目录执行，即 pyproject.toml 所在那一层）：

    # 提交两个 prompt，回答分别写进 out/1.md、out/2.md
    uv run python scripts/chat-glm.py \
        --prompt="问题一" --prompt="问题二" --dir=out

    # 也可以只给一个文件：本次所有回答全写进它，第 1 个覆盖写、之后追加写
    uv run python scripts/chat-glm.py \
        --prompt="问题一" --prompt="问题二" --file=out/汇总.md

    # 结果以 JSON 输出到 stdout，便于上层程序解析
    uv run python scripts/chat-glm.py --prompt="问题" --dir=out --json

输出：进度日志走 stderr，最终结果走 stdout——重定向时能拿到干净的结果。
落盘位置 --dir 与 --file 二选一：--dir 给目录，每个 prompt 的回答写进目录下以序号
命名的 Markdown 文件（1.md、2.md …）；--file 给文件，本次所有回答都写进这一个文件
（第 1 个覆盖写、之后逐个追加）。顺序就是 prompt 的提交顺序。

流程（按顺序）：

1. 三步验证，每步各打一行日志（①②③），全过才开浏览器：
   ① 验证参数（--prompt 必填；--dir 与 --file 二选一，缺一个或都给都报错退出）→
   ② 验证输出位置（--dir 须已存在；--file 的父目录须已存在）→ ③ 验证登录状态。
   登录校验交给 platform-logined-validator.py --platform=glm：未登录由它把窗口交给
   用户登，登不上（或超时）本脚本直接终止。
2. 打开（或复用）浏览器 → **窗口最小化** → 等页面就绪 → 把「思考深度」切到 Max →
   逐个提交 prompt、等收尾、取回 Markdown。确认登录之后浏览器就不再占前台，
   全流程在后台跑；要看页面加 --show。
3. 每个回答写进 --dir/1.md、--dir/2.md …（或按 --file 追加进同一个文件），
   序号从 1 开始，就是 prompt 的提交顺序。
4. 关掉浏览器。**没有「删会话」这一步**——体验中心的对话不落库，刷新即清，
   没有可以删的记录（详见 cleanup_skip_reason）。

**流程骨架在 `chat_base.py`**（模板方法模式）：三步验证、开浏览器、等页面就绪、
提交、等收尾、落盘、关浏览器都是那边写好的，本文件只写 GLM 的差异——选择器、
页面探测、提交方式、收尾判据、「思考深度」开关，以及页面特有的 HTML → Markdown。
要改公共流程请去改 chat_base.py，改一处所有平台都生效。

与 deepseek 版的差异（都是页面本身不一样，流程一模一样）：

1. **入口是体验中心**——https://bigmodel.cn/trialcenter/modeltrial/text，不是独立
   的聊天站；未登录访问会被整页重定向到 /login（判据与 validator 的 glm 探针一致）。
2. **多一个「思考深度」开关**——deepseek 切「深度思考」，GLM 切「思考深度：Max」，
   默认就是 Max，不是才动（见 select_max_thinking）。
3. **不删会话**——体验中心没有会话列表，URL 里也不带会话 ID，对话刷新即清。

实测记录（2026-10-13，页面结构以那天为准）：

- 输入框是 `textarea.el-textarea__inner`，**回车即发送**：页面上没有常驻的发送按钮，
  文本填进去之后才冒出一个 `.submit-btn` 图标按钮，所以提交走 Enter、不走点按钮。
- 一轮对话 = 一个 `.chat-item`（用户提问与回答都在里面），回答正文是其中的
  `.markdown-body`（markdown-it-vue 渲染）。同一条 `.chat-item` 上还挂着
  `data-answer="CHAT_ANSWER__N"`，将来要精确定位轮次可以走这个属性。
- 「思考深度」控件是 `.thinking-depth-tag`，`name` 属性形如 `思考深度_max`；
  点开弹层 `.thinking-depth-popper`，选项是 `ul.dropdown-menu-content > li`，
  选中的那条带 `selected` 类。
- 对话不持久化：刷新页面后 `.chat-item` 归零，侧栏是导航菜单而不是会话列表。

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
# 正文由 markdown-it-vue 渲染，产出的是 markdown-it 的标准 HTML：代码块是
# <pre><code class="language-xxx">，标签语义规整，没有 deepseek 那种横幅式代码块组件。
#
# 为什么不用第三方 Markdown 转换库：通用的库认不出页面塞在正文里的界面元素——
# KaTeX 的孪生节点（katex-mathml 与 katex-html 各渲染一份，直接下探会读到重复且
# 错乱的公式）、代码块上的「复制」按钮。这些都会混进正文，所以沿 DOM 反向推回
# Markdown 语法，公式与代码块两处显式截断。
#
# deepseek 那套 .md-code-block 分支也留着：GLM 现在不用它，但两边结构真重合时
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

    # deepseek 风格的代码块容器（带横幅、语言标签、「复制」「下载」按钮）。GLM 不用，
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
        # markdown-it 的标准代码块：<pre><code class="language-x">。
        # 语言名藏在 code 的 class 里，取不到就交空围栏，只保证代码本体不丢。
        code_el = node.find("code")
        if code_el is None:
            return "\n\n```\n" + node.get_text().rstrip("\n") + "\n```\n\n"
        classes = " ".join(code_el.get("class") or [])
        found = CODE_LANG_RE.search(classes)
        lang = found.group(1) if found else ""
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


class GLMChat(chat_base.ChatScript):
    """智谱 GLM 网页版（bigmodel.cn 体验中心）的批量提问脚本。流程见 chat_base.ChatScript.main()。

    本文件只负责 GLM 的差异：选择器、探测 JS、提交方式、收尾判据、「思考深度」开关，
    以及上面那段 HTML → Markdown。
    """

    PLATFORM = config.GLM
    LOG_PREFIX = "[glm]"
    DESCRIPTION = (
        "用 playwright-cli 驱动智谱 GLM 网页版（bigmodel.cn 体验中心），"
        "批量提交 prompt 并取回 Markdown 回答"
    )
    URL_LABEL = "智谱 GLM 地址"
    LOGIN_FAILED_TEMPLATE = (
        "{prefix} 智谱 GLM 未登录（登录校验退出码 {code}），流程终止。\n"
        "  请在浏览器窗口里登好智谱账号再重跑本脚本；登录由你本人完成，脚本不代登。"
    )

    # 轮次容器与正文容器：一轮对话一个 .chat-item，回答正文是其中的 .markdown-body。
    # 用户提问在同一个 .chat-item 里，但用的是 .chat-prompt-text（不是 .markdown-body），
    # 所以按 BODY_SELECTOR 取正文不会把提问串进回答。
    ROUND_SELECTOR = ".chat-item"
    BODY_SELECTOR = ".markdown-body"

    # 输入框按顺序试，取最后一个可见的。页面现在只有一个 textarea，多留两个是给改版兜底；
    # 三个都不认时 submit 会明确报错，不会静默失败。用到它们的方法覆写基类那三个单值属性。
    INPUT_SELECTORS: ClassVar[list[str]] = [
        "textarea.el-textarea__inner",
        "textarea",
        "[contenteditable='true']",
    ]

    # 未登录时整页被重定向到 /login（判据与 validator 的 glm 探针一致）
    SIGN_IN_PATH = "/login"

    # 「思考深度」控件：触发器带 name 属性形如「思考深度_max」，值是当前模式
    THINKING_TAG_SELECTOR = ".thinking-depth-tag"
    THINKING_POPPER_SELECTOR = ".thinking-depth-popper"
    THINKING_OPTION_SELECTOR = "ul.dropdown-menu-content > li"
    THINKING_OPTION_TITLE_SELECTOR = ".option-title"
    THINKING_TARGET = "Max"

    # 回答区长度连续几次探询不变才认作收尾。2 表示要跨两个轮询间隔（默认 5 秒 → 10 秒），
    # 要两次而不是一次，是为了跨过流式输出中途那几秒停顿。
    #
    # 这里**不认「停止生成」按钮**：GLM 有没有这个按钮没能实测到（账号余额不足，
    # 生成被服务端当场挡回，看不到流式过程），只在长度上做判据。空回答不算数
    # （见 is_round_done），所以 Max 模式那段不写正文的思考期不会被误判成收尾。
    STABLE_ROUNDS = 2

    # 体验中心的对话不落在 URL 里：地址恒为 /trialcenter/modeltrial/text，点「新建对话」
    # 也不变，所以这条正则现在匹配不到东西。留着它是给基类的 read_conversation_id 一个
    # 明确的答案（恒为 None → 没有本次新建的会话），收尾的删会话那步会被跳过，
    # 理由见 cleanup_skip_reason。
    CONVERSATION_URL_RE = re.compile(r"/trialcenter/modeltrial/text/([0-9a-zA-Z-]{6,})")

    # 挡路的模态弹窗（Element UI 的 el-dialog）。实测遇到的是「邀请新用户」弹窗，
    # 它不是每次都在，但一旦弹出来就会盖住输入框。关闭按钮取对话框右上角那颗
    # （.el-dialog__headerbtn），认不出来就什么都不做，静默通过。
    DISMISS_DIALOGS_JS = (
        "(() => {"
        "  const vis = el => { const r = el.getBoundingClientRect();"
        " return r.width > 0 && r.height > 0; };"
        "  const dialogs = [...document.querySelectorAll('.el-dialog__wrapper')].filter(vis);"
        "  let closed = 0;"
        "  for (const d of dialogs) {"
        "    const btn = d.querySelector('.el-dialog__headerbtn');"
        "    if (btn) { btn.click(); closed += 1; }"
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
        """槽位 3 · 把「思考深度」切到 Max。

        它是会话级的设置，提第一个问题前设一次就够。位置与 deepseek 的
        select_deep_think 一致（读会话基线之后），别挪。
        """
        if self.args.no_max_thinking:
            self.log("按 --no-max-thinking 保持页面上现有的「思考深度」")
        else:
            self.select_max_thinking(session)

    def add_platform_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--no-max-thinking",
            action="store_true",
            help="不切「思考深度：Max」，保持页面上当前的档位（默认会切到 Max）",
        )

    # -------------------------------------------------------------- 页面探测

    def page_state_js(self) -> str:
        """一次取回三件事：是不是登录页、输入框在不在、页面上已有几轮对话。

        登录判据与 platform-logined-validator.py 的 glm 探针保持一致：未登录访问体验
        中心会被整页重定向到 /login。**不带 input_ready**——未登录时页面已经跳走，
        根本没有输入框，看 URL 就够（deepseek 同理）。
        """
        sels = json.dumps(", ".join(self.INPUT_SELECTORS))
        return (
            "(() => {"
            "  const vis = el => { const r = el.getBoundingClientRect();"
            " return r.width > 0 && r.height > 0; };"
            f"  const hits = [...document.querySelectorAll({sels})].filter(vis);"
            f"  const signIn = location.pathname.startsWith({json.dumps(self.SIGN_IN_PATH)});"
            "  return JSON.stringify({sign_in: signIn, input_ready: hits.length > 0,"
            f" rounds: document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)}).length}});"
            "})()"
        )

    def looks_logged_out(self, state: dict[str, Any]) -> bool:
        """停在登录页就是登录态丢了（与 validator 的 glm 探针同一套判据）。"""
        return bool(state.get("sign_in"))

    def logout_recheck_seconds(self) -> float:
        """GLM 实测复核间隔 1.5 秒（与基类默认一致，写出来是为了与 deepseek 的偏置对照）。"""
        return 1.5

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
        """读第 index 轮（0 起）的收尾状态：这一轮回答正文的字符数。

        为什么盯住第 index 个 .chat-item 而不是「最后一个」：多轮连续提交时，回车后
        新容器还没出现，页面上的最后一条仍是上一轮的已完成状态，看最后一个会把
        「还没开始」误判成「已收尾」。钉死下标才准。

        正文还没挂上（.markdown-body 不存在）时长度按 0 算，由 is_round_done 那条
        「长度为 0 不算稳定」的规则兜住。
        """
        return (
            "(() => {"
            f"  const items = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)});"
            f"  if (items.length <= {index})"
            " return JSON.stringify({state: 'wait:no-message', length: 0});"
            f"  const body = items[{index}].querySelector({json.dumps(self.BODY_SELECTOR)});"
            "  const text = body ? (body.textContent || '').trim() : '';"
            "  return JSON.stringify({state: 'ok', length: text.length});"
            "})()"
        )

    # ------------------------------------------------------------ 思考深度开关

    def max_thinking_js(self) -> str:
        """读当前档位 → 不是 Max 才展开弹层 → 点 Max → 复核。

        四步塞进同一次 run-code：分成多条命令的话，命令之间的空档够页面重渲染，
        读完状态再点，读到的可能已经是过期的（理由同 submit_js）。

        当前档位读的是触发器的 name 属性（`思考深度_max` 这种），比解析「思考深度：Max」
        这段展示文字稳——文字排版改起来比属性随意得多。弹层点击是 toggle，所以先看
        一眼它是不是已经展开（display 非 none），展开了就直接选项，别把弹层点关。
        """
        tag = json.dumps(self.THINKING_TAG_SELECTOR)
        popper = json.dumps(self.THINKING_POPPER_SELECTOR)
        option = json.dumps(self.THINKING_OPTION_SELECTOR)
        title = json.dumps(self.THINKING_OPTION_TITLE_SELECTOR)
        target = json.dumps(self.THINKING_TARGET)
        return (
            "async page => {"
            f"  const tag = page.locator({tag}).first();"
            "  if (!(await tag.count())) return JSON.stringify({ok: false, action: 'not-found'});"
            "  const name = (await tag.getAttribute('name')) || '';"
            f"  if (new RegExp('_' + {target} + '$', 'i').test(name))"
            "    return JSON.stringify({ok: true, action: 'already', name: name});"
            "  const shown = await page.evaluate(sel => {"
            "    const p = document.querySelector(sel);"
            "    return !!p && getComputedStyle(p).display !== 'none';"
            f"  }}, {popper});"
            "  if (!shown) {"
            "    await tag.click();"
            "    await page.waitForTimeout(700);"
            "  }"
            f"  const items = page.locator({option});"
            "  const n = await items.count();"
            "  let picked = false;"
            "  for (let i = 0; i < n; i++) {"
            f"    const t = (await items.nth(i).locator({title}).innerText()).trim();"
            f"    if (t === {target}) {{ await items.nth(i).click(); picked = true; break; }}"
            "  }"
            "  if (!picked) return JSON.stringify({ok: false, action: 'option-not-found'});"
            "  await page.waitForTimeout(900);"
            "  const after = (await tag.getAttribute('name')) || '';"
            f"  return JSON.stringify({{ok: new RegExp('_' + {target} + '$', 'i').test(after),"
            " action: 'clicked', name: after});"
            "}"
        )

    def select_max_thinking(self, session: str) -> None:
        """把「思考深度」切到 Max。

        读的是 `name` 属性而不是 `li.selected`：属性在触发器上，弹层没展开时也读得到，
        不用为了确认当前档位先把弹层点开一次。

        找不到控件不算错：页面改版可能换类名或去掉这个开关，为它中断整个流程不值当，
        照常提问就是，日志里说一声。点了没切过来同理。
        """
        result = run_code(session, self.max_thinking_js())
        if not isinstance(result, dict):
            sys.exit(f"{self.LOG_PREFIX} 「思考深度」的检查结果无法解析：{result!r}")

        action = result.get("action")
        if action == "already":
            self.log(f"「思考深度」已经是 {self.THINKING_TARGET}")
        elif result.get("ok"):
            self.log(f"已把「思考深度」切到 {self.THINKING_TARGET}")
        elif action == "not-found":
            self.log("页面上没找到「思考深度」控件，跳过这一步（不影响提问）")
        elif action == "option-not-found":
            self.log(f"弹层里没有 {self.THINKING_TARGET} 这一档，跳过这一步（不影响提问）")
        else:
            self.log(
                f"「思考深度」点了但没切过来（当前 {result.get('name')!r}），继续往下走"
            )

    # ------------------------------------------------------------------ 提交

    def submit_js(self, text: str) -> str:
        """聚焦 → 填入 → 回车，全部塞进同一次 run-code。

        为什么不能拆成 fill / click / press 三条独立命令（实测踩过）：每条命令是独立
        进程，命令之间的空档正好够页面完成一次重渲染，刚拿到的焦点会被冲掉，Enter
        落空。症状是「命令条条成功、页面纹丝不动」，prompt 还留在输入框里没发出去。
        塞进同一个 Playwright 上下文连续执行，焦点才保得住。

        **回车即发送**：GLM 没有常驻的发送按钮（填了字才冒出一个 .submit-btn 图标），
        所以这里按 Enter，不点按钮——按钮的出现时机不定，等它反而更容易踩空。

        输入框按顺序试、取最后一个可见的：聊天页的输入框在所有匹配里排最后，用 .last()
        而不是 .first() 是为了躲开页面上那些隐藏的、别的用途的同名元素。
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
        """GLM 多一种失败：三个输入框选择器一个都没命中。"""
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

        要求两次而不是一次，是因为流式输出中途常有几秒停顿，停一次就取会截在半截。
        长度为 0 不算「稳定」：Max 模式先跑思考、正文容器可能已经挂上但一个字没写，
        连着读到几次 0 就认作收尾的话，会取回一个空回答。
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

    def cleanup_skip_reason(
        self, session: str, current_id: str | None, baseline: Any
    ) -> str | None:
        """GLM 没有可删的会话记录，这一步固定跳过。

        deepseek 那套「删掉左侧列表里本次新建的会话」在这儿无从谈起：体验中心侧栏是
        导航菜单、不是会话列表，URL 里也不带会话 ID，对话本身不落库——刷新页面
        .chat-item 就归零。没有记录会留在用户账号里，也就没有要清理的东西。

        固定返回原因而不是返回 None：基类拿到 None 会去调 delete_conversation_js，
        而 GLM 没有那套 DOM 操作可写（写出来也只是空转）。
        """
        return "智谱体验中心的对话不落库（刷新即清空），没有需要删除的记录，跳过"

    # --------------------------------------------------------- HTML → Markdown

    def convert_html(self, html: str) -> str:
        """把一段正文 HTML 还原成 Markdown——转交本文件的 convert()（见上面那段）。"""
        return convert(html)


if __name__ == "__main__":
    GLMChat().main()
