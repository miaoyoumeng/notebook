#!/usr/bin/env python3
"""
TDD 工作流引导器 - 引导 Red-Green-Refactor 循环，验证阶段完成条件。

强制验证：
  RED: 必须亲眼看到测试失败
  GREEN: 必须亲眼看到测试通过，其他测试依然通过
  REFACTOR: 每次小重构后必须重新运行测试
"""
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()


class Phase(str, Enum):
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"


RED_CHECKLIST = """
[bold]RED 阶段 — 写失败测试[/bold]

检查清单:
  1. [ ] 写一个最小测试，描述期望行为
  2. [ ] 测试名清晰（should<行为>_when<条件>）
  3. [ ] 一个测试一个行为
  4. [ ] 使用真实代码（mock 只在不可避免时）
"""

RED_VERIFY = """
[bold]验证 RED [/bold]

运行测试:
  [cyan]mvn test -Dtest={test_name}[/cyan]

确认:
  - 测试 [red]失败[/red]（不是编译报错）— 编译失败也是测试失败
  - 失败信息符合预期
  - 失败原因: [red]功能缺失[/red]（不是语法/导入/配置错误）

  测试通过了？你测的是已存在行为 → 修测试
  测试报错了？修错误 → 重新运行直到 [red]正确地失败[/red]
"""

GREEN_CHECKLIST = """
[bold]GREEN 阶段 — 最小实现[/bold]

检查清单:
  1. [ ] 写最简代码让测试通过
  2. [ ] 不添加功能
  3. [ ] 不重构其他代码
  4. [ ] 不"改进"超出测试范围的东西
  5. [ ] 临时重复代码可接受
"""

GREEN_VERIFY = """
[bold]验证 GREEN [/bold]

运行测试:
  [cyan]mvn test -Dtest={test_name}[/cyan]

确认:
  - 测试 [green]通过[/green]
  - [green]其他测试依然通过[/green]
  - [green]输出干净[/green]（无 error、无 warning）

  测试失败？修代码，不要修测试
  其他测试失败？立即修复
"""

REFACTOR_CHECKLIST = """
[bold]REFACTOR 阶段 — 清理[/bold]

检查清单:
  1. [ ] 消除重复代码
  2. [ ] 改进命名
  3. [ ] 提取 helper 方法/类
  4. [ ] 每次小重构后运行测试: [cyan]mvn test[/cyan]
  5. [ ] 保持测试 [green]绿色[/green]
  6. [ ] 不要添加行为
"""


@app.command()
def phase(
    stage: Phase = typer.Argument(..., help="TDD 阶段: red / green / refactor"),
    test_name: str = typer.Option("XxxTest", "--test", "-t", help="测试类名"),
    module: Optional[str] = typer.Option(None, "--module", "-m", help="Maven 模块路径"),
):
    """
    引导 TDD 工作流的单个阶段。
    """
    console.print(Panel.fit("[bold blue]TDD Java — 工作流引导[/bold blue]"))

    module_flag = f" -pl {module}" if module else ""

    if stage == Phase.RED:
        console.print(RED_CHECKLIST)
        console.print(RED_VERIFY.format(test_name=test_name))

        console.print(f"\n[bold]运行命令:[/bold]")
        console.print(f"  [cyan]mvn test -Dtest={test_name}{module_flag}[/cyan]")

        console.print(f"\n[bold]Maven Surefire 配置检查:[/bold]")
        console.print("  确保 pom.xml 中: <argLine>${{'{'}}jacocoArgLine{'}'}}</argLine>")

    elif stage == Phase.GREEN:
        console.print(GREEN_CHECKLIST)
        console.print(GREEN_VERIFY.format(test_name=test_name))

        console.print(f"\n[bold]运行命令:[/bold]")
        console.print(f"  [cyan]mvn test -Dtest={test_name}{module_flag}[/cyan]")

    elif stage == Phase.REFACTOR:
        console.print(REFACTOR_CHECKLIST)

        console.print(f"\n[bold]运行命令:[/bold]")
        console.print(f"  [cyan]mvn test{module_flag}[/cyan]")


