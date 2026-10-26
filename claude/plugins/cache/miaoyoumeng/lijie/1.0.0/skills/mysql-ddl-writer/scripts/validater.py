#!/usr/bin/env python3
"""校验 MySQL DDL 是否符合 mysql-ddl-writer 约定。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import sqlparse

REQUIRED_COLUMNS: dict[str, dict[str, object]] = {
    "id": {
        "type": "BIGINT",
        "flags": ("UNSIGNED", "NOT NULL", "AUTO_INCREMENT"),
    },
    "is_deleted": {
        "type": "TINYINT",
        "flags": ("NOT NULL",),
        "default": "0",
    },
    "created_at": {
        "type": "DATETIME",
        "flags": ("NOT NULL",),
        "default": "CURRENT_TIMESTAMP",
    },
    "updated_at": {
        "type": "DATETIME",
        "flags": ("NOT NULL",),
        "default": "CURRENT_TIMESTAMP",
        "on_update": "CURRENT_TIMESTAMP",
    },
}

FORBIDDEN_TYPES = ("FLOAT", "DOUBLE", "ENUM")
NON_COLUMN_PREFIXES = (
    "PRIMARY KEY",
    "UNIQUE KEY",
    "UNIQUE INDEX",
    "KEY",
    "INDEX",
    "CONSTRAINT",
    "FOREIGN KEY",
    "FULLTEXT",
    "SPATIAL",
    "CHECK",
)

COLUMN_RE = re.compile(r"^`?([A-Za-z_][A-Za-z0-9_]*)`?\s+([A-Za-z]+)")
CREATE_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?([A-Za-z_][A-Za-z0-9_]*)`?",
    re.IGNORECASE,
)
IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def split_top_level(body: str) -> list[str]:
    """按顶层逗号切分表体，忽略括号内的逗号。"""
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for char in body:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current).strip())
    return [part for part in parts if part]


def find_body(statement: str, start: int) -> tuple[str, int] | None:
    """返回表体内容与右括号位置。"""
    depth = 0
    for index in range(start, len(statement)):
        char = statement[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return statement[start + 1 : index], index
    return None


def parse_columns(body: str) -> dict[str, str]:
    """解析字段定义，保留原始字段名。"""
    columns: dict[str, str] = {}
    for part in split_top_level(body):
        normalized = " ".join(part.split())
        if normalized.upper().startswith(NON_COLUMN_PREFIXES):
            continue
        match = COLUMN_RE.match(normalized)
        if match:
            columns[match.group(1)] = normalized
    return columns


def validate_table(table: str, statement: str) -> list[str]:
    """校验单张表的字段、命名、注释与表选项。"""
    errors: list[str] = []
    match = CREATE_RE.search(statement)
    body_start = statement.find("(", match.end())
    if body_start < 0:
        return [f"{table}: 无法定位表定义"]

    body_info = find_body(statement, body_start)
    if body_info is None:
        return [f"{table}: 括号不闭合，无法解析"]

    body, body_end = body_info
    columns = parse_columns(body)
    if not columns:
        return [f"{table}: 未解析到字段定义"]

    if not IDENTIFIER_RE.fullmatch(table):
        errors.append(f"{table}: 表名须为小写字母、数字、下划线且不以数字开头")

    by_lower = {name.lower(): definition for name, definition in columns.items()}

    for name, rule in REQUIRED_COLUMNS.items():
        definition = by_lower.get(name)
        if definition is None:
            errors.append(f"{table}.{name}: 缺失必填字段")
            continue
        upper = definition.upper()
        type_name = str(rule["type"])
        if not re.search(rf"\b{type_name}\b", upper):
            errors.append(f"{table}.{name}: 类型应为 {type_name}")
        for flag in rule.get("flags", ()):
            if flag not in upper:
                errors.append(f"{table}.{name}: 缺少 {flag}")
        default = rule.get("default")
        if default and not re.search(rf"\bDEFAULT\s+{default}\b", upper):
            errors.append(f"{table}.{name}: 默认值应为 {default}")
        on_update = rule.get("on_update")
        if on_update and not re.search(rf"\bON\s+UPDATE\s+{on_update}\b", upper):
            errors.append(f"{table}.{name}: 缺少 ON UPDATE {on_update}")

    for name, definition in columns.items():
        upper = definition.upper()
        if not IDENTIFIER_RE.fullmatch(name):
            errors.append(f"{table}.{name}: 字段名须为小写字母、数字、下划线且不以数字开头")
        for forbidden in FORBIDDEN_TYPES:
            if re.search(rf"\b{forbidden}\b", upper):
                errors.append(f"{table}.{name}: 禁止使用 {forbidden}")
        if "COMMENT" not in upper:
            errors.append(f"{table}.{name}: 缺少 COMMENT")

    tail = statement[body_end + 1 :].upper().replace(" ", "")
    if "ENGINE=INNODB" not in tail:
        errors.append(f"{table}: 引擎须为 InnoDB")
    if "CHARSET=UTF8MB4" not in tail:
        errors.append(f"{table}: 字符集须为 utf8mb4")
    if "COMMENT=" not in tail:
        errors.append(f"{table}: 缺少表级 COMMENT")
    if re.search(r"\bFOREIGN\s+KEY\b", statement, re.IGNORECASE):
        errors.append(f"{table}: 禁止物理外键 FOREIGN KEY")

    return errors


def validate_file(path: Path) -> list[str]:
    """校验文件内所有 CREATE TABLE 语句。"""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path}: 读取失败: {exc}"]

    errors: list[str] = []
    table_count = 0
    for raw in sqlparse.split(content):
        parsed = sqlparse.parse(raw)
        if not parsed:
            continue
        statement_text = str(parsed[0])
        match = CREATE_RE.search(statement_text)
        if not match:
            continue
        table_count += 1
        errors.extend(validate_table(match.group(1), statement_text))

    if table_count == 0:
        errors.append(f"{path}: 未找到 CREATE TABLE 语句")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("用法: uv run python scripts/validater.py <ddl_file> [ddl_file ...]")
        return 2

    total_errors = 0
    for raw_path in argv[1:]:
        path = Path(raw_path)
        errors = validate_file(path)
        if errors:
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
            total_errors += len(errors)
        else:
            print(f"PASS {path}")

    if total_errors:
        print(f"\n共 {total_errors} 项未通过")
        return 1

    print("\n全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
