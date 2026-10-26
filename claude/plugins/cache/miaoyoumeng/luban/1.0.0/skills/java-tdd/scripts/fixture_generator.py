#!/usr/bin/env python3
"""
夹具生成器 - 从 Java Entity/DTO 类生成测试夹具（mock 数据对象）。

支持:
  - 从 entity/DTO 源码解析字段并生成 Builder 式构建方法
  - 边界值生成（BCDE-B）
  - 边缘场景数据
"""
import re
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()


def parse_java_fields(source: str) -> list[dict]:
    """解析 Java 类的字段定义。"""
    fields = []
    pattern = r"(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?([\w<>,.\s\[\]]+?)\s+(\w+)\s*;"
    for m in re.finditer(pattern, source):
        type_str = m.group(1).strip()
        name = m.group(2)
        java_type = _normalize_type(type_str)
        fields.append({"name": name, "type": type_str, "java_type": java_type})
    return fields


def _normalize_type(type_str: str) -> str:
    """规范化类型名用于方法名。"""
    type_str = type_str.strip()
    if "<" in type_str:
        type_str = type_str.split("<")[0]
    if type_str == "String":
        return "String"
    if type_str in ("Long", "long"):
        return "Long"
    if type_str in ("Integer", "int"):
        return "Integer"
    if type_str in ("Boolean", "boolean"):
        return "Boolean"
    if type_str in ("Double", "double"):
        return "Double"
    if type_str in ("BigDecimal",):
        return "BigDecimal"
    if type_str in ("LocalDateTime", "LocalDate", "LocalTime"):
        return "LocalDateTime"
    return type_str


def generate_default_value(field: dict) -> str:
    """根据字段类型生成默认测试值。"""
    name = field["name"].lower()
    jtype = field["java_type"]

    # 按字段名推断
    if "id" == name:
        return "1L"
    if "name" in name:
        return '"TestName"'
    if "email" in name:
        return '"test@example.com"'
    if "phone" in name or "mobile" in name:
        return '"13800138000"'
    if "status" in name:
        return "1"
    if "password" in name or "pwd" in name:
        return '"password123"'
    if "url" in name or "link" in name:
        return '"https://example.com"'
    if "time" in name or "date" in name:
        return "LocalDateTime.now()"

    # 按类型
    type_defaults = {
        "String": '""',
        "Long": "1L",
        "Integer": "1",
        "Boolean": "true",
        "Double": "1.0",
        "BigDecimal": "new BigDecimal(\"1.00\")",
        "LocalDateTime": "LocalDateTime.now()",
        "LocalDate": "LocalDate.now()",
        "LocalTime": "LocalTime.now()",
    }
    return type_defaults.get(jtype, "null")


def generate_mock_for_entity(entity_name: str, fields: list[dict], pkg: str) -> str:
    """生成 Builder 模式的测试数据构建方法。"""
    lines = []
    lines.append(f"// {entity_name} 测试夹具")
    lines.append(f"public class {entity_name}Fixture {{")
    lines.append("")

    # 正常数据
    lines.append(f"    public static {entity_name} a{entity_name}() {{")
    lines.append(f"        {entity_name} entity = new {entity_name}();")
    for f in fields:
        lines.append(f"        entity.set{_capitalize(f['name'])}({generate_default_value(f)});")
    lines.append(f"        return entity;")
    lines.append(f"    }}")
    lines.append("")

    # 空数据
    lines.append(f"    public static {entity_name} anEmpty{entity_name}() {{")
    lines.append(f"        return new {entity_name}();")
    lines.append(f"    }}")
    lines.append("")

    # 列表
    lines.append(f"    public static List<{entity_name}> {_decapitalize(entity_name)}List(int count) {{")
    lines.append(f"        List<{entity_name}> list = new ArrayList<>();")
    lines.append(f"        for (int i = 0; i < count; i++) {{")
    lines.append(f"            {entity_name} entity = a{entity_name}();")
    lines.append(f"            entity.setId((long) (i + 1));")
    lines.append(f"            list.add(entity);")
    lines.append(f"        }}")
    lines.append(f"        return list;")
    lines.append(f"    }}")
    lines.append("")

    # 边界值数据
    for f in fields:
        jtype = f["java_type"]
        if jtype == "String":
            lines.append(f"    // 边界值 (BCDE-B)")
            lines.append(f"    public static {entity_name} a{entity_name}WithNull{_capitalize(f['name'])}() {{")
            lines.append(f"        {entity_name} entity = a{entity_name}();")
            lines.append(f"        entity.set{_capitalize(f['name'])}(null);")
            lines.append(f"        return entity;")
            lines.append(f"    }}")
            lines.append("")
            lines.append(f"    public static {entity_name} a{entity_name}WithEmpty{_capitalize(f['name'])}() {{")
            lines.append(f"        {entity_name} entity = a{entity_name}();")
            lines.append(f"        entity.set{_capitalize(f['name'])}('\"\"');")
            lines.append(f"        return entity;")
            lines.append(f"    }}")
            break

    # 错误数据
    for f in fields:
        if "email" in f["name"].lower():
            lines.append(f"    // 错误数据 (BCDE-E)")
            lines.append(f"    public static {entity_name} a{entity_name}WithInvalidEmail() {{")
            lines.append(f"        {entity_name} entity = a{entity_name}();")
            lines.append(f"        entity.set{_capitalize(f['name'])}('\"invalid-email\"');")
            lines.append(f"        return entity;")
            lines.append(f"    }}")
            break

    lines.append("}")
    return "\n".join(lines)


