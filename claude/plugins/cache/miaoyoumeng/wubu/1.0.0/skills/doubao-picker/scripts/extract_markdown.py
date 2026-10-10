#!/usr/bin/env python3
"""
豆包回答区 HTML → Markdown 还原

为什么需要这个脚本：
豆包网页把回答渲染成 HTML，页面上直接读文本拿到的是排版后的结果——
`**加粗**` 的星号、代码块的三反引号围栏、公式的定界符在渲染时就被吃掉了。
直接拿渲染文本展示，会和「回答原样保留 Markdown」的要求冲突。
本脚本沿 DOM 反向推回 Markdown 语法，把格式还回来。

为什么取 HTML 这一步要委托 playwright-cli：
浏览器由 playwright-cli 以 --remote-debugging-pipe 方式托管，没有开放 TCP 调试端口，
外部进程（含 Playwright 的 Python 绑定）连不进去，DOM 只能由它取。
取回来之后的 HTML → Markdown 转换，全部在本脚本里完成。

用法（在插件根目录执行，也就是 pyproject.toml 所在的那一层）：
    uv run python skills/doubao-picker/scripts/extract_markdown.py
    uv run python skills/doubao-picker/scripts/extract_markdown.py --session chat.doubao

输出：JSON 数组，按对话顺序每轮回答一个元素；页面上还没有回答时是 []。
多轮追问场景下，数组下标即轮次（第 1 轮 = 下标 0）。

为什么要按 data-message-role="assistant" 分组：
豆包会把同一轮回答拆成多个 .md-box-root——开场白、工具调用说明、正文各占一个，
实测一轮出现过 4 个（2026-10）。生成结束后这些容器并不总会合并：有的轮次收敛成 1 个，
有的轮次原样留着多个。若把所有 .md-box-root 摊平输出，一轮会被当成好几轮，
下标与真实轮次对不上。所以先按轮次容器分组，组内拼接，组间不混。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# 一轮对话的容器。必须带 data-message-role="assistant"：
# 用户提问也带 .md-box-root，只用类名会把提问一起捞进来。
ROUND_SELECTOR = '[data-message-role="assistant"]'

# 轮次容器内的正文容器。一轮可能有多个（开场白 / 工具说明 / 正文各占一个），
# 分组后由 convert_round 拼接，不摊平成多轮。
BODY_SELECTOR = ".md-box-root"

FETCH_JS = (
    "(() => {"
    f"  const rounds = document.querySelectorAll({json.dumps(ROUND_SELECTOR)});"
    "   return [...rounds].map(r =>"
    f"     [...r.querySelectorAll({json.dumps(BODY_SELECTOR)})].map(e => e.outerHTML)"
    "   );"
    "})()"
)

# 语言标签只认这种长相的短标识，免得把按钮文字错认成语言
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


def _class_contains(node: Tag, fragment: str) -> bool:
    return any(fragment in c for c in (node.get("class") or []))


def _tex(raw: str) -> str:
    """把豆包 copy-text 里的 LaTeX 还原成 Markdown 数学定界符。

    豆包把公式原文存在 copy-text 属性里，行内形如 `\\(E = mc^2\\)`。
    转成 `$...$` / `$$...$$` 是 Markdown 的通行写法，渲染器都认。
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


def convert_round(blocks: list[str]) -> str:
    """一轮里的多个正文容器按顺序拼接；空容器直接丢掉，不影响下标。"""
    parts = [b for b in (convert(html) for html in blocks) if b]
    return "\n\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="把豆包网页上的回答还原成 Markdown"
    )
    parser.add_argument(
        "--session",
        default="chat.doubao",
        help="playwright-cli 的会话名（默认 chat.doubao）",
    )
    args = parser.parse_args()

    rounds = [convert_round(blocks) for blocks in fetch_html(args.session)]
    print(json.dumps(rounds, ensure_ascii=False))


if __name__ == "__main__":
    main()
