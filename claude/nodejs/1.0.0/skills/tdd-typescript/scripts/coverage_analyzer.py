#!/usr/bin/env python3
"""分析和解析 TypeScript 项目的测试覆盖率报告（LCOV / JSON）。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
app = typer.Typer(help="分析 TypeScript 项目覆盖率报告")


P0_KEYWORDS = ["handle", "error", "catch", "fail", "invalid", "reject", "throw"]
P1_KEYWORDS = ["if", "else", "switch", "case", "branch", "condition"]


def classify_gap(file_path: str, lines: str, functions: str) -> str:
    """根据文件名和行号信息分类覆盖率缺口优先级。"""
    combined = f"{file_path} {functions}".lower()
    if any(kw in combined for kw in P0_KEYWORDS):
        return "P0"
    if any(kw in combined for kw in P1_KEYWORDS):
        return "P1"
    return "P2"


def parse_lcov(content: str) -> dict:
    """解析 LCOV 格式的覆盖率报告。"""
    files: dict[str, dict] = {}
    current_file: Optional[str] = None
    current_data: dict = {}

    for line in content.strip().split("\n"):
        line = line.strip()
        if line.startswith("SF:"):
            current_file = line[3:]
            current_data = {"file": current_file, "lines": [], "functions": [], "branches": []}
            files[current_file] = current_data
        elif line.startswith("DA:") and current_file:
            parts = line[3:].split(",")
            current_data["lines"].append({"line": int(parts[0]), "hit": int(parts[1])})
        elif line.startswith("FN:") and current_file:
            parts = line[3:].split(",")
            current_data["functions"].append({"line": int(parts[0]), "name": parts[1]})
        elif line.startswith("FNDA:") and current_file:
            parts = line[4:].split(",")
            hit = int(parts[0])
            name = parts[1]
            for fn in current_data["functions"]:
                if fn["name"] == name:
                    fn["hit"] = hit

    return files


def parse_json(content: str) -> dict:
    """解析 Istanbul/V8 JSON 覆盖率报告。"""
    data = json.loads(content)
    files: dict[str, dict] = {}

    for file_path, file_data in data.items():
        lines = []
        for line_no_str, hit in file_data.get("s", {}).items():
            lines.append({"line": int(line_no_str), "hit": hit})

        fn_map = file_data.get("fnMap", {})
        fn_hits = file_data.get("f", {})
        functions = []
        for fn_id, fn_info in fn_map.items():
            functions.append({
                "line": fn_info.get("decl", {}).get("start", {}).get("line", 0),
                "name": fn_info.get("name", "unknown"),
                "hit": fn_hits.get(fn_id, 0),
            })

        files[file_path] = {"file": file_path, "lines": lines, "functions": functions, "branches": []}

    return files


def detect_format(content: str) -> str:
    """自动检测覆盖率报告格式。"""
    content = content.strip()
    if content.startswith("SF:") or "end_of_record" in content:
        return "lcov"
    if content.startswith("{") and ("s\":" in content or '"s":' in content):
        return "json"
    return "lcov"


def calculate_coverage(file_data: dict) -> dict:
    """计算单个文件的覆盖率指标。"""
    lines = file_data.get("lines", [])
    fns = file_data.get("functions", [])

    total_lines = len(lines)
    covered_lines = sum(1 for l in lines if l["hit"] > 0) if total_lines > 0 else 0
    total_fns = len(fns)
    covered_fns = sum(1 for f in fns if f.get("hit", 0) > 0) if total_fns > 0 else 0

    return {
        "line_pct": round(covered_lines / total_lines * 100, 1) if total_lines > 0 else 0,
        "fn_pct": round(covered_fns / total_fns * 100, 1) if total_fns > 0 else 0,
        "total_lines": total_lines,
        "covered_lines": covered_lines,
        "total_fns": total_fns,
        "covered_fns": covered_fns,
    }


def find_gaps(files: dict) -> list[dict]:
    """查找未覆盖的代码区域。"""
    gaps: list[dict] = []
    for file_path, data in files.items():
        if any(x in file_path for x in [".d.ts", "index.ts", "__tests__"]):
            continue

        # 未覆盖的行
        uncovered_lines = [l for l in data.get("lines", []) if l["hit"] == 0]
        # 未覆盖的函数
        uncovered_fns = [f for f in data.get("functions", []) if f.get("hit", 0) == 0]

        for ul in uncovered_lines:
            gaps.append({
                "file": file_path,
                "line": ul["line"],
                "type": "line",
                "priority": "P1",
            })

        for uf in uncovered_fns:
            priority = classify_gap(file_path, str(uf["line"]), uf["name"])
            gaps.append({
                "file": file_path,
                "line": uf["line"],
                "name": uf["name"],
                "type": "function",
                "priority": priority,
            })

    return sorted(gaps, key=lambda g: {"P0": 0, "P1": 1, "P2": 2}[g["priority"]])


# ── CLI ───────────────────────────────────────────────────

@app.command()
def analyze(
    report: Path = typer.Option(..., "--report", "-r", help="覆盖率报告文件路径"),
    threshold: float = typer.Option(80.0, "--threshold", "-t", help="目标覆盖率阈值"),
):
    """分析覆盖率报告，识别缺口并按优先级排序。"""
    if not report.exists():
        console.print(f"[red]报告文件不存在: {report}[/red]")
        raise typer.Exit(1)

    content = report.read_text()
    fmt = detect_format(content)

    if fmt == "lcov":
        files = parse_lcov(content)
    else:
        files = parse_json(content)

    if not files:
        console.print("[yellow]未在报告中找到任何文件数据[/yellow]")
        raise typer.Exit(0)

    # 计算总体覆盖率
    total_lines = sum(len(d.get("lines", [])) for d in files.values())
    total_covered = sum(sum(1 for l in d.get("lines", []) if l["hit"] > 0) for d in files.values())
    overall = round(total_covered / total_lines * 100, 1) if total_lines > 0 else 0

    status_color = "green" if overall >= threshold else "yellow" if overall >= threshold * 0.7 else "red"
    console.print(f"\n[bold]TypeScript 覆盖率报告 — [/bold][{status_color}]总体: {overall}%[/{status_color}] (阈值: {threshold}%)\n")

    # 文件级覆盖率
    file_table = Table(title="文件覆盖率明细")
    file_table.add_column("文件", style="cyan")
    file_table.add_column("行覆盖率", style="yellow")
    file_table.add_column("函数覆盖率", style="magenta")
    file_table.add_column("状态")

    for fp, data in files.items():
        cov = calculate_coverage(data)
        status = "✅" if cov["line_pct"] >= threshold else "❌"
        file_table.add_row(fp, f"{cov['line_pct']}% ({cov['covered_lines']}/{cov['total_lines']})", f"{cov['fn_pct']}% ({cov['covered_fns']}/{cov['total_fns']})", status)

    console.print(file_table)

    # 缺口分析
    gaps = find_gaps(files)
    if gaps:
        console.print("\n[bold]覆盖率缺口（按优先级排序）[/bold]\n")

        priorities: dict[str, list[dict]] = {}
        for g in gaps:
            priorities.setdefault(g["priority"], []).append(g)

        for p in ("P0", "P1", "P2"):
            items = priorities.get(p, [])
            if not items:
                continue
            color = {"P0": "red", "P1": "yellow", "P2": "dim"}[p]
            console.print(f"[bold {color}]{p} — {'关键缺口' if p == 'P0' else '高价值缺口' if p == 'P1' else '低风险缺口'}（{len(items)} 项）[/bold {color}]")
            for g in items[:10]:
                name_str = f"  {g.get('name', 'unknown')}()" if g["type"] == "function" else f"  行 {g['line']}"
                console.print(f"  [{color}]{g['file']}:{g['line']}[/{color}]{name_str}")
            if len(items) > 10:
                console.print(f"  ... 还有 {len(items) - 10} 项\n")

    if overall < threshold:
        needed = threshold - overall
        console.print(f"\n[yellow]建议：需要提升 {needed:.1f}% 覆盖率达到 {threshold}% 阈值。优先生成 P0 项目的测试。[/yellow]")
    else:
        console.print(f"\n[green]覆盖率已满足 {threshold}% 阈值要求。[/green]")


@app.command()
def summary(report: Path = typer.Argument(..., help="覆盖率报告文件路径")):
    """快速查看覆盖率摘要。"""
    content = report.read_text()
    fmt = detect_format(content)
    files = parse_lcov(content) if fmt == "lcov" else parse_json(content)

    total_lines = sum(len(d.get("lines", [])) for d in files.values())
    total_covered = sum(sum(1 for l in d.get("lines", []) if l["hit"] > 0) for d in files.values())
    overall = round(total_covered / total_lines * 100, 1) if total_lines > 0 else 0

    total_fns = sum(len(d.get("functions", [])) for d in files.values())
    covered_fns = sum(sum(1 for f in d.get("functions", []) if f.get("hit", 0) > 0) for d in files.values())
    fn_cov = round(covered_fns / total_fns * 100, 1) if total_fns > 0 else 0

    panel = Panel(
        f"行覆盖率: {overall}% ({total_covered}/{total_lines})\n"
        f"函数覆盖率: {fn_cov}% ({covered_fns}/{total_fns})\n"
        f"文件数: {len(files)}",
        title="覆盖率摘要",
        border_style="green" if overall >= 80 else "yellow",
    )
    console.print(panel)


if __name__ == "__main__":
    app()
