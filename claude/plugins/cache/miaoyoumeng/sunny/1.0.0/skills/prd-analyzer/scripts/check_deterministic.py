#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prd-analyzer 确定性检查脚本（继承自原 prd-validator）。

实现维度 4（表格对齐）、维度 5（模板完整性）、维度 7（排版与结构）中的
确定性规则；语义类维度（导航、命名、图文、字典、规则、角色、5W1H）
仍由模型按 SKILL.md 规则执行。

用法：
    python3 check_deterministic.py <PRD 文件或目录> [...]
    # 目录输入递归扫描 *.md

输出：stdout 打印 JSON，结构为
    {"files": [...], "findings": [{file, line, dimension, rule, severity, detail}], "summary": {...}}
line 为 0 表示文档级问题（如章节缺失）。

无第三方依赖。严重度与 prd-analyzer/SKILL.md「验证（Verification）- 公共规则 - 严重程度」一致。
已知简化：单元格内转义管道符（\\|）按分列处理，可能误报列数问题。
"""

import json
import re
import sys
from pathlib import Path

PLACEHOLDER_KEYWORDS = ["TBD", "TODO", "待补充", "[待展开]"]

# 必选章节：(章节号, 标题关键词)，依据 prd-writer 模板
REQUIRED_CHAPTERS = [
    ("一", "需求背景"),
    ("二", "页面UI"),
    ("三", "用户角色"),
    ("四", "页面目标"),
    ("五", "功能详细说明"),
    ("六", "数据展示"),
    ("七", "交互需求"),
    ("八", "用户旅程"),
    ("十", "功能导航"),
]

CN_ORDER = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一"]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
SEP_CELL_RE = re.compile(r"^:?-{3,}:?$")
LONG_CHAPTER_LINES = 80


def add(findings, file, line, dimension, rule, severity, detail):
    findings.append({
        "file": str(file),
        "line": line,
        "dimension": dimension,
        "rule": rule,
        "severity": severity,
        "detail": detail,
    })


def build_fence_mask(lines):
    mask = []
    in_fence = False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            mask.append(True)
            in_fence = not in_fence
            continue
        mask.append(in_fence)
    return mask


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def is_separator(cells):
    return bool(cells) and all(SEP_CELL_RE.match(c) for c in cells)


def check_tables(path, lines, fence_mask, findings):
    i, n = 0, len(lines)
    while i < n:
        if fence_mask[i] or not lines[i].lstrip().startswith("|"):
            i += 1
            continue
        start = i
        while i < n and not fence_mask[i] and lines[i].lstrip().startswith("|"):
            i += 1
        block = lines[start:i]
        if len(block) < 2:
            continue
        header = split_row(block[0])
        ncols = len(header)
        sep_ok = is_separator(split_row(block[1]))
        if not sep_ok:
            add(findings, path, start + 2, "表格对齐", "分隔行合法", "High",
                f"表格（第 {start + 1} 行起）表头下一行不是合法分隔行，渲染时整张表失效")
        body = block[1:] if not sep_ok else block[2:]
        body_off = 1 if not sep_ok else 2
        for off, row in enumerate(body, start=body_off):
            cells = split_row(row)
            if len(cells) != ncols:
                add(findings, path, start + off + 1, "表格对齐", "列数一致", "High",
                    f"该行 {len(cells)} 列，表头 {ncols} 列：{row.strip()[:60]}")
        empties = [idx + 1 for idx, c in enumerate(header) if c == ""]
        if empties:
            add(findings, path, start + 1, "表格对齐", "空表头", "Medium",
                f"表头第 {', '.join(str(x) for x in empties)} 列为空")
        if sep_ok:
            rows = [header] + [split_row(r) for r in block[2:]]
            rows = [r for r in rows if len(r) == ncols]
            for col in range(ncols):
                ws = [len(r[col]) for r in rows]
                if ws and max(ws) - min(ws) > 2:
                    add(findings, path, start + 1, "表格对齐", "源码对齐", "Low",
                        f"表格（第 {start + 1} 行起）第 {col + 1} 列管道符宽度未对齐")
                    break


def check_placeholders(path, lines, findings):
    for idx, ln in enumerate(lines):
        for kw in PLACEHOLDER_KEYWORDS:
            if kw in ln:
                add(findings, path, idx + 1, "模板完整性", "占位符残留", "High",
                    f"发现占位符「{kw}」：{ln.strip()[:60]}")


def find_chapters(lines, fence_mask):
    found = {}
    order = []
    for idx, ln in enumerate(lines):
        if fence_mask[idx]:
            continue
        t = ln.strip().lstrip("#").strip()
        for num in CN_ORDER:
            if t.startswith(f"{num}、"):
                if num not in found:
                    found[num] = (idx + 1, t)
                    order.append((CN_ORDER.index(num), t))
                break
    return found, order


def check_structure(path, lines, fence_mask, findings):
    headings = []
    for idx, ln in enumerate(lines):
        if fence_mask[idx]:
            continue
        m = HEADING_RE.match(ln)
        if m:
            headings.append((idx + 1, len(m.group(1)), m.group(2).strip()))

    prev = None
    for line, level, text in headings:
        if prev is not None and level > prev + 1:
            add(findings, path, line, "排版与结构", "标题层级", "Low",
                f"标题级别跳级（H{prev} → H{level}）：{text[:40]}")
        prev = level

    found, order = find_chapters(lines, fence_mask)

    for num, kw in REQUIRED_CHAPTERS:
        if num not in found or kw not in found[num][1]:
            add(findings, path, 0, "模板完整性", "必选章节覆盖", "High",
                f"缺失必选章节「{num}、…{kw}…」")

    for a, b in zip(order, order[1:]):
        if b[0] < a[0]:
            add(findings, path, 0, "排版与结构", "章节顺序", "Medium",
                f"章节顺序错乱：「{a[1][:20]}」之后出现「{b[1][:20]}」")
            break

    h2s = [(line, text) for line, level, text in headings if level == 2]
    for k, (line, text) in enumerate(h2s):
        end = h2s[k + 1][0] - 1 if k + 1 < len(h2s) else len(lines)
        body = lines[line:end]
        has_sub = any(HEADING_RE.match(b) and len(HEADING_RE.match(b).group(1)) >= 3
                      for b in body)
        nonempty = sum(1 for b in body if b.strip())
        if not has_sub and nonempty > LONG_CHAPTER_LINES:
            add(findings, path, line, "排版与结构", "标题层级", "Medium",
                f"章节「{text[:20]}」达 {nonempty} 行且无子标题，压缩时难以保留关键信息")


def collect_files(paths):
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"路径不存在: {p}", file=sys.stderr)
            sys.exit(1)
    return files


def main():
    args = sys.argv[1:]
    if not args:
        print("用法: check_deterministic.py <PRD 文件或目录> [...]", file=sys.stderr)
        sys.exit(2)
    files = collect_files(args)
    if not files:
        print("未找到任何 .md 文件", file=sys.stderr)
        sys.exit(1)
    findings = []
    for f in files:
        lines = f.read_text(encoding="utf-8").splitlines()
        mask = build_fence_mask(lines)
        check_tables(f, lines, mask, findings)
        check_placeholders(f, lines, findings)
        check_structure(f, lines, mask, findings)
    findings.sort(key=lambda x: (x["file"], x["line"]))
    summary = {s: sum(1 for x in findings if x["severity"] == s)
               for s in ("High", "Medium", "Low")}
    print(json.dumps({"files": [str(f) for f in files],
                      "findings": findings,
                      "summary": summary},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
