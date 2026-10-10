#!/usr/bin/env python3
"""
元宝回答区 HTML → Markdown 还原

为什么需要这个脚本：
元宝网页把回答渲染成 HTML，页面上直接读文本拿到的是排版后的结果——
`**加粗**` 的星号、代码块的三反引号围栏、公式的 $ 定界符在渲染时就被吃掉了。
直接拿渲染文本展示，会和「回答原样保留 Markdown」的要求冲突。
本脚本沿 DOM 反向推回 Markdown 语法，把格式还回来。

为什么不能直接套用 deepseek-picker 的那一份：
两家页面的 DOM 结构不一样，2026-10 实测元宝上对不上的地方有两处——
  * 代码块。元宝是 pre.ybc-pre-component，语言名在横幅内的
    .hyc-common-markdown__code__langComponent__text；deepseek 脚本找的
    .md-code-block-banner 在元宝上不存在，于是走 pre 兜底分支，结果是围栏语言
    丢失，且横幅上的语言名被 get_text() 当成代码正文（输出成
    「pythondef bubble_sort」这样）。
  * 列表。元宝每个列表项前面挂了一个装饰圆点
    span.ybc-li-component_dot（内容就是字符 ∙），deepseek 脚本会把它当正文
    文本捞出来，输出成「- ∙**时间复杂度**」。
选择器与分支因此按元宝重写。

为什么取 HTML 这一步要委托 playwright-cli：
浏览器由 playwright-cli 以 --remote-debugging-pipe 方式托管，没有开放 TCP 调试端口，
外部进程（含 Playwright 的 Python 绑定）连不进去，DOM 只能由它取。
取回来之后的 HTML → Markdown 转换，全部在本脚本里完成。

用法（在插件根目录执行，也就是 pyproject.toml 所在的那一层）：
    uv run python skills/yuanbao-picker/scripts/extract_markdown.py
    uv run python skills/yuanbao-picker/scripts/extract_markdown.py --session yuanbao

输出：JSON 数组，按对话顺序每轮回答一个元素；页面上还没有回答时是 []。
多轮追问场景下，数组下标即轮次（第 1 轮 = 下标 0）。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# 回答容器。必须用直接子级选择器 >：
# .hyc-content-md 这个类名在思考过程容器内部也有一份，用后代选择器会把整段
# 思考过程一起捞出来。2026-10 实测：全部匹配 2 个，直接子级只有 1 个是正文。
CONTAINER_SELECTORS = [
    ".hyc-component-deepsearch-cot > .hyc-content-md",
]

FETCH_JS = (
    "(() => {"
    f"  const sels = {json.dumps(CONTAINER_SELECTORS)};"
    "   for (const s of sels) {"
    "     const hits = document.querySelectorAll(s);"
    "     if (hits.length) return [...hits].map(e => e.outerHTML);"
    "   }"
    "   return [];"
    "})()"
)

# 语言标签只认这种长相的短标识，免得把「复制」「下载」这类按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")


def fetch_html(session: str) -> list[str]:
    """让 playwright-cli 把每轮回答的 HTML 取回来。"""
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
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit(f"playwright-cli 返回的不是合法 JSON：\n{proc.stdout[:300]}")


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


def _text(node) -> str:
    """文本节点取值，顺手把不换行空格拉回普通空格，输出更干净。"""
    return str(node).replace("\xa0", " ")


def _code_block(node: Tag) -> str:
    """元宝的代码块：pre.ybc-pre-component。

    横幅（.hyc-common-markdown__code__hd）里装着语言名和「复制」按钮，是整个
    pre 中唯一不属于代码的文本。不摘掉它，这些界面文字会混进正文——实测会输出
    成「pythondef bubble_sort」这样：语言名和代码首行黏在一起。
    语言名要在摘横幅之前取，取完再摘。
    """
    label = node.select_one(".hyc-common-markdown__code__langComponent__text")
    raw = label.get_text().strip() if label else ""
    lang = raw if LANG_RE.fullmatch(raw) else ""

    banner = node.select_one(".hyc-common-markdown__code__hd")
    if banner is not None:
        banner.extract()

    code = node.get_text().rstrip("\n")
    return f"\n\n```{lang}\n{code}\n```\n\n"


def walk(node) -> str:
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
    if _has_class(node, "ybc-li-component_dot") or _has_class(
        node, "ybc-li-component__dot-wp"
    ):
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
        if _has_class(node, "ybc-pre-component"):
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
    # 收尾压掉多余空行。代码块内部的连续空行也会被一起压掉——Markdown 里
    # 块内空行不承载语义，这个代价换实现更简单，划算。
    return re.sub(r"\n{3,}", "\n\n", walk(BeautifulSoup(html, "html.parser"))).strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="把元宝网页上的回答还原成 Markdown"
    )
    parser.add_argument(
        "--session",
        default="yuanbao",
        help="playwright-cli 的会话名（默认 yuanbao）",
    )
    args = parser.parse_args()

    blocks = [convert(html) for html in fetch_html(args.session)]
    print(json.dumps(blocks, ensure_ascii=False))


if __name__ == "__main__":
    main()
