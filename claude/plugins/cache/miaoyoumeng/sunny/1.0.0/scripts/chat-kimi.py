#!/usr/bin/env python3
"""
chat-kimi.py — 用 playwright-cli 驱动 Kimi 网页版，批量提交 prompt 并取回 Markdown 回答

用法（在插件根目录执行，即 pyproject.toml 所在那一层）：

    # 提交两个 prompt，回答分别写进 out/1.md、out/2.md
    uv run python scripts/chat-kimi.py \
        --prompt="问题一" --prompt="问题二" --dir=out

    # 也可以只给一个文件：本次所有回答全写进它，第 1 个覆盖写、之后追加写
    uv run python scripts/chat-kimi.py \
        --prompt="问题一" --prompt="问题二" --file=out/汇总.md

    # 结果以 JSON 输出到 stdout，便于上层程序解析
    uv run python scripts/chat-kimi.py --prompt="问题" --dir=out --json

输出：进度日志走 stderr，最终结果走 stdout——重定向时能拿到干净的结果。
落盘位置 --dir 与 --file 二选一：--dir 给目录，每个 prompt 的回答写进目录下以序号
命名的 Markdown 文件（1.md、2.md …）；--file 给文件，本次所有回答都写进这一个文件
（第 1 个覆盖写、之后逐个追加）。顺序就是 prompt 的提交顺序。

流程（按顺序）：

1. 三步验证，每步各打一行日志（①②③），全过才开浏览器：
   ① 验证参数（--prompt 必填；--dir 与 --file 二选一，缺一个或都给都报错退出）→
   ② 验证输出位置（--dir 须已存在；--file 的父目录须已存在）→ ③ 验证登录状态。
   登录校验交给 platform-logined-validator.py --platform=kimi：未登录由它把
   窗口交给用户登，登不上（或超时）本脚本直接终止。
2. 打开（或复用）浏览器 → **窗口最小化** → 等页面就绪 → 逐个提交 prompt、等收尾、
   取回 Markdown。确认登录之后浏览器就不再占前台，全流程在后台跑；要看页面加 --show。
3. 每个回答写进 --dir/1.md、--dir/2.md …（或按 --file 追加进同一个文件），
   序号从 1 开始，就是 prompt 的提交顺序。
4. 删掉左侧列表里「本次交互」那条会话记录，再关闭浏览器。只删脚本自己新建的
   （提交前就存在的会话不动，免得误删历史）；想留着记录加 --keep-conversation。

**流程骨架在 `chat_base.py`**（模板方法模式）：三步验证、开浏览器、等页面就绪、
提交、等收尾、落盘、删会话、关浏览器都是那边写好的，本文件只写 Kimi 的差异——
选择器、页面探测、提交方式、收尾判据、删会话的 DOM 操作，以及页面特有的
HTML → Markdown 转换。要改公共流程请去改 chat_base.py，改一处五个平台都生效。

与 kimi-picker 技能（sunny 插件）流程的差异，四处：

1. **一次会话提交多个 prompt**——按「提交 → 等本轮收尾 → 取本轮回答」串行推进，
   每个 prompt 对应一条响应，下标严格对齐。串行是必须的：并行提交会让两轮回答
   在页面上交叉，谁也认不出哪条回答属于哪个问题。
2. **登录交给 platform-logined-validator.py**——本脚本不自己判断登录、也不等
   用户登录，只认那个脚本的结论；它说没登上，这里立刻终止，后面都不开始。
3. **结果落盘**——每个回答写进 --dir 下一个以序号命名的 .md 文件（或按 --file
   追加进同一个文件），拿文件走人即可，不必解析 stdout。
4. **收尾多一步删会话**——技能里没这一步，见 chat_base.py 的 cleanup_conversation()。

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


# ------------------------------------------------------- HTML → Markdown
# 这一段内联自 kimi-picker 技能的 scripts/extract_markdown.py（2026-10-10 实测版本）。
#
# 为什么不用第三方 Markdown 转换库：Kimi 页面有它特有的结构——代码块头部的
# 「复制」按钮与语言标签、KaTeX 的公式渲染树。通用库不认这些，会把界面文字
# 混进正文、把公式读成乱码。所以沿 DOM 反向推回 Markdown 语法。
#
# Kimi 的两个特点决定了 walk 的写法：
#
# 1. 段落由 div.paragraph 承载，其余 div 全是布局容器——只认这个类名，别的 div
#    一律穿透，免得每层都塞一对空行。
# 2. 公式只有 KaTeX 的 HTML 渲染版，没有 LaTeX 原文（详见 _tex 的说明）。

# 语言标签只认这种长相的短标识，免得把「复制」「运行」这类按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")


def _has_class(node: Tag, name: str) -> bool:
    return name in (node.get("class") or [])


def _tex(node: Tag) -> str:
    """取公式文本。

    有 MathML annotation 就用它，那是 LaTeX 原文，能原样还原。
    没有就退回渲染后的字符序列——Kimi 目前走的是这条路，
    拿回来的文本会丢上标与分式结构，属于已知限制。
    """
    ann = node.find("annotation", attrs={"encoding": "application/x-tex"})
    if ann:
        return ann.get_text().strip()
    return node.get_text().strip()


def _code_lang(node: Tag) -> str:
    """从 <pre class="language-python"> 里取语言，比界面上那个标签可靠。"""
    for c in node.get("class") or []:
        if c.startswith("language-") and LANG_RE.fullmatch(c[9:]):
            return c[9:]
    return ""


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

    # 公式必须在遍历子节点之前截断：KaTeX 的 HTML 里全是排版用的嵌套 span，
    # 继续下探只会把字符拆得七零八落。
    if _has_class(node, "katex"):
        text = _tex(node)
        if not text:
            return ""
        return f"\n\n$$\n{text}\n$$\n\n" if _has_class(node, "katex-display") else f"${text}$"

    # 代码块容器。整个容器里的界面文字（语言标签、「复制」按钮）都不属于代码，
    # 不整块拦下来会混进正文。语言改从 <pre> 的 class 取。
    if _has_class(node, "segment-code"):
        pre = node.find("pre")
        code = (pre if pre is not None else node).get_text().rstrip("\n")
        lang = _code_lang(pre) if pre is not None else ""
        return f"\n\n```{lang}\n{code}\n```\n\n"

    if tag in ("script", "style", "button", "svg", "noscript"):
        return ""

    if tag == "br":
        return "  \n"  # 行尾两个空格 = Markdown 硬换行

    if tag == "hr":
        return "\n\n---\n\n"

    # Kimi 用 div.paragraph 承载段落。只认这个类名，
    # 其余 div 一律当布局容器穿透，免得每层都塞一对空行。
    if _has_class(node, "paragraph"):
        inner = kids().strip()
        return f"\n\n{inner}\n\n" if inner else ""

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
        # 块级代码由上层 .segment-code / pre 接走，走到这里只可能是行内代码
        return "`" + node.get_text() + "`"

    if tag == "pre":
        # 兜底：正常路径已被 .segment-code 分支接走，走到这里说明页面结构变了。
        code = node.get_text().rstrip("\n")
        return f"\n\n```{_code_lang(node)}\n{code}\n```\n\n"

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
    # 整行只有空白的，先压成空行：Kimi 会在段落之间插只含 <br> 的占位节点，
    # 留着会在正文里多出一行孤立的空白
    text = re.sub(r"\n[ \t]+\n", "\n\n", text)
    # 再压掉多余空行。代码块内部的连续空行也会被一起压掉——Markdown 里
    # 块内空行不承载语义，这个代价换实现更简单，划算。
    return re.sub(r"\n{3,}", "\n\n", text).strip()


# ----------------------------------------------------------------- 脚本


class KimiChat(chat_base.ChatScript):
    """Kimi 网页版的批量提问脚本。流程见 chat_base.ChatScript.main()。

    本文件只负责 Kimi 的差异：选择器、探测 JS、提交方式、收尾判据、删会话，
    以及上面那段 HTML → Markdown。
    """

    PLATFORM = config.KIMI
    LOG_PREFIX = "[kimi]"
    DESCRIPTION = "用 playwright-cli 驱动 Kimi 网页版，批量提交 prompt 并取回 Markdown 回答"
    URL_LABEL = "Kimi 地址"
    LOGIN_FAILED_TEMPLATE = (
        "{prefix} Kimi 未登录（登录校验退出码 {code}），流程终止。\n"
        "  请在浏览器窗口里登好 Kimi 再重跑本脚本；登录由你本人完成，脚本不代登。"
    )

    # 输入框：Lexical 富文本。用选择器定位，不受 ref 失效影响（技能里用的是 snapshot + ref，
    # 那套要求每条命令前重新 snapshot，脚本里没法照搬）
    INPUT_SELECTOR = "[data-lexical-editor]"

    # 轮次容器 / 正文容器 / 收尾标志（kimi-picker 2026-10-10 实测，2026-10-12 复核）
    #
    # 正文选择器里的 :not(.toolcall-content-text) 不能省：同一轮里思考过程也是
    # .markdown-container，只是多带这个类，不排除会把「用户问…我需要…」的内心独白
    # 当成回答捞出来。
    ROUND_SELECTOR = ".chat-content-item-assistant"
    BODY_SELECTOR = ".markdown-container:not(.toolcall-content-text)"
    ACTION_SELECTOR = ".segment-assistant-actions"

    # 正文容器带上这个类 = 这一轮还在流式输出。实测：生成中正文带 .toolcall-text-in
    # 且本轮操作条还没出现；两者同时翻转才算收尾，单看一个都会误判。
    STREAMING_CLASS = "toolcall-text-in"

    # 会话页 URL 形如 /chat/<uuid>，收尾时按这个 ID 去左侧列表认本次那条会话。
    # Kimi 的会话 ID 是标准 UUID（8-4-4-4-12），照这个形状匹配正好把 /chat/history
    # 这类固定页面挡在外面——它不是 UUID，匹配不上。
    CONVERSATION_URL_RE = re.compile(
        r"/chat/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
    )

    # ------------------------------------------------------------ 页面探测

    def page_state_js(self) -> str:
        """一次取回四件事：有没有「登录」按钮、侧栏用户菜单在不在、输入框在不在、
        页面上已有几轮回答。

        登录判据看两个元素：`.login-button` 存在即未登录，侧栏用户菜单存在即已登录。
        两个都读回来而不是只读一个——复核时能分得清「未登录」和「页面还没渲染出来」。
        """
        return (
            "(() => {"
            "  const login = document.querySelectorAll('.login-button').length;"
            "  const user = document.querySelectorAll('[data-testid=sidebar-user-menu-trigger]').length;"
            f"  const input = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            f"  const rounds = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)}).length;"
            "  return JSON.stringify({login_buttons: login, user_menu: user,"
            "    input_ready: !!input, rounds: rounds});"
            "})()"
        )

    def looks_logged_out(self, state: dict[str, Any]) -> bool:
        """登录按钮出现且用户菜单不在，才算登录态丢了。

        Kimi 首屏会先吐一份未登录形态的 HTML，前端接管后才换成登录态的界面，
        所以判据必须带上「输入框已经就绪」——页面正在加载时读到的东西不作数。
        两个元素一起看：只有登录按钮、没有用户菜单才是真未登录；
        单看登录按钮的话，两者同时存在的中间态会误报。
        """
        return (
            bool(state.get("input_ready"))
            and int(state.get("login_buttons", 0) or 0) > 0
            and not int(state.get("user_menu", 0) or 0)
        )

    def probe_js(self, index: int) -> str:
        """读第 index 轮（0 起）的收尾状态。

        为什么盯住第 index 个容器而不是「最后一条」：多轮连续提交时，回车后新容器
        还没出现，页面上的最后一条仍是上一轮的已完成状态，看最后一条会把「还没开始」
        误判成「已收尾」。钉死下标才准。

        判据取两个、都钉在本轮上（见 STREAMING_CLASS 处的说明）：
        正文还在流式 → 没完；本轮操作条没出现 → 没完。都过去了才认收尾。
        """
        return (
            "(() => {"
            f"  const msgs = [...document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)})];"
            f"  if (msgs.length <= {index}) return 'wait:no-message';"
            f"  const round = msgs[{index}];"
            f"  const boxes = [...round.querySelectorAll({json.dumps(self.BODY_SELECTOR)})];"
            f"  if (boxes.some(b => b.classList.contains({json.dumps(self.STREAMING_CLASS)})))"
            "    return 'wait:streaming';"
            f"  if (!round.querySelector({json.dumps(self.ACTION_SELECTOR)})) return 'wait:actions';"
            "  if (!boxes.length) return 'wait:no-body';"
            "  return 'done';"
            "})()"
        )

    # ---------------------------------------------------------------- 提交

    def submit_js(self, text: str) -> str:
        """聚焦 → 填入 → 回车，全部塞进同一次 run-code。

        为什么不能拆成 fill / press 两条独立命令（豆包脚本实测踩过，同款架构同款坑）：
        每条命令是独立进程，命令之间的空档正好够页面完成一次重渲染，刚拿到的焦点
        会被冲掉，Enter 落空。症状是「命令条条成功、页面纹丝不动」，prompt 还留在
        输入框里没发出去。塞进同一个 Playwright 上下文连续执行，焦点才保得住。

        不先 click 输入框：fill 自己会聚焦，少一步就少一个失败点（Kimi 输入框在
        页面中央，实测 fill 直接可用）。
        """
        return (
            "async page => {"
            f"  const box = page.locator({json.dumps(self.INPUT_SELECTOR)});"
            f"  await box.fill({json.dumps(text, ensure_ascii=False)});"
            "  const filled = await box.innerText();"
            "  if (!filled.trim()) return JSON.stringify({ok: false, stage: 'fill'});"
            "  await page.keyboard.press('Enter');"
            "  await page.waitForTimeout(1500);"
            "  const left = await box.innerText();"
            "  return JSON.stringify({ok: !left.trim(), stage: 'submit', left: left});"
            "}"
        )

    # ------------------------------------------------------------ 会话清理

    def delete_conversation_js(self, conversation_id: str) -> str:
        """删掉左侧列表里指定会话：更多按钮 → 菜单点「删除」→ 确认框点「删除」。

        为什么全程用 page.evaluate 里的 JS click，而不是 Playwright 的 locator.click
        （2026-10-12 实测踩过）：Kimi 侧栏可以折叠，折叠时条目被推到视口左侧外面
        （实测条目 rect.x = -232），locator.click / hover 会一路重试到 30 秒超时，
        报 "element is outside of the viewport"。JS 的 el.click() 不看视口，稳。

        每一步都先验证入口存在再点，并把卡住的步骤名带回去——菜单、确认框都是点完
        才渲染的，得等它们出现；哪一步没等到，日志里说得出是哪一步。
        """
        link_sel = json.dumps(f'a[href*="/chat/{conversation_id}"]')
        return (
            "async page => await page.evaluate(async () => {"
            f"  const link = document.querySelector({link_sel});"
            "  if (!link) return JSON.stringify({ok: false, stage: 'locate'});"
            "  const item = link.closest('.next-sidebar-history-item') || link.parentElement;"
            "  const more = item.querySelector('.next-sidebar-history-item__more');"
            "  if (!more) return JSON.stringify({ok: false, stage: 'more-button'});"
            "  more.click();"
            "  await new Promise(r => setTimeout(r, 900));"
            "  const del = [...document.querySelectorAll('[role=menuitem]')]"
            "    .find(i => (i.textContent || '').trim() === '删除');"
            "  if (!del) return JSON.stringify({ok: false, stage: 'menu'});"
            "  del.click();"
            "  await new Promise(r => setTimeout(r, 1000));"
            "  const confirm = document.querySelector('[data-testid=confirm-dialog-confirm]');"
            "  if (!confirm) return JSON.stringify({ok: false, stage: 'confirm'});"
            "  confirm.click();"
            # 侧栏列表更新是异步的：实测点完确认要 2~4 秒那条才从列表里消失。
            # 固定等一拍再查会读早了，把「已经删掉」报成「没删掉」（端到端实测踩过），
            # 所以轮询到它消失为止，最多等 10 秒。
            "  let remains = 1;"
            "  for (let i = 0; i < 20; i++) {"
            "    await new Promise(r => setTimeout(r, 500));"
            f"    remains = document.querySelectorAll({link_sel}).length;"
            "    if (remains === 0) break;"
            "  }"
            "  return JSON.stringify({ok: remains === 0, stage: 'verify', remains});"
            "})"
        )

    # ------------------------------------------------------- HTML → Markdown

    def convert_html(self, html: str) -> str:
        """把一段正文 HTML 还原成 Markdown——转交本文件的 convert()（见上面那段）。"""
        return convert(html)


if __name__ == "__main__":
    KimiChat().main()
