#!/usr/bin/env python3
"""
测试桩生成器 - 从 Java 源码分析并生成 JUnit 5 测试桩。

注意：生成的测试桩不等于测试。真正写测试必须走 TDD 铁律流程。
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


def parse_java_class(source: str) -> dict:
    """解析 Java 类的基本结构。"""
    result = {
        "package": "",
        "imports": [],
        "class_name": "",
        "methods": [],
        "fields": [],
    }

    # 提取 package
    pkg_match = re.search(r"package\s+([\w.]+)\s*;", source)
    if pkg_match:
        result["package"] = pkg_match.group(1)

    # 提取 imports
    result["imports"] = re.findall(r"import\s+([\w.*]+)\s*;", source)

    # 提取类名
    class_match = re.search(r"(?:public\s+)?class\s+(\w+)", source)
    if class_match:
        result["class_name"] = class_match.group(1)

    # 提取方法签名
    method_pattern = r"(?:public|protected|private)\s+(?:static\s+)?(?:[\w<>,.\s\[\]]+)\s+(\w+)\s*\([^)]*\)"
    for m in re.finditer(method_pattern, source):
        result["methods"].append(m.group(1))

    # 提取字段
    field_pattern = r"(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?([\w<>,.\s\[\]]+)\s+(\w+)\s*;"
    for m in re.finditer(field_pattern, source):
        result["fields"].append({"type": m.group(1).strip(), "name": m.group(2)})

    return result


def generate_import_line() -> str:
    """生成 JUnit 5 import。"""
    return "\n".join([
        "import org.junit.jupiter.api.Test;",
        "import org.junit.jupiter.api.BeforeEach;",
        "import org.junit.jupiter.api.extension.ExtendWith;",
        "import org.mockito.junit.jupiter.MockitoExtension;",
        "import org.mockito.Mock;",
        "import org.mockito.InjectMocks;",
        "import static org.junit.jupiter.api.Assertions.*;",
        "import static org.mockito.Mockito.*;",
        "import static org.assertj.core.api.Assertions.*;",
    ])


def generate_test_class(class_name: str, methods: list[str], pkg: str) -> str:
    """生成测试类骨架。"""
    lines = []
    lines.append(f"package {pkg};" if pkg else "")
    lines.append("")
    lines.append(generate_import_line())
    lines.append("")
    lines.append(f"@ExtendWith(MockitoExtension.class)")
    lines.append(f"class {class_name}Test {{")
    lines.append("")
    lines.append(f"    @InjectMocks")
    lines.append(f"    private {class_name} target;")
    lines.append("")

    for method in methods:
        test_name = _method_to_test_name(method)
        lines.append(f"    @Test")
        lines.append(f"    void {test_name}() {{")
        lines.append(f"        // TODO: write failing test first (TDD RED)")
        lines.append(f"        fail(\"Not yet implemented\");")
        lines.append(f"    }}")
        lines.append("")

    lines.append("}")
    return "\n".join(lines)


def generate_happy_path_test(class_name: str, method: str, pkg: str) -> str:
    """为 happy path 生成测试桩。"""
    test_name = _method_to_test_name(method)
    return f"""@Test
void {test_name}() {{
    // Given: 正常输入
    // TODO: 准备测试数据

    // When: 调用被测方法
    // var result = target.{method}(...)

    // Then: 验证预期结果
    fail("Not yet implemented — write this test first (TDD RED)");
}}"""


def generate_error_tests(class_name: str, method: str, pkg: str) -> str:
    """为错误场景生成测试桩。"""
    return f"""@Test
void shouldThrowException_when{method.capitalize()}WithInvalidInput() {{
    // Given: 非法输入（null / 空值 / 越界）
    // TODO: 准备非法测试数据

    // When / Then: 应抛出异常
    // assertThrows(IllegalArgumentException.class, () -> target.{method}(...));
    fail("Not yet implemented — write this test first (TDD RED)");
}}

@Test
void shouldThrowException_when{method.capitalize()}WithNullInput() {{
    // Given: null 输入
    // When / Then: 应抛出异常
    // assertThrows(NullPointerException.class, () -> target.{method}(null));
    fail("Not yet implemented — write this test first (TDD RED)");
}}"""


def generate_boundary_tests(class_name: str, method: str, pkg: str) -> str:
    """为边界场景生成测试桩。"""
    return f"""@Test
