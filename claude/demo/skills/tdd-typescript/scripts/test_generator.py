#!/usr/bin/env python3
"""从 TypeScript 源码生成 Vitest 测试用例，适用于 Vue 3 + TDesign + Vite 项目。"""

from __future__ import annotations

import re
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
app = typer.Typer(help="从 TypeScript 源码生成 Vitest 测试用例")


# ── 源码解析 ──────────────────────────────────────────────

EXPORT_PATTERNS = [
    re.compile(r"export\s+(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*(\S+))?"),
    re.compile(r"export\s+(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*(?::\s*(\S+))?\s*=>"),
    re.compile(r"public\s+(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*(?::\s*(\S+))?"),
    re.compile(r"(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*(?::\s*(\S+))?\s*\{"),
]

THROW_PATTERN = re.compile(r"throw\s+(?:new\s+)?(\w+)?(?:\()?['\"](.+)['\"]")
CONDITION_PATTERN = re.compile(r"if\s*\(([^)]+)\)\s*(?:return|throw)")


def parse_functions(source: str) -> list[dict]:
    """从 TypeScript 源码中提取函数签名和逻辑信息。"""
    funcs: list[dict] = []
    lines = source.split("\n")
    current: Optional[dict] = None
    brace_depth = 0

    for i, line in enumerate(lines):
        for pat in EXPORT_PATTERNS:
            m = pat.search(line)
            if m:
                name = m.group(1)
                params = m.group(2) if m.group(2) else ""
                ret_type = m.group(3) if m.lastindex and m.lastindex >= 3 else "void"
                current = {
                    "name": name,
                    "params": [p.strip() for p in params.split(",") if p.strip()],
                    "return_type": ret_type,
                    "line": i + 1,
                    "body": [],
                    "throws": [],
                    "conditions": [],
                }
                if "class " not in line.lower():
                    funcs.append(current)
                break

        if current is not None:
            current["body"].append(line)
            brace_depth += line.count("{") - line.count("}")

            tm = THROW_PATTERN.search(line)
            if tm:
                current["throws"].append({"type": tm.group(1) or "Error", "message": tm.group(2)})

            cm = CONDITION_PATTERN.search(line)
            if cm:
                current["conditions"].append({"condition": cm.group(1), "line": i + 1})

            if brace_depth == 0:
                current = None

    return funcs


# ── 测试用例生成 ──────────────────────────────────────────

def infer_function_type(func: dict) -> str:
    """推断函数类型以决定测试策略。"""
    name = func["name"].lower()
    rt = func["return_type"].lower()
    if any(kw in name for kw in ["validate", "check", "is", "has", "can", "should"]):
        return "predicate"
    if "throw" in str(func["throws"]) or len(func["throws"]) > 0:
        return "fallible"
    if rt == "void" or rt == "undefined":
        return "side-effect"
    return "transform"


def generate_happy_path_test(func: dict) -> str:
    """生成正常路径测试用例。"""
    name = func["name"]
    params = func["params"]
    args = guess_args(func)

    if infer_function_type(func) == "predicate":
        return f"""  it('should handle valid input correctly', () => {{
    const result = {name}({", ".join(args)});
    expect(result).toBeDefined();
  }});"""

    if infer_function_type(func) == "fallible":
        return f"""  it('should not throw with valid input', () => {{
    expect(() => {name}({", ".join(args)})).not.toThrow();
  }});"""

    return f"""  it('should return expected result', () => {{
    const result = {name}({", ".join(args)});
    expect(result).toBeDefined();
  }});"""


def generate_error_tests(func: dict) -> list[str]:
    """生成错误路径测试用例。"""
    tests: list[str] = []

    for t in func["throws"]:
        tests.append(f"""  it('should throw {t["type"]} when invalid input provided', () => {{
    expect(() => {func["name"]}(/* invalid */)).toThrow('{t["message"]}');
  }});""")

    return tests


def generate_boundary_tests(func: dict) -> list[str]:
    """生成边界条件测试用例。"""
    tests: list[str] = []
    params = func["params"]

    for p in params:
        pname = p.split(":")[0].strip()
        ptype = p.split(":")[1].strip() if ":" in p else "any"

        if "string" in ptype:
            tests.append(f"""  it('should handle empty string', () => {{
    const result = {func["name"]}({', '.join("''" if x == pname else guess_single_arg(x) for x in [pp.split(":")[0].strip() for pp in params])});
    expect(result).toBeDefined();
  }});""")
        elif "number" in ptype:
            tests.append(f"""  it('should handle zero value', () => {{
    const result = {func["name"]}({', '.join("0" if x.split(":")[0].strip() == pname else guess_single_arg(x) for x in params)});
    expect(result).toBeDefined();
  }});""")
            tests.append(f"""  it('should handle negative value', () => {{
    const result = {func["name"]}({', '.join("-1" if x.split(":")[0].strip() == pname else guess_single_arg(x) for x in params)});
    expect(result).toBeDefined();
  }});""")
        elif "[]" in ptype or "Array" in ptype:
            tests.append(f"""  it('should handle empty array', () => {{
    const result = {func["name"]}({', '.join("[]" if x.split(":")[0].strip() == pname else guess_single_arg(x) for x in params)});
    expect(result).toBeDefined();
  }});""")

    return tests