def generate_mockito_fixture(entity_name: str, fields: list[dict]) -> str:
    """生成 Mockito mock 模板。"""
    lines = []
    lines.append(f"// Mockito Mock 模板")
    lines.append(f"@Mock")
    lines.append(f"private {entity_name} mock{entity_name};")
    lines.append("")
    for f in fields:
        lines.append(f"// when(mock{entity_name}.get{_capitalize(f['name'])}()).thenReturn({generate_default_value(f)});")
    return "\n".join(lines)


def _capitalize(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def _decapitalize(s: str) -> str:
    return s[0].lower() + s[1:] if s else s


@app.command()
def generate(
    input_text: Optional[str] = typer.Option(None, "--input", "-i", help="Java Entity/DTO 源码路径或粘贴内容"),
    source_file: Optional[Path] = typer.Option(None, "--file", "-f", help="Java Entity/DTO 源文件路径"),
    count: int = typer.Option(5, "--count", "-c", help="生成列表时的默认数量"),
):
    """
    从 Java Entity/DTO 生成测试夹具。
    """
    console.print(Panel.fit("[bold blue]TDD Java — 夹具生成器[/bold blue]"))

    if source_file:
        source = source_file.read_text(encoding="utf-8")
    elif input_text:
        source = input_text
    else:
        source = sys.stdin.read()

    if not source.strip():
        console.print("[red]错误: 未提供 Java 源码。[/red]")
        raise typer.Exit(code=1)

    fields = parse_java_fields(source)
    if not fields:
        console.print("[yellow]警告: 未从源码中解析出字段。[/yellow]")
        raise typer.Exit(code=0)

    # 提取类名
    class_match = re.search(r"class\s+(\w+)", source)
    entity_name = class_match.group(1) if class_match else "UnknownEntity"

    # 提取包名
    pkg_match = re.search(r"package\s+([\w.]+)\s*;", source)
    pkg = pkg_match.group(1) if pkg_match else ""

    console.print(f"类名: [green]{entity_name}[/green]")
    console.print(f"字段数: [green]{len(fields)}[/green]")

    console.print("\n[bold]字段列表:[/bold]")
    for f in fields:
        console.print(f"  {f['type']:30s} {f['name']}")

    fixture = generate_mock_for_entity(entity_name, fields, pkg)
    console.print(f"\n[bold]生成的夹具 (Fixture):[/bold]")
    console.print(Panel(fixture, title=f"{entity_name}Fixture.java"))

    mockito_fixture = generate_mockito_fixture(entity_name, fields)
    console.print(f"\n[bold]Mockito Mock 模板:[/bold]")
    console.print(Panel(mockito_fixture, title="Mockito Template"))

    console.print(
        "\n[yellow]注意: 生成的夹具是辅助工具。[/yellow]\n"
        "  - BCDE-B 边界值数据已生成\n"
        "  - BCDE-E 错误数据已生成\n"
        "  - BCDE-C 正确输入已生成\n"
        "  - 真正写测试仍须走 TDD 铁律流程"
    )


@app.command()
def version():
    """显示版本信息。"""
    console.print("tdd-java fixture_generator v1.0.0")


if __name__ == "__main__":
    app()