@app.command()
def full_cycle(
    test_name: str = typer.Option(..., "--test", "-t", help="测试类名"),
    module: Optional[str] = typer.Option(None, "--module", "-m", help="Maven 模块路径"),
):
    """
    引导完整的 Red-Green-Refactor 循环。
    """
    console.print(Panel.fit("[bold blue]TDD Java — 完整循环[/bold blue]"))

    console.print("[bold]Step 1: RED[/bold]")
    console.print(RED_CHECKLIST)
    console.print(RED_VERIFY.format(test_name=test_name))
    console.print(f"  运行: [cyan]mvn test -Dtest={test_name}[/cyan]")
    console.print("\n  ⏸  看到测试失败后，按任意键进入 GREEN...")

    console.print("\n[bold]Step 2: GREEN[/bold]")
    console.print(GREEN_CHECKLIST)
    console.print(GREEN_VERIFY.format(test_name=test_name))
    console.print(f"  运行: [cyan]mvn test -Dtest={test_name}[/cyan]")
    console.print("\n  ⏸  看到测试通过后，按任意键进入 REFACTOR...")

    console.print("\n[bold]Step 3: REFACTOR[/bold]")
    console.print(REFACTOR_CHECKLIST)
    console.print(f"  运行: [cyan]mvn test[/cyan]")
    console.print("\n  ⏸  重构完成，进入下一个 RED...")


@app.command()
def verify(
    phase_name: Phase = typer.Argument(..., help="要验证的阶段: red / green / refactor"),
    test_name: str = typer.Option(..., "--test", "-t", help="测试类名"),
    module: Optional[str] = typer.Option(None, "--module", "-m", help="Maven 模块路径"),
):
    """
    验证当前阶段是否满足完成条件。
    """
    console.print(Panel.fit(f"[bold blue]TDD Java — 验证: {phase_name.value.upper()}[/bold blue]"))

    module_flag = f" -pl {module}" if module else ""

    if phase_name == Phase.RED:
        console.print("[bold]RED 完成条件:[/bold]")
        console.print("  ✅ 测试文件存在")
        console.print("  ✅ 测试编译通过（mvn test-compile 成功）")
        console.print("  ✅ 测试因功能缺失而失败")
        console.print(f"\n  运行: [cyan]mvn test -Dtest={test_name}{module_flag}[/cyan]")
        console.print("  检查失败原因是否因 [red]功能缺失[/red]")

    elif phase_name == Phase.GREEN:
        console.print("[bold]GREEN 完成条件:[/bold]")
        console.print("  ✅ 新增测试通过")
        console.print("  ✅ 其他测试依然通过")
        console.print("  ✅ 输出干净（无 error/warning）")
        console.print(f"\n  运行: [cyan]mvn test -Dtest={test_name}{module_flag}[/cyan]")
        console.print("  然后运行: [cyan]mvn test{module_flag}[/cyan] 确认全部通过")

    elif phase_name == Phase.REFACTOR:
        console.print("[bold]REFACTOR 完成条件:[/bold]")
        console.print("  ✅ 重复代码已消除")
        console.print("  ✅ 命名已改进")
        console.print("  ✅ 所有测试依然通过")
        console.print("  ✅ 未添加新行为")
        console.print(f"\n  运行: [cyan]mvn test{module_flag}[/cyan]")


@app.command()
def checklist():
    """
    显示最终验证清单。
    """
    console.print(Panel.fit("[bold blue]TDD Java — 最终验证清单[/bold blue]"))

    items = [
        ("每个新方法都有测试", False),
        ("亲眼看过每个测试失败", False),
        ("每个测试因预期原因失败（功能缺失，不是语法错误）", False),
        ("为每个测试写最小代码通过", False),
        ("所有测试通过", False),
        ("输出干净（无 error、无 warning）", False),
        ("测试用真实代码（mock 只在不可避免时使用）", False),
        ("边界场景和错误已覆盖（BCDE）", False),
        ("测试是自动化的（不用 System.out 人肉验收）", False),
        ("测试是独立的（不依赖执行顺序）", False),
        ("测试是可重复的（每次结果一致）", False),
    ]

    for item, _ in items:
        console.print(f"  [ ] {item}")

    console.print("\n[yellow]不能全打勾？你跳过了 TDD。从头开始。[/yellow]")


@app.command()
def version():
    """显示版本信息。"""
    console.print("tdd-java tdd_workflow v1.0.0")


if __name__ == "__main__":
    app()
