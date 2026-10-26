#!/usr/bin/env python3
"""引导 TypeScript TDD Red-Green-Refactor 工作流。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
app = typer.Typer(help="TDD Red-Green-Refactor 工作流引导")


PHASE_CHECKS = {
    "red": [
        "是否已编写测试代码？（测试应描述期望行为）",
        "测试是否能编译通过？（无语法/类型错误）",
        "运行测试是否失败？（因缺少实现而非语法错误）",
        "失败信息是否有意义？（明确显示缺少什么）",
    ],
    "green": [
        "是否只编写了使测试通过的最小代码？",
        "所有测试是否全部通过？",
        "是否修改过测试代码？（不应修改已写好的测试）",
        "是否引入了超出测试要求的功能？",
    ],
    "refactor": [
        "所有测试是否保持绿色？",
        "是否消除了重复代码？",
        "变量/函数命名是否清晰？",
        "是否移除了调试代码或临时代码？",
        "复杂度是否在合理范围内？（圈复杂度 < 10）",
    ],
}

ANTI_PATTERNS = {
    "red": [
        "先写实现代码再写测试",
        "测试空白或无断言",
        "同时测试多个行为",
        "测试依赖外部状态（数据库、网络）",
    ],
    "green": [
        "一次实现过多功能",
        "在 GREEN 阶段修改测试",
        "跳过 RED 阶段验证",
        "实现代码包含未测试的逻辑",
    ],
    "refactor": [
        "跳过重构直接进行下一轮",
        "重构后不运行测试",
        "引入不必要的抽象",
        "同时重构测试和实现代码",
    ],
}


def load_workflow_state(state_file: Path) -> dict:
    """加载工作流状态文件。"""
    if state_file.exists():
        return json.loads(state_file.read_text())
    return {"phase": "red", "cycles": [], "files": []}


def save_workflow_state(state_file: Path, state: dict) -> None:
    """保存工作流状态文件。"""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))


@app.command()
def check(
    phase: str = typer.Option("red", "--phase", "-p", help="当前 TDD 阶段: red | green | refactor"),
    state_file: Optional[Path] = typer.Option(None, "--state", "-s", help="工作流状态文件路径"),
):
    """验证当前阶段的完成情况。"""
    phase = phase.lower()
    if phase not in PHASE_CHECKS:
        console.print(f"[red]无效阶段: {phase}，可选: red, green, refactor[/red]")
        raise typer.Exit(1)

    phase_names = {"red": "RED — 编写失败测试", "green": "GREEN — 最小实现通过测试", "refactor": "REFACTOR — 重构优化"}

    console.print(f"\n[bold]TDD 阶段: {phase_names[phase]}[/bold]\n")

    # 检查清单
    console.print("[bold]验证清单:[/bold]")
    for i, check_item in enumerate(PHASE_CHECKS[phase], 1):
        console.print(f"  {i}. [ ] {check_item}")

    # 反模式警告
    console.print(f"\n[bold yellow]⚠ 常见反模式 — 请避免:[/bold yellow]")
    for anti in ANTI_PATTERNS[phase]:
        console.print(f"  ❌ {anti}")

    # 下一阶段提示
    next_phase = {"red": "green", "green": "refactor", "refactor": "red"}
    console.print(f"\n[bold green]完成以上验证后进入 → {next_phase[phase].upper()} 阶段[/bold green]")


@app.command()
def next(
    phase: str = typer.Option(..., "--phase", "-p", help="即将进入的阶段: red | green | refactor"),
    test_file: Optional[str] = typer.Option(None, "--test", "-t", help="当前测试文件路径"),
    impl_file: Optional[str] = typer.Option(None, "--impl", "-i", help="实现文件路径"),
    state_file: Optional[Path] = typer.Option(None, "--state", "-s", help="工作流状态文件路径"),
):
    """进入下一个 TDD 阶段并获取指导。"""
    phase = phase.lower()
    if phase not in PHASE_CHECKS:
        console.print(f"[red]无效阶段: {phase}[/red]")
        raise typer.Exit(1)

    guidance = {
        "red": Panel(
            "[bold]RED 阶段指引[/bold]\n\n"
            "1. 根据需求/规格编写测试代码\n"
            "2. 测试名描述预期行为: it('should <行为> when <条件>')\n"
            "3. 遵循 AAA 模式: Arrange → Act → Assert\n"
            "4. 运行测试并确认失败（因缺少实现）\n"
            "5. 确认失败信息有意义，非语法错误\n\n"
            "⚠ 不要写任何实现代码！",
            border_style="red",
        ),
        "green": Panel(
            "[bold]GREEN 阶段指引[/bold]\n\n"
            "1. 编写最小代码，只使当前测试通过\n"
            "2. 不要添加额外功能或优化\n"
            "3. 重复代码暂时可以接受\n"
            "4. 运行测试确认通过\n"
            "5. 提交代码（安全检查点）\n\n"
            "⚠ 只让失败的测试通过，不要多做！",
            border_style="green",
        ),
        "refactor": Panel(
            "[bold]REFACTOR 阶段指引[/bold]\n\n"
            "1. 消除重复代码\n"
            "2. 改进变量/函数命名\n"
            "3. 提取公共方法或工具函数\n"
            "4. 每次小重构后运行全部测试\n"
            "5. 确保测试保持绿色\n\n"
            "建议检查:\n"
            "- 圈复杂度 < 10\n"
            "- 函数长度 < 20 行\n"
            "- 类长度 < 200 行\n"
            "- 无重复代码块(>3行)",
            border_style="blue",
        ),
    }

    console.print(guidance[phase])

    # 记录状态
    if state_file:
        state = load_workflow_state(state_file)
        cycle = {"phase": phase, "test_file": test_file, "impl_file": impl_file}
        state["cycles"].append(cycle)
        state["phase"] = phase
        if test_file:
            state["files"].append(test_file)
        if impl_file:
            state["files"].append(impl_file)
        save_workflow_state(state_file, state)
        console.print(f"\n[dim]状态已保存至: {state_file}[/dim]")


@app.command()
def report(state_file: Path = typer.Argument(..., help="工作流状态文件路径")):
    """输出 TDD 工作流执行报告。"""
    if not state_file.exists():
        console.print("[red]状态文件不存在，请先运行 TDD 工作流[/red]")
        raise typer.Exit(1)

    state = load_workflow_state(state_file)
    cycles = state.get("cycles", [])

    table = Table(title="TDD 工作流报告")
    table.add_column("序号", style="dim")
    table.add_column("阶段", style="cyan")
    table.add_column("测试文件", style="green")
    table.add_column("实现文件", style="yellow")

    red_count = green_count = refactor_count = 0
    for i, cycle in enumerate(cycles, 1):
        phase = cycle.get("phase", "unknown")
        if phase == "red":
            red_count += 1
        elif phase == "green":
            green_count += 1
        elif phase == "refactor":
            refactor_count += 1
        table.add_row(str(i), phase.upper(), cycle.get("test_file", "-"), cycle.get("impl_file", "-"))

    console.print(table)
    console.print(f"\n[bold]统计:[/bold] RED={red_count}  GREEN={green_count}  REFACTOR={refactor_count}")
    console.print(f"涉及文件: {len(set(state.get('files', [])))} 个")

    if red_count > 0 and green_count > 0:
        ratio = green_count / red_count
        if ratio < 0.9:
            console.print(f"[yellow]⚠ RED/GREEN 比例偏低 ({ratio:.1%})，确保每个 RED 后都有 GREEN[/yellow]")


@app.command()
def init(path: Path = typer.Option(Path(".tdd-state.json"), "--path", "-p", help="状态文件路径")):
    """初始化 TDD 工作流状态文件。"""
    state = {"phase": "red", "cycles": [], "files": [], "created_at": "", "thresholds": {"line": 80, "branch": 75, "function": 90}}
    save_workflow_state(path, state)
    console.print(f"[green]状态文件已创建: {path}[/green]")


if __name__ == "__main__":
    app()
