#!/usr/bin/env python3
"""为 TypeScript + Vue 3 + TDesign 测试生成 Vitest 夹具数据、mock 对象和边界值。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.syntax import Syntax

console = Console()
app = typer.Typer(help="生成 Vitest 测试夹具和 mock 数据")


INTERFACE_PATTERN = re.compile(r"(?:export\s+)?interface\s+(\w+)\s*\{([^}]*)\}", re.DOTALL)
TYPE_PATTERN = re.compile(r"(?:export\s+)?type\s+(\w+)\s*=\s*\{([^}]*)\}", re.DOTALL)
PROP_PATTERN = re.compile(r"(\w+)\??\s*:\s*([^;]+?)(?:;|$)")


def parse_entity(source: str) -> list[dict]:
    """从 TypeScript 源码提取 interface/type 定义。"""
    entities: list[dict] = []

    for pat in (INTERFACE_PATTERN, TYPE_PATTERN):
        for m in pat.finditer(source):
            name = m.group(1)
            body = m.group(2)
            props: list[dict] = []
            for pm in PROP_PATTERN.finditer(body):
                prop_name = pm.group(1)
                prop_type = pm.group(2).strip()
                optional = "?" in pm.group(0)
                props.append({"name": prop_name, "type": prop_type, "optional": optional})
            entities.append({"name": name, "props": props})

    return entities


def guess_fixture_value(prop_type: str, prop_name: str) -> str:
    """根据属性类型和名称生成合理的测试夹具值。"""
    t = prop_type.lower().replace(" ", "")
    name = prop_name.lower()

    name_hints = {
        "id": "'uuid-1'",
        "uuid": "'550e8400-e29b-41d4-a716-446655440000'",
        "email": "'test@example.com'",
        "name": "'Test User'",
        "username": "'testuser'",
        "password": "'hashed-password'",
        "token": "'eyJhbGciOiJIUzI1NiJ9.xxx'",
        "url": "'https://example.com'",
        "phone": "'+86-13800138000'",
        "address": "'123 Main St'",
        "city": "'Beijing'",
        "country": "'CN'",
        "zip": "'100000'",
        "title": "'Test Title'",
        "description": "'A test description'",
        "body": "'Content body text'",
        "message": "'A test message'",
        "status": "'active'",
        "role": "'user'",
        "type": "'default'",
        "currency": "'CNY'",
        "timestamp": "Date.now()",
        "createdat": "new Date()",
        "updatedat": "new Date()",
        "date": "new Date('2026-01-01')",
    }
    if name in name_hints:
        return name_hints[name]

    if t == "string":
        return "'test-string'"
    if t == "number":
        return "1"
    if t == "boolean":
        return "true"
    if t in ("string[]", "array<string>"):
        return "['a', 'b']"
    if t in ("number[]", "array<number>"):
        return "[1, 2]"
    if t.startswith("record<"):
        return "{}"
    if t.startswith("map<"):
        return "new Map()"
    if t.startswith("set<"):
        return "new Set()"
    if t in ("void", "undefined"):
        return "undefined"
    if t == "null":
        return "null"
    if t in ("any", "unknown"):
        return "{}"
    if t == "date":
        return "new Date()"
    if t == "regexp":
        return "/test/"
    if "promise" in t:
        return "Promise.resolve()"
    return "{}"


def generate_fixture(entity: dict, count: int) -> str:
    """生成 TypeScript 夹具对象数组。"""
    lines: list[str] = []
    lines.append(f"import type {{ {entity['name']} }} from './types';")
    lines.append("")

    if count == 1:
        lines.append(f"export const mock{entity['name']}: {entity['name']} = {{")
        for prop in entity["props"]:
            val = guess_fixture_value(prop["type"], prop["name"])
            lines.append(f"  {prop['name']}: {val},")
        lines.append("};")
    else:
        lines.append(f"export function createMock{entity['name']}(")
        lines.append(f"  overrides?: Partial<{entity['name']}>")
        lines.append(f"): {entity['name']} {{")
        lines.append("  return {")
        for prop in entity["props"]:
            val = guess_fixture_value(prop["type"], prop["name"])
            lines.append(f"    {prop['name']}: {val},")
        lines.append("    ...overrides,")
        lines.append("  };")
        lines.append("}")
        lines.append("")

        lines.append(f"export function createMock{entity['name']}List(count: number): {entity['name']}[] {{")
        lines.append(f"  return Array.from({{ length: count }}, (_, i) => createMock{entity['name']}({{")
        if any(p["name"] == "id" for p in entity["props"]):
            lines.append("    id: `id-${i}`,")
        lines.append("  }));")
        lines.append("}")

    return "\n".join(lines)


def generate_edge_cases(entity: dict) -> str:
    """为实体生成边界值测试数据。"""
    lines: list[str] = []
    lines.append(f"// 边界值测试数据 — {entity['name']}")
    lines.append(f"export const {entity['name'].lower()}EdgeCases = {{")

    for prop in entity["props"]:
        t = prop["type"].lower().replace(" ", "")
        pname = prop["name"]

        if "string" in t:
            lines.append(f"  // {pname}")
            lines.append(f"  {pname}Empty: '',")
            lines.append(f"  {pname}Long: 'a'.repeat(1000),")
            lines.append(f"  {pname}Unicode: '中文测试',")
            lines.append(f"  {pname}Special: '<script>alert(\"xss\")</script>',")
        elif "number" in t:
            lines.append(f"  // {pname}")
            lines.append(f"  {pname}Zero: 0,")
            lines.append(f"  {pname}Negative: -1,")
            lines.append(f"  {pname}MaxSafe: Number.MAX_SAFE_INTEGER,")
            lines.append(f"  {pname}MinSafe: Number.MIN_SAFE_INTEGER,")
        elif "boolean" in t:
            lines.append(f"  {pname}True: true,")
            lines.append(f"  {pname}False: false,")

    lines.append("};")
    return "\n".join(lines)


def generate_mock_for_entity(entity: dict) -> str:
    """为实体生成 vi.fn() mock。"""
    name = entity["name"]
    lines = [f"export const mock{name} = {{"]
    for prop in entity["props"]:
        t = prop["type"].lower()
        if "()" in prop["type"] or "=>" in prop["type"]:
            lines.append(f"  {prop['name']}: vi.fn(),")
        else:
            val = guess_fixture_value(prop["type"], prop["name"])
            lines.append(f"  {prop['name']}: {val},")
    lines.append("};")
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────

@app.command()
def fixture(
    entity: str = typer.Option(..., "--entity", "-e", help="实体名称（interface/type 名）"),
    count: int = typer.Option(1, "--count", "-n", help="生成夹具数量"),
    source: Optional[Path] = typer.Option(None, "--source", "-s", help="TypeScript 类型定义文件"),
    props: Optional[str] = typer.Option(None, "--props", "-p", help="手动指定属性: name:string,age:number"),
):
    """生成测试夹具对象。"""
    entity_def: dict = {"name": entity, "props": []}

    if source:
        content = source.read_text()
        entities = parse_entity(content)
        found = next((e for e in entities if e["name"] == entity), None)
        if found:
            entity_def = found
        else:
            console.print(f"[yellow]未找到 {entity} 的类型定义，使用空 schema[/yellow]")
    elif props:
        for part in props.split(","):
            part = part.strip()
            if ":" in part:
                pname, ptype = part.split(":", 1)
                entity_def["props"].append({"name": pname.strip(), "type": ptype.strip(), "optional": "?" in pname})

    if not entity_def["props"]:
        console.print("[yellow]未提供属性定义，生成空夹具[/yellow]")

    result = generate_fixture(entity_def, count)
    console.print(Syntax(result, "typescript", theme="monokai", line_numbers=False))


@app.command()
def edge(
    entity: str = typer.Option(..., "--entity", "-e", help="实体名称"),
    source: Optional[Path] = typer.Option(None, "--source", "-s", help="TypeScript 类型定义文件"),
    props: Optional[str] = typer.Option(None, "--props", "-p", help="手动指定属性"),
):
    """生成边界值测试数据。"""
    entity_def: dict = {"name": entity, "props": []}

    if source:
        content = source.read_text()
        entities = parse_entity(content)
        found = next((e for e in entities if e["name"] == entity), None)
        if found:
            entity_def = found
    elif props:
        for part in props.split(","):
            part = part.strip()
            if ":" in part:
                pname, ptype = part.split(":", 1)
                entity_def["props"].append({"name": pname.strip(), "type": ptype.strip(), "optional": "?" in pname})

    result = generate_edge_cases(entity_def)
    console.print(Syntax(result, "typescript", theme="monokai", line_numbers=False))


@app.command()
def mock(
    entity: str = typer.Option(..., "--entity", "-e", help="实体名称"),
    source: Optional[Path] = typer.Option(None, "--source", "-s", help="TypeScript 类型定义文件"),
    props: Optional[str] = typer.Option(None, "--props", "-p", help="手动指定属性"),
):
    """生成 vi.fn() mock 对象。"""
    entity_def: dict = {"name": entity, "props": []}

    if source:
        content = source.read_text()
        entities = parse_entity(content)
        found = next((e for e in entities if e["name"] == entity), None)
        if found:
            entity_def = found
    elif props:
        for part in props.split(","):
            part = part.strip()
            if ":" in part:
                pname, ptype = part.split(":", 1)
                entity_def["props"].append({"name": pname.strip(), "type": ptype.strip(), "optional": "?" in pname})

    result = generate_mock_for_entity(entity_def)
    console.print(Syntax(result, "typescript", theme="monokai", line_numbers=False))


@app.command()
def analyze(source: Path = typer.Argument(..., help="TypeScript 类型定义文件")):
    """列出文件中所有可生成夹具的类型/接口。"""
    content = source.read_text()
    entities = parse_entity(content)

    if not entities:
        console.print("[yellow]未找到 interface 或 type 定义[/yellow]")
        return

    for e in entities:
        console.print(f"[cyan]{e['name']}[/cyan] ({len(e['props'])} 个属性)")
        for p in e["props"]:
            opt = "?" if p["optional"] else " "
            console.print(f"  {opt} [yellow]{p['name']}[/yellow]: [green]{p['type']}[/green]")


if __name__ == "__main__":
    app()
