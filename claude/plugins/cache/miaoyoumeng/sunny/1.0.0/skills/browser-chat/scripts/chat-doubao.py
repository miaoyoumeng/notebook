#!/usr/bin/env python3
"""
chat-doubao.py — 用 playwright-cli 驱动豆包网页版，批量提交 prompt 并取回 Markdown 回答

用法（在插件根目录执行，即 pyproject.toml 所在那一层）：

    # 提交两个 prompt，回答分别写进 out/1.md、out/2.md
    uv run python scripts/chat-doubao.py \
        --prompt="问题一" --prompt="问题二" --dir=out

    # 也可以只给一个文件：本次所有回答全写进它，第 1 个覆盖写、之后追加写
    uv run python scripts/chat-doubao.py \
        --prompt="问题一" --prompt="问题二" --file=out/汇总.md

    # 结果以 JSON 输出到 stdout，便于上层程序解析
    uv run python scripts/chat-doubao.py --prompt="问题" --dir=out --json

输出：进度日志走 stderr，最终结果走 stdout——重定向时能拿到干净的结果。
落盘位置 --dir 与 --file 二选一：--dir 给目录，每个 prompt 的回答写进目录下以序号
命名的 Markdown 文件（1.md、2.md …）；--file 给文件，本次所有回答都写进这一个文件
（第 1 个覆盖写、之后逐个追加）。顺序就是 prompt 的提交顺序。

流程（按顺序）：

1. 三步验证，每步各打一行日志（①②③），全过才开浏览器：
   ① 验证参数（--prompt 必填；--dir 与 --file 二选一，缺一个或都给都报错退出）→
   ② 验证输出位置（--dir 须已存在；--file 的父目录须已存在）→ ③ 验证登录状态。
   登录校验交给 platform-logined-validator.py --platform=doubao：未登录由它把
   窗口交给用户登，登不上（或超时）本脚本直接终止。
2. 打开（或复用）浏览器 → **窗口最小化** → 等页面就绪 → 逐个提交 prompt、等收尾、
   取回 Markdown。确认登录之后浏览器就不再占前台，全流程在后台跑；要看页面加 --show。
3. 每个回答写进 --dir/1.md、--dir/2.md …（或按 --file 追加进同一个文件），
   序号从 1 开始，就是 prompt 的提交顺序。
4. 删掉左侧列表里「本次交互」那条会话记录，再关闭浏览器。只删脚本自己新建的
   （提交前就存在的会话不动，免得误删历史）；想留着记录加 --keep-conversation。

**流程骨架在 `chat_base.py`**（模板方法模式）：三步验证、开浏览器、等页面就绪、
提交、等收尾、落盘、删会话、关浏览器都是那边写好的，本文件只写豆包的差异——
选择器、页面探测、提交方式、收尾判据、删会话的 DOM 操作、挡路弹窗的清理，
以及页面特有的 HTML → Markdown 转换。要改公共流程请去改 chat_base.py，
改一处所有平台都生效。

与 doubao-picker 技能（sunny 插件）流程的差异，三处：

1. **一次会话提交多个 prompt**——按「提交 → 等本轮收尾 → 取本轮回答」串行推进，
   每个 prompt 对应一条响应，下标严格对齐。串行是必须的：并行提交会让两轮回答
   在页面上交叉，谁也认不出哪条回答属于哪个问题。
2. **登录交给 platform-logined-validator.py**——本脚本不自己判断登录、也不等
   用户登录，只认那个脚本的结论；它说没登上，这里立刻终止，后面都不开始。
3. **结果落盘**——每个回答写进 --dir 下一个以序号命名的 .md 文件（或按 --file
   追加进同一个文件），拿文件走人即可，不必解析 stdout。

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


# ------------------------------------------------------- HTML → Markdown
# 这一段内联自 doubao-picker 的 scripts/extract_markdown.py（实测踩坑版本）。
#
# 为什么不用第三方 Markdown 转换库：豆包页面有它特有的界面噪音——代码块头部的
# 「python / 运行 / 复制 / 预览」、表格工具栏的「表格」二字加按钮、公式的 MathML
# 孪生结构。通用库不认这些 data-* 标记，会把界面文字混进正文、把公式读成乱码。
# 所以沿 DOM 反向推回 Markdown 语法。

# 语言标签只认这种长相的短标识，免得把按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")


def _class_contains(node: Tag, fragment: str) -> bool:
    # 注意这里是**子串**匹配，与别家的 _has_class（整串相等）不是一回事：
    # 豆包的表格工具栏容器类名带后缀（table-header-xxx），整串比不出来。
    return any(fragment in c for c in (node.get("class") or []))


def _tex(raw: str) -> str:
    """把豆包 copy-text 里的 LaTeX 还原成 Markdown 数学定界符。

    豆包把公式原文存在 copy-text 属性里，行内形如 \\(E = mc^2\\)。
    转成 $...$ / $$...$$ 是 Markdown 的通行写法，渲染器都认。
    """
    raw = raw.strip()
    if raw.startswith("\\(") and raw.endswith("\\)"):
        return f"${raw[2:-2]}$"
    if raw.startswith("\\[") and raw.endswith("\\]"):
        return f"\n\n$$\n{raw[2:-2]}\n$$\n\n"
    return raw


def _code_lang(node: Tag) -> str:
    """语言取自 <pre> 的 class（language-python）。

    代码块头部的语言标签是界面文字，整块已被丢弃；class 更可靠。
    """
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

    # 界面元素整块丢弃，否则这些文字会混进正文：
    # 代码块头部的语言标签与「运行 / 复制 / 预览」按钮带 data-copy-ignore="true"；
    # 表格工具栏（「表格」二字加按钮）在 table-header-* 容器里。
    if node.get("data-copy-ignore") == "true":
        return ""
    if _class_contains(node, "table-header"):
        return ""

    # 公式必须在遍历子节点之前截断：copy-text 之外还挂着一堆渲染用的
    # span（MathML 与可视化孪生结构），继续下探只会得到重复且错乱的文本。
    raw_tex = node.get("copy-text")
    if raw_tex:
        return _tex(raw_tex)

    if tag in ("script", "style", "button", "svg", "noscript"):
        return ""

    if tag == "br":
        return "  \n"  # 行尾两个空格 = Markdown 硬换行

    if tag == "hr":
        return "\n\n---\n\n"

    # 豆包用 div 承载段落（没有 p 标签），每个 div 按块级处理；
    # 嵌套多包一层只会多出空行，收尾时统一压缩掉。
    if tag == "div":
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
        # 块级代码由上层 pre 接走，走到这里只可能是行内代码
        return "`" + node.get_text() + "`"

    if tag == "pre":
        code = node.get_text().rstrip("\n")
        lang = _code_lang(node)
        return f"\n\n```{lang}\n{code}\n```\n\n"

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


class DoubaoChat(chat_base.ChatScript):
    """豆包网页版的批量提问脚本。流程见 chat_base.ChatScript.main()。

    本文件只负责豆包的差异：选择器、探测 JS、提交方式、收尾判据、删会话，
    挡路的推广弹窗，以及上面那段 HTML → Markdown。
    """

    PLATFORM = config.DOUBAO
    LOG_PREFIX = "[doubao]"
    DESCRIPTION = "用 playwright-cli 驱动豆包网页版，批量提交 prompt 并取回 Markdown 回答"
    URL_LABEL = "豆包地址"
    LOGIN_FAILED_TEMPLATE = (
        "{prefix} 豆包未登录（登录校验退出码 {code}），流程终止。\n"
        "  请在浏览器窗口里登好豆包再重跑本脚本；登录由你本人完成，脚本不代登。"
    )

    # 输入框：ProseMirror 富文本，全页恰好 1 个；用选择器定位，不受 ref 失效影响
    INPUT_SELECTOR = "[contenteditable='true']"

    # 读输入框时另用一个更精确的选择器（提交时仍用上面那个）。
    # 两个选择器并存是原有实现，别顺手统一——实测中它们各自的命中情况并不相同。
    INPUT_JS_SELECTOR = ".ProseMirror"

    # 轮次容器 / 正文容器（doubao-picker 2026-10 实测选择器）
    ROUND_SELECTOR = '[data-message-role="assistant"]'
    BODY_SELECTOR = ".md-box-root"

    # 会话页 URL 形如 /chat/<纯数字ID>，收尾时按这个 ID 去左侧列表认本次那条会话。
    # 只认纯数字：/chat/skills、/chat/cron-jobs 这些固定页面不是会话
    CONVERSATION_URL_RE = re.compile(r"/chat/(\d{6,})")

    # 挡路的模态弹窗。豆包访问 /chat 时会弹「下载电脑版」的推广弹窗，它拦截指针事件：
    # 输入框在弹窗底下看得见、点不着，click 会一路重试到 30 秒超时（实测报错原文是
    # "subtree intercepts pointer events"）。而 fill 不受影响——它不要求元素能接收
    # 指针事件，所以症状是「文字填得进去、回车发不出去」，很有迷惑性。
    # 关闭按钮用 JS 直接 .click()：不走指针事件，绕开遮罩拦截。
    DISMISS_DIALOGS_JS = (
        "(() => {"
        "  const dialogs = [...document.querySelectorAll('[role=dialog][data-state=open]')];"
        "  let closed = 0;"
        "  for (const d of dialogs) {"
        "    const btns = [...d.querySelectorAll('button')];"
        "    const pick = btns.find(b => (b.innerText || '').trim() === '下次提醒我')"
        "      || btns.find(b => (b.innerText || '').trim() === '关闭')"
        "      || btns.find(b => (b.getAttribute('aria-label') || '').trim() === '关闭');"
        "    if (pick) { pick.click(); closed += 1; }"
        "  }"
        "  return JSON.stringify({dialogs: dialogs.length, closed: closed});"
        "})()"
    )

    # ---------------------------------------------------------- 平台特有槽位

    def dismiss_dialogs(self, session: str) -> None:
        """关掉挡路的模态弹窗；没有弹窗时静默通过。

        优先点「下次提醒我」而不是「关闭」：前者会让豆包记下来，少弹几次。
        """
        result = eval_js(session, self.DISMISS_DIALOGS_JS)
        if isinstance(result, dict) and result.get("closed"):
            self.log(f"关掉了 {result['closed']} 个挡路的弹窗")

    def prepare_page(self, session: str, baseline: int) -> int:
        """槽位 1 · 页面就绪之后先清一次挡路的推广弹窗。

        轮数基线不受影响，原样返回。弹窗也可能在页面加载完之后才弹出来，
        所以提交前还会再清一次，见 submit_js()。
        """
        self.dismiss_dialogs(session)
        return baseline

    # -------------------------------------------------------------- 页面探测

    def page_state_js(self) -> str:
        """一次取回三件事：有没有「登录」按钮、输入框在不在、页面上已有几轮回答。

        登录判据只看「登录」按钮的有无：豆包未登录时输入框照样渲染，
        占位文案也和登录后一样，拿输入框当判据会误判（实测未登录恰好 1 个按钮，
        登录后 0 个）。
        """
        return (
            "(() => {"
            "  const btns = [...document.querySelectorAll('button')];"
            "  const loginCount = btns.filter(b => (b.textContent || '').trim() === '登录').length;"
            f"  const input = document.querySelector({json.dumps(self.INPUT_SELECTOR)});"
            f"  const rounds = document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)}).length;"
            "  return JSON.stringify({login_button: loginCount, input_ready: !!input,"
            " rounds: rounds});"
            "})()"
        )

    def looks_logged_out(self, state: dict[str, Any]) -> bool:
        """页面上挂着「登录」按钮，就算登录态丢了。

        带上 input_ready 沿用原来的位置：页面正在加载时读到的东西不作数，
        这时候有没有按钮都说明不了问题。
        """
        return bool(state.get("input_ready")) and int(state.get("login_button", 0) or 0) > 0

    def logout_recheck_seconds(self) -> float:
        """豆包实测复核间隔 1.0 秒（其余平台是 1.5，别顺手统一）。"""
        return 1.0

    def read_box_js(self) -> str:
        """读回输入框现有文本（fill 不回显填入的内容，要校验只能读回来）。

        用的是 .ProseMirror（INPUT_JS_SELECTOR），与提交时的 INPUT_SELECTOR
        不是同一个选择器——沿用原有实现。
        """
        return (
            "(() => {"
            f"  const ce = document.querySelector({json.dumps(self.INPUT_JS_SELECTOR)});"
            "  return JSON.stringify({text: ce ? ce.innerText : null});"
            "})()"
        )

    def probe_js(self, index: int) -> str:
        """读第 index 轮（0 起）的收尾状态。

        为什么盯住第 index 个容器而不是「最后一条」：多轮连续提交时，回车后新容器
        还没出现，页面上的最后一条仍是上一轮的已完成状态，看最后一条会把「还没开始」
        误判成「已收尾」。钉死下标才准。
        """
        return (
            "(() => {"
            f"  const msgs = [...document.querySelectorAll({json.dumps(self.ROUND_SELECTOR)})];"
            f"  if (msgs.length <= {index}) return 'wait:no-message';"
            f"  const round = msgs[{index}];"
            "  const el = round.querySelector('[data-testid=preamble-elapsed]');"
            "  if (el) return el.getAttribute('data-message-content-collapsed') === 'true'"
            "    ? 'done' : 'wait:running';"
            f"  const boxes = [...round.querySelectorAll({json.dumps(self.BODY_SELECTOR)})];"
            "  if (!boxes.length) return 'wait:no-container';"
            "  return boxes.some(b => b.dataset.streaming === 'true') ? 'wait:streaming'"
            " : 'suspect';"
            "})()"
        )

    def is_round_done(self, status: str, memory: dict[str, Any], index: int) -> bool:
        """收尾判据：主判据是开场白计时器，退到 streaming 标记时结论可疑，要连读 2 次。

        为什么这样（doubao-picker 实测踩过的坑，改前先想清楚）：

        - **主判据是开场白计时器的折叠属性，不是 data-streaming**。豆包的节奏是
          「开场白 → 执行工具 → 写正文」，工具执行期间正文容器根本不存在，
          data-streaming 给不出「还在跑」的信号，单看它会取到半截回答。
        - **一轮可能挂多个 .md-box-root**（实测 4 个），所以只判断「有没有还在跑的」，
          不按容器数量数轮次。
        - **suspect 要复读一次才采信**：没有开场白计时器兜底时，等一个间隔再看一眼，
          两次一致才算数。
        """
        if status == "done":
            return True
        if status == "suspect":
            memory["suspect_streak"] = int(memory.get("suspect_streak", 0)) + 1
            return memory["suspect_streak"] >= 2
        memory["suspect_streak"] = 0
        return False

    # ------------------------------------------------------------------ 提交

    def submit_js(self, text: str) -> str:
        """聚焦 → 填入 → 回车，全部塞进同一次 run-code。

        为什么不能拆成 fill / click / press 三条独立命令（实测踩过）：每条命令是独立
        进程，命令之间的空档正好够页面完成一次重渲染，刚拿到的焦点会被冲掉，Enter
        落空。症状是「命令条条成功、页面纹丝不动」，prompt 还留在输入框里没发出去。
        塞进同一个 Playwright 上下文连续执行，焦点才保得住。
        """
        return (
            "async page => {"
            # 弹窗可能在页面加载完之后才弹出来，提交前再清一次，别让它挡住输入框
            f"  await page.evaluate({json.dumps(self.DISMISS_DIALOGS_JS)});"
            f"  const box = page.locator({json.dumps(self.INPUT_SELECTOR)});"
            "  await box.click();"
            f"  await box.fill({json.dumps(text, ensure_ascii=False)});"
            "  const filled = await box.innerText();"
            "  if (!filled.trim()) return JSON.stringify({ok: false, stage: 'fill'});"
            "  await page.keyboard.press('Enter');"
            "  await page.waitForTimeout(1500);"
            "  const left = await box.innerText();"
            "  return JSON.stringify({ok: !left.trim(), stage: 'submit', left: left});"
            "}"
        )

    # -------------------------------------------------------------- 会话清理

    def delete_conversation_js(self, conversation_id: str) -> str:
        """删掉左侧列表里指定会话：hover 出「⋯」→ 菜单点「删除」→ 确认条点「删除」。

        每一步都先验证入口存在再点，并把卡住的步骤名带回去——确认条要等菜单点完才
        渲染出来；哪一步没等到，日志里说得出是哪一步。豆包的确认框没有 dialog 语义，
        就是页面上一个居中容器，所以只能按按钮文本找。
        """
        item_sel = json.dumps(f'[data-conversation-id="{conversation_id}"]')
        actions_sel = json.dumps('[data-sidebar-item-actions="true"] button')
        menu_item_sel = json.dumps('[role="menuitem"]')
        return (
            "async page => {"
            f"  const item = page.locator({item_sel});"
            "  if (!(await item.count())) return JSON.stringify({ok: false, stage: 'locate'});"
            "  await item.hover();"
            "  await page.waitForTimeout(500);"
            f"  await item.locator({actions_sel}).last().click();"
            "  await page.waitForTimeout(900);"
            f"  const del = page.locator({menu_item_sel})"
            ".filter({ hasText: /^删除$/ }).first();"
            "  if (!(await del.count())) return JSON.stringify({ok: false, stage: 'menu'});"
            "  await del.click();"
            "  await page.waitForTimeout(1000);"
            "  const confirm = page.getByRole('button', { name: '删除', exact: true }).last();"
            "  if (!(await confirm.count())) return JSON.stringify({ok: false, stage: 'confirm'});"
            "  await confirm.click();"
            "  await page.waitForTimeout(2000);"
            f"  const remains = await page.locator({item_sel}).count();"
            "  return JSON.stringify({ok: remains === 0, stage: 'verify', remains});"
            "}"
        )

    # --------------------------------------------------------- HTML → Markdown

    def convert_html(self, html: str) -> str:
        """把一段正文 HTML 还原成 Markdown——转交本文件的 convert()（见上面那段）。"""
        return convert(html)


if __name__ == "__main__":
    DoubaoChat().main()