void shouldHandleEmpty_when{method.capitalize()}() {{
    // Given: 空集合 / 空字符串
    // When: 调用方法
    // Then: 返回空结果而非 NPE
    fail("Not yet implemented — write this test first (TDD RED)");
}}

@Test
void shouldHandleMaxValue_when{method.capitalize()}() {{
    // Given: 边界值 / 最大值
    // When: 调用方法
    // Then: 正常处理不溢出
    fail("Not yet implemented — write this test first (TDD RED)");
}}"""


def _method_to_test_name(method: str) -> str:
    """将方法名转换为测试方法名。"""
    if method.startswith("get") or method.startswith("set"):
        return f"should{method.capitalize()}"
    return f"should{method[0].upper() + method[1:]}"


def detect_framework_from_config() -> str:
    """检测框架配置 — 固定返回 junit5。"""
    return "junit5"


def generate_service_test(class_name: str, methods: list[str], fields: list[dict], pkg: str) -> str:
    """生成 Service 层测试（@ExtendWith + @Mock + @InjectMocks）。"""
    field_mocks = []
    for f in fields:
        type_name = f["type"]
        name = f["name"]
        field_mocks.append(f"    @Mock\n    private {type_name} {name};")

    test_methods = []
    for method in methods:
        if method in ("equals", "hashCode", "toString", "getClass"):
            continue
        test_name = _method_to_test_name(method)
        test_methods.append(f"""    @Test
    void {test_name}() {{
        // TODO: TDD RED — write this failing test first
        fail("Not yet implemented");
    }}""")

    return f"""package {pkg};

{generate_import_line()}

@ExtendWith(MockitoExtension.class)
class {class_name}Test {{

{chr(10).join(field_mocks)}

    @InjectMocks
    private {class_name} target;

    @BeforeEach
    void setUp() {{
        // Mock 准备
    }}

{chr(10).join(test_methods)}
}}"""


@app.command()
def generate(
    input_text: Optional[str] = typer.Option(None, "--input", "-i", help="Java 源代码文件路径或粘贴内容"),
    source_file: Optional[Path] = typer.Option(None, "--file", "-f", help="Java 源文件路径"),
    include_boundary: bool = typer.Option(True, "--boundary/--no-boundary", help="是否包含边界测试（BCDE-B 原则）"),
    include_error: bool = typer.Option(True, "--error/--no-error", help="是否包含错误场景测试（BCDE-E 原则）"),
):
    """
    从 Java 源码生成 JUnit 5 测试桩。
    注意：生成的桩不等于测试，真正写测试必须走 TDD 铁律流程。
    """
    console.print(Panel.fit("[bold blue]TDD Java — 测试桩生成器[/bold blue]"))

    if source_file:
        source = source_file.read_text(encoding="utf-8")
    elif input_text:
        source = input_text
    else:
        source = sys.stdin.read()

    if not source.strip():
        console.print("[red]错误: 未提供 Java 源代码。请用 --input 或 --file 提供。[/red]")
        raise typer.Exit(code=1)

    info = parse_java_class(source)

    if not info["class_name"]:
        console.print("[red]错误: 未能从源码中解析出类名。[/red]")
        raise typer.Exit(code=1)

    console.print(f"类名: [green]{info['class_name']}[/green]")
    console.print(f"方法数: [green]{len(info['methods'])}[/green]")
    console.print(f"字段数: [green]{len(info['fields'])}[/green]")

    if info["fields"]:
        # Service/Component 类 → 带 Mock 的测试
        result = generate_service_test(
            info["class_name"], info["methods"], info["fields"],
            info["package"]
        )
    else:
        # 工具类 → 纯测试
        result = generate_test_class(
            info["class_name"], info["methods"], info["package"]
        )

    console.print("\n[bold]生成的测试桩:[/bold]")
    console.print(Panel(result, title=f"{info['class_name']}Test.java"))

    console.print(
        "\n[yellow]⚠️  这只是一个测试桩。请按照 TDD 铁律重写测试:[/yellow]\n"
        "  1. 写一个最小失败测试\n"
        "  2. 亲眼看到它失败\n"
        "  3. 写最小实现让它通过\n"
        "  4. 亲眼看到它通过"
    )


@app.command()
def version():
    """显示版本信息。"""
    console.print("tdd-java test_generator v1.0.0")


if __name__ == "__main__":
    app()
