#!/usr/bin/env python3
"""
覆盖率分析器 - 解析 JaCoCo XML/CSV 覆盖率报告，识别缺口并按优先级排序。

优先级：
  P0 - 关键路径未覆盖（auth、支付、数据校验、核心业务）
  P1 - 行覆盖率 < 阈值
  P2 - 分支覆盖率 < 阈值
"""
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer()
console = Console()

CRITICAL_PATHS = [
    "auth", "login", "permission", "verify", "password",
    "payment", "pay", "charge", "refund", "billing",
    "validate", "validation", "sanitize", "check",
    "user", "account", "order", "transaction",
]


def parse_jacoco_xml(filepath: Path) -> list[dict]:
    """解析 JaCoCo XML 报告。"""
    tree = ET.parse(filepath)
    root = tree.getroot()
    results = []

    for pkg in root.findall(".//package"):
        pkg_name = pkg.get("name", "").replace("/", ".")
        for cls in pkg.findall("class"):
            class_name = cls.get("name", "").replace("/", ".")
            for method in cls.findall("method"):
                name = method.get("name", "")
                line_counter = None
                branch_counter = None
                for counter in method.findall("counter"):
                    ctype = counter.get("type")
                    missed = int(counter.get("missed", 0))
                    covered = int(counter.get("covered", 0))
                    total = missed + covered
                    ratio = covered / total if total > 0 else 0
                    if ctype == "LINE":
                        line_counter = {"missed": missed, "covered": covered, "ratio": ratio}
                    elif ctype == "BRANCH":
                        branch_counter = {"missed": missed, "covered": covered, "ratio": ratio}

                results.append({
                    "package": pkg_name,
                    "class": class_name,
                    "method": name,
                    "line_missed": line_counter["missed"] if line_counter else 0,
                    "line_covered": line_counter["covered"] if line_counter else 0,
                    "line_ratio": line_counter["ratio"] if line_counter else 0,
                    "branch_missed": branch_counter["missed"] if branch_counter else 0,
                    "branch_covered": branch_counter["covered"] if branch_counter else 0,
                    "branch_ratio": branch_counter["ratio"] if branch_counter else 0,
                })
    return results


def parse_jacoco_csv(filepath: Path) -> list[dict]:
    """解析 JaCoCo CSV 报告。"""
    results = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line_covered = int(row.get("LINE_COVERED", 0))
            line_missed = int(row.get("LINE_MISSED", 0))
            line_total = line_covered + line_missed
            branch_covered = int(row.get("BRANCH_COVERED", 0))
            branch_missed = int(row.get("BRANCH_MISSED", 0))
            branch_total = branch_covered + branch_missed

            results.append({
                "package": row.get("PACKAGE", "").replace("/", "."),
                "class": row.get("CLASS", "").replace("/", "."),
                "method": row.get("METHOD", ""),
                "line_missed": line_missed,
                "line_covered": line_covered,
                "line_ratio": line_covered / line_total if line_total > 0 else 0,
                "branch_missed": branch_missed,
                "branch_covered": branch_covered,
                "branch_ratio": branch_covered / branch_total if branch_total > 0 else 0,
            })
    return results


def assign_priority(item: dict, line_threshold: float, branch_threshold: float) -> str:
    """按优先级分类覆盖率缺口。"""
    fqn = f"{item['package']}.{item['class']}.{item['method']}".lower()

    # P0: 关键路径无覆盖
    for path in CRITICAL_PATHS:
        if path in fqn and item["line_ratio"] == 0:
            return "P0"

    # P1: 行覆盖率低于阈值
    if item["line_ratio"] < line_threshold / 100:
        return "P1"

    # P2: 分支覆盖率低于阈值
    if item["branch_ratio"] < branch_threshold / 100:
        return "P2"

    return "-"


def build_summary(results: list[dict]) -> dict:
    """构建覆盖率摘要。"""
    if not results:
        return {"line_ratio": 0, "branch_ratio": 0, "method_ratio": 0, "total_methods": 0}

    total_line_covered = sum(r["line_covered"] for r in results)
    total_line_missed = sum(r["line_missed"] for r in results)
    total_line = total_line_covered + total_line_missed
    total_branch_covered = sum(r["branch_covered"] for r in results)
    total_branch_missed = sum(r["branch_missed"] for r in results)
    total_branch = total_branch_covered + total_branch_missed
    total_methods = len(results)
    covered_methods = sum(1 for r in results if r["line_ratio"] > 0)

    return {
        "line_ratio": total_line_covered / total_line if total_line > 0 else 0,
        "branch_ratio": total_branch_covered / total_branch if total_branch > 0 else 0,
        "method_ratio": covered_methods / total_methods if total_methods > 0 else 0,
        "total_methods": total_methods,
        "total_lines": total_line,
        "total_branches": total_branch,
    }