def guess_args(func: dict) -> list[str]:
    """生成合理的测试参数值。"""
    args: list[str] = []
    for p in func["params"]:
        if not p:
            continue
        parts = p.split(":")
        pname = parts[0].strip()
        ptype = parts[1].strip() if len(parts) > 1 else "any"
        args.append(guess_single_arg(f"{pname}:{ptype}"))
    return args


def guess_single_arg(param: str) -> str:
    """根据参数类型猜测一个合理的测试值。"""
    parts = param.split(":")
    if len(parts) < 2:
        return "'test'"
    ptype = parts[1].strip().lower()
    mapping = {
        "string": "'test'",
        "number": "1",
        "boolean": "true",
        "string[]": "['a']",
        "number[]": "[1]",
        "object": "{}",
        "record": "{}",
        "map": "new Map()",
        "set": "new Set()",
        "void": "undefined",
        "undefined": "undefined",
        "null": "null",
        "any": "'test'",
        "unknown": "'test'",
    }
    for key, val in mapping.items():
        if key in ptype:
            return val
    return "{}"


def generate_import_line(funcs: list[dict], source_path: Optional[str]) -> str:
    """生成 vitest import 和源码 import 语句。"""
    names = sorted({f["name"] for f in funcs})
    lines = ["import { describe, it, expect } from 'vitest';"]
    if source_path:
        module = Path(source_path).stem
        lines.append(f"import {{ {', '.join(names)} }} from './{module}';")
    else:
        lines.append(f"import {{ {', '.join(names)} }} from './module';")
    return "\n".join(lines)


def generate_tests(source: str, source_path: Optional[str] = None) -> str:
    """从 TypeScript 源码生成完整 Vitest 测试文件内容。"""
    funcs = parse_functions(source)
    if not funcs:
        return "// 未检测到可测试的导出函数"

    lines: list[str] = []
    lines.append(generate_import_line(funcs, source_path))
    lines.append("")

    for func in funcs:
        lines.append(f"describe('{func['name']}', () => {{")
        lines.append(generate_happy_path_test(func))

        for t in generate_error_tests(func):
            lines.append(t)

        for t in generate_boundary_tests(func)[:4]:
            lines.append(t)

        lines.append("});")
        lines.append("")

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────

@app.command()
def generate(
    input_file: Optional[Path] = typer.Option(None, "--input", "-i", help="TypeScript 源码文件路径"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="直接粘贴 TypeScript 源码"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径，默认输出到 stdout"),
):
    """从 TypeScript 源码生成 Vitest 测试用例。"""
    if input_file and not code:
        path = Path(input_file)
        if not path.exists():
            console.print(f"[red]文件不存在: {path}[/red]")
            raise typer.Exit(1)
        source = path.read_text()
        source_path = str(path)
    elif code:
        source = code
        source_path = None
    else:
        source = sys.stdin.read()
        source_path = None

    if not source.strip():
        console.print("[red]未提供源码[/red]")
        raise typer.Exit(1)

    result = generate_tests(source, source_path)

    if output:
        output.write_text(result)
        console.print(f"[green]测试文件已生成: {output}[/green]")
    else:
        console.print(Panel(result, title="生成的测试 (vitest)", border_style="green"))


@app.command()
def analyze(input_file: Path = typer.Argument(..., help="TypeScript 源码文件路径")):
    """分析 TypeScript 源码，输出函数和分支概览。"""
    source = input_file.read_text()
    funcs = parse_functions(source)

    table = Table(title=f"函数分析 — {input_file.name}")
    table.add_column("函数", style="cyan")
    table.add_column("参数", style="yellow")
    table.add_column("类型", style="magenta")
    table.add_column("异常", style="red")
    table.add_column("分支", style="green")

    for func in funcs:
        table.add_row(
            func["name"],
            ", ".join(func["params"]) if func["params"] else "无",
            infer_function_type(func),
            str(len(func["throws"])),
            str(len(func["conditions"])),
        )

    console.print(table)


if __name__ == "__main__":
    app()
