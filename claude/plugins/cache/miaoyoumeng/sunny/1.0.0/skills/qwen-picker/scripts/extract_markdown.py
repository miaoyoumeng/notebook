#!/usr/bin/env python3
"""
千问回答区 HTML → Markdown 还原

为什么需要这个脚本：
千问网页把回答渲染成 HTML，页面上直接读文本拿到的是排版后的结果——
`**加粗**` 的星号、代码块的三反引号围栏、公式的 $ 定界符在渲染时就被吃掉了。
直接拿渲染文本展示，会和「回答原样保留 Markdown」的要求冲突。
本脚本沿 DOM 反向推回 Markdown 语法，把格式还回来。

为什么取 HTML 这一步要委托 playwright-cli：
浏览器由 playwright-cli 以 --remote-debugging-pipe 方式托管，没有开放 TCP 调试端口，
外部进程（含 Playwright 的 Python 绑定）连不进去，DOM 只能由它取。
取回来之后的 HTML → Markdown 转换，全部在本脚本里完成。

本脚本从 deepseek-picker 的同名脚本移植：HTML → Markdown 的转换逻辑完全通用，
三个站点相关的常量（CONTAINER_SELECTORS / CODE_BLOCK_CLASSES / CODE_BANNER_SELECTOR）
已按 2026-10-10 实测的千问页面结构设定。

页面改版导致取不到内容时，跑 --dump：它按文本长度列出页面上所有候选容器，
文本最长的那一坨通常就是回答区；把新的类名填进对应常量即可。

用法（在插件根目录执行，也就是 pyproject.toml 所在的那一层）：
    uv run python skills/qwen-picker/scripts/extract_markdown.py
    uv run python skills/qwen-picker/scripts/extract_markdown.py --dump

输出（正常模式）：JSON 数组，按对话顺序每轮回答一个元素；页面上还没有回答时是 []。
多轮追问场景下，数组下标即轮次（第 1 轮 = 下标 0）。
输出（--dump 模式）：候选容器清单，按文本长度降序。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# —— 以下三个常量与站点强相关，2026-10-10 实测千问页面后确定 ——

# 回答区容器。实测页面上只有一个 .qk-markdown，且只对应回答——提问不带这个类。
CONTAINER_SELECTORS = [
    ".qk-markdown",
]

# 代码块容器类名。
CODE_BLOCK_CLASSES = ["qw-md-code"]

# 代码块里的语言标签。横幅里唯一带 mr-auto 的 span（复制等按钮在它右侧）。
CODE_BANNER_SELECTOR = ".qw-md-code span.mr-auto"

# 表格工具栏的容器类名，里面放着「表格」标题和下载/导出按钮的文字。
TABLE_TOOLBAR_CLASSES = ["qk-md-table-action"]

# —— 以下为通用逻辑，两个站点共用 ——

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

# 诊断用：把页面上所有"像回答区"的容器按文本长度列出来。
# 同类名只留一个代表，避免同一容器嵌套多层时刷屏。
DUMP_JS = (
    "(() => {"
    "  const out = [];"
    "  const seen = new Set();"
    "  for (const el of document.querySelectorAll('div,article,section,main')) {"
    "    const cls = (typeof el.className === 'string' ? el.className : '').trim();"
    "    if (!cls || seen.has(cls)) continue;"
    "    const text = (el.textContent || '').trim();"
    "    if (text.length < 40) continue;"
    "    seen.add(cls);"
    "    out.push({tag: el.tagName.toLowerCase(), cls: cls, len: text.length});"
    "  }"
    "  return out.sort((a, b) => b.len - a.len).slice(0, 40);"
    "})()"
)

# 语言标签只认这种长相的短标识，免得把「复制」「下载」这类按钮文字错认成语言
LANG_RE = re.compile(r"^[\w+#.-]{1,20}$")


def run_eval(session: str, js: str):
    """让 playwright-cli 在页面里求值，返回解析后的 JSON。"""
    try:
        proc = subprocess.run(
            ["playwright-cli", "-s", session, "--raw", "eval", js],
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


def fetch_html(session: str) -> list[str]:
    """让 playwright-cli 把每轮回答的 HTML 取回来。"""
    return run_eval(session, FETCH_JS)


def dump_candidates(session: str) -> None:
    """列出页面上可能的回答容器，按文本长度降序——用来实测确定选择器。"""
    rows = run_eval(session, DUMP_JS)
    if not rows:
        sys.exit("没抓到候选元素。页面可能没加载完、没登录，或会话名不对。")

    print(f"{'文本长度':>8}  {'标签':<8} 类名")
    print("-" * 60)
    for r in rows:
        print(f"{r['len']:>8,}  {r['tag']:<8} {r['cls']}")
    print()
    print("回答区通常是文本最长的那一条。把它的类名填进 CONTAINER_SELECTORS 首位。")


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


def _code_text(node) -> str:
    """取代码原文，顺手丢掉行号。

    不能直接用 get_text()：千问用 react-syntax-highlighter 渲染代码，每行开头
    塞一个行号 span（类名 linenumber · react-syntax-highlighter-line-number，
    inline style 里带 user-select: none），get_text() 会把它一起捞出来，
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


def walk(node) -> str:
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
        code = (_code_text(pre) if pre else _code_text(node)).rstrip("\n")
        label = node.select_one(CODE_BANNER_SELECTOR) if CODE_BANNER_SELECTOR else None
        raw = label.get_text().strip() if label else ""
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
    parser = argparse.ArgumentParser(description="把千问网页上的回答还原成 Markdown")
    parser.add_argument(
        "--session",
        default="qianwen",
        help="playwright-cli 的会话名（默认 qianwen）",
    )
    parser.add_argument(
        "--dump",
        action="store_true",
        help="列出页面上可能的回答容器，用于实测确定选择器",
    )
    args = parser.parse_args()

    if args.dump:
        dump_candidates(args.session)
        return

    blocks = [convert(html) for html in fetch_html(args.session)]
    if not blocks:
        print(
            f"未匹配到回答元素（选择器：{CONTAINER_SELECTORS}）。\n"
            "若页面上确实已有回答，说明选择器还是 DeepSeek 的值——"
            "跑 --dump 查看页面结构后替换 CONTAINER_SELECTORS。",
            file=sys.stderr,
        )
    print(json.dumps(blocks, ensure_ascii=False))


if __name__ == "__main__":
    main()