@app.command()
def analyze(
    report: Path = typer.Option(..., "--report", "-r", help="JaCoCo 报告文件（XML 或 CSV）"),
    threshold: int = typer.Option(80, "--threshold", "-t", help="目标行覆盖率阈值（百分比）"),
    branch_threshold: int = typer.Option(75, "--branch-threshold", help="目标分支覆盖率阈值（百分比）"),
    source_dir: Optional[Path] = typer.Option(None, "--source", "-s", help="源代码目录"),
    priority_filter: Optional[str] = typer.Option(None, "--priority", "-p", help="只显示指定优先级（P0/P1/P2）"),
):
    """
    分析 JaCoCo 覆盖率报告，识别缺口并按优先级推荐。
    """
    console.print(Panel.fit("[bold blue]TDD Java — 覆盖率分析器[/bold blue]"))

    if not report.exists():
        console.print(f"[red]错误: 报告文件不存在: {report}[/red]")
        raise typer.Exit(code=1)

    # 解析报告
    suffix = report.suffix.lower()
    if suffix == ".xml":
        results = parse_jacoco_xml(report)
    elif suffix == ".csv":
        results = parse_jacoco_csv(report)
    else:
        console.print(f"[red]错误: 不支持的格式 {suffix}。支持 XML 和 CSV。[/red]")
        raise typer.Exit(code=1)

    if not results:
        console.print("[yellow]警告: 报告为空或解析失败。[/yellow]")
        raise typer.Exit(code=0)

    # 摘要
    summary = build_summary(results)
    console.print(f"\n[bold]覆盖率摘要[/bold]")
    console.print(f"行覆盖率:   [{'green' if summary['line_ratio'] >= threshold/100 else 'red'}]{summary['line_ratio']:.1%}[/] (目标: {threshold}%)")
    console.print(f"分支覆盖率: [{'green' if summary['branch_ratio'] >= branch_threshold/100 else 'red'}]{summary['branch_ratio']:.1%}[/] (目标: {branch_threshold}%)")
    console.print(f"方法覆盖率: {summary['method_ratio']:.1%}")
    console.print(f"总方法数:   {summary['total_methods']}")

    # 优先级分类
    for r in results:
        r["priority"] = assign_priority(r, threshold, branch_threshold)

    gaps = [r for r in results if r["priority"] in ("P0", "P1", "P2")]
    if priority_filter:
        gaps = [r for r in gaps if r["priority"] == priority_filter]

    p0_count = sum(1 for r in results if r["priority"] == "P0")
    p1_count = sum(1 for r in results if r["priority"] == "P1")
    p2_count = sum(1 for r in results if r["priority"] == "P2")

    console.print(f"\n[bold]缺口分布[/bold]")
    console.print(f"P0 (关键路径): {p0_count}")
    console.print(f"P1 (行覆盖率): {p1_count}")
    console.print(f"P2 (分支覆盖率): {p2_count}")

    if gaps:
        table = Table(title="按优先级排序的覆盖率缺口")
        table.add_column("优先级", style="bold")
        table.add_column("包")
        table.add_column("类")
        table.add_column("方法")
        table.add_column("行覆盖率")
        table.add_column("分支覆盖率")
        table.add_column("建议")

        for g in sorted(gaps, key=lambda x: (["P0", "P1", "P2"].index(x["priority"]), x["line_ratio"]))[:30]:
            priority_color = {"P0": "red", "P1": "yellow", "P2": "dim"}.get(g["priority"], "")
            suggestion = _get_suggestion(g)
            table.add_row(
                f"[{priority_color}]{g['priority']}[/{priority_color}]",
                g["package"][:40],
                g["class"][:40],
                g["method"][:30],
                f"{g['line_ratio']:.0%}",
                f"{g['branch_ratio']:.0%}",
                suggestion,
            )

        console.print(table)

    console.print(f"\n[bold]推荐操作[/bold]")
    console.print("1. [red]P0[/red]: 立即为关键路径方法编写测试（auth/payment/validation）")
    console.print("2. [yellow]P1[/yellow]: 补充行覆盖率低于阈值的测试")
    console.print("3. [dim]P2[/dim]: 补充分支场景测试（if-else/try-catch）")


def _get_suggestion(item: dict) -> str:
    """根据缺口类型生成建议。"""
    if item["line_ratio"] == 0:
        return "优先补测试（BCDE-C: 正确输入 + BCDE-E: 错误输入）"
    elif item["branch_ratio"] == 0 and item["line_ratio"] > 0.5:
        return "补充分支测试（BCDE-B: 边界值）"
    elif item["line_ratio"] < 0.5:
        return "增加场景覆盖"
    else:
        return "补充边界和异常测试"


@app.command()
def summary(
    report: Path = typer.Option(..., "--report", "-r", help="JaCoCo 报告文件"),
):
    """快速查看覆盖率摘要。"""
    suffix = report.suffix.lower()
    if suffix == ".xml":
        results = parse_jacoco_xml(report)
    elif suffix == ".csv":
        results = parse_jacoco_csv(report)
    else:
        console.print(f"[red]不支持的格式: {suffix}[/red]")
        raise typer.Exit(code=1)

    s = build_summary(results)
    console.print(f"行覆盖率: {s['line_ratio']:.1%}")
    console.print(f"分支覆盖率: {s['branch_ratio']:.1%}")
    console.print(f"方法覆盖率: {s['method_ratio']:.1%}")
    console.print(f"总行数: {s['total_lines']}, 总方法数: {s['total_methods']}")


@app.command()
def version():
    """显示版本信息。"""
    console.print("tdd-java coverage_analyzer v1.0.0")


if __name__ == "__main__":
    app()
