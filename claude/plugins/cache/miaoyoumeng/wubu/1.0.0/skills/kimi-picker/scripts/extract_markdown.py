#!/usr/bin/env python3
"""
Kimi 回答区 HTML → Markdown 还原

为什么需要这个脚本：
Kimi 网页把回答渲染成 HTML，页面上直接读文本拿到的是排版后的结果——
`**加粗**` 的星号、代码块的三反引号围栏在渲染时就被吃掉了。
直接拿渲染文本展示，会和「回答原样保留 Markdown」的要求冲突。
本脚本沿 DOM 反向推回 Markdown 语法，把格式还回来。

为什么要顺着 chat-content-item-assistant 分组：
Kimi 在同一轮回答里会挂多个 markdown 容器（正文、工具调用产物各占一个），
外层还额外挂一份「思考过程」。按下标输出时必须是「一轮 = 一个元素」，
所以先按轮次容器分组，组内再拼接，组间不混。

为什么取 HTML 这一步要委托 playwright-cli：
浏览器由 playwright-cli 以 --remote-debugging-pipe 方式托管，没有开放 TCP 调试端口，
外部进程（含 Playwright 的 Python 绑定）连不进去，DOM 只能由它取。
取回来之后的 HTML → Markdown 转换，全部在本脚本里完成。

用法（在插件根目录执行，也就是 pyproject.toml 所在的那一层）：
    uv run python skills/kimi-picker/scripts/extract_markdown.py
    uv run python skills/kimi-picker/scripts/extract_markdown.py --session chat.kimi

输出：JSON 数组，按对话顺序每轮回答一个元素；页面上还没有回答时是 []。
多轮追问场景下，数组下标即轮次（第 1 轮 = 下标 0）。
某轮还在生成、尚未产出正文时，该位置是空字符串，下标不会错位。

已知限制（页面本身的限制，不是脚本缺陷）：
Kimi 只渲染 KaTeX 的 HTML 版，既没有 MathML 孪生结构，也没有 LaTeX 原文。
公式只能取到渲染后的字符序列，上标、分式、根号的结构会丢失——
`$E=mc^2$` 会退化成 `$E=mc2$`。含公式的回答请按近似文本使用。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# 一轮对话的容器。用户提问是 .chat-content-item-user，两者不会互相命中。
ROUND_SELECTOR = ".chat-content-item-assistant"

# 轮次容器内的正文容器。必须排除 .toolcall-content-text：
# 思考过程同样是 .markdown-container，只是多带这个类，不排除会把它当回答捞出来。
# 2026-10-10 实测：正文不带 .toolcall-content-text；生成中的正文额外带 .toolcall-text-in，
# 该分支不影响取值，因为 :not() 只看 toolcall-content-text。
BODY_SELECTOR = ".markdown-container:not(.toolcall-content-text)"

FETCH_JS = (
    "(() => {"
    f"  const rounds = document.querySelectorAll({json.dumps(ROUND_SELECTOR)});"
    "   return [...rounds].map(r =>"
    f"     [...r.querySelectorAll({json.dumps(BODY_SELECTOR)})].map(e => e.outerHTML)"
    "   );"
    "})()"
)

# 语言标签只认这种长相的短标识，免得把「复制」「运行」这类按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")


def fetch_html(session: str) -> list[list[str]]:
    """让 playwright-cli 把每轮正文的 HTML 取回来，按轮次分组。"""
    try:
        proc = subprocess.run(
            ["playwright-cli", "-s", session, "--raw", "eval", FETCH_JS],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        sys.exit("找不到 playwright-cli 命令，请先确认它已安装且在 PATH 中。")

    if proc.returncode != 0:
        sys.exit(f"playwright-cli 执行失败：{(proc.stderr or proc.stdout).strip()}")

    try:
        rounds = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit(f"playwright-cli 返回的不是合法 JSON：\n{proc.stdout[:300]}")

    if not isinstance(rounds, list):
        sys.exit(f"playwright-cli 返回的结构不是数组：{str(rounds)[:300]}")
    return rounds


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


def _text(node) -> str:
    """文本节点取值，顺手把不换行空格拉回普通空格，输出更干净。"""
    return str(node).replace("\xa0", " ")


def walk(node) -> str:
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
            [cell(td) for td in tr.children if isinstance(td, Tag)]
            for tr in node.find_all("tr")
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


def convert_round(blocks: list[str]) -> str:
    """一轮里的多个正文容器按顺序拼接。"""
    parts = [b for b in (convert(html) for html in blocks) if b]
    return "\n\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="把 Kimi 网页上的回答还原成 Markdown"
    )
    parser.add_argument(
        "--session",
        default="chat.kimi",
        help="playwright-cli 的会话名（默认 chat.kimi）",
    )
    args = parser.parse_args()

    rounds = [convert_round(blocks) for blocks in fetch_html(args.session)]
    print(json.dumps(rounds, ensure_ascii=False))


if __name__ == "__main__":
    main()
