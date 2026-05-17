#!/usr/bin/env python3
"""
读取 indicators 目录下的 CSV 文件，提取去重后的指标名称，
合并到 references/indicators_dict.md 中。

目录约定（--dir 为数据存储根目录）：
    {dir}/indicators/  — markdown_2_indicators.py 输出的 CSV 文件

用法:
    uv run python scripts/refresh_indicators.py --dir /path/to/data
"""

import argparse
import csv
import os
import sys
from pathlib import Path

from config import SKILL_ROOT_DIR, setup_logger, logging


def extract_indicators_from_csv(csv_file: Path) -> set:
    """从 CSV 文件中提取指标名称（第三列）"""
    indicators = set()
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return indicators
            col_index = None
            for i, col in enumerate(header):
                if col.strip() == "指标项":
                    col_index = i
                    break
            if col_index is None:
                logger.warning(f"  {csv_file.name}: 未找到'指标项'列，表头={header}")
                return indicators
            for row in reader:
                if len(row) > col_index:
                    val = row[col_index].strip()
                    if val:
                        indicators.add(val)
    except Exception as e:
        logger.error(f"  读取 {csv_file.name} 失败: {e}")
    return indicators


def load_existing_indicators(dict_file: Path) -> set:
    """从 indicators_dict.md 加载已有指标"""
    if not dict_file.exists():
        return set()
    indicators = set()
    in_block = False
    with open(dict_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if "```properties" in stripped:
                in_block = True
                continue
            if in_block and stripped == "```":
                in_block = False
                continue
            if in_block and stripped:
                # 支持 key=value 或纯名称两种格式
                if "=" in stripped:
                    key = stripped.split("=", 1)[0].strip()
                    indicators.add(key)
                else:
                    indicators.add(stripped)
    return indicators


def update_dict_file(dict_file: Path, new_indicators: set) -> None:
    """将新指标追加到 indicators_dict.md 的 properties 代码块中"""
    if not new_indicators:
        return

    content = ""
    if dict_file.exists():
        content = dict_file.read_text(encoding="utf-8")

    in_block = False
    lines = content.split("\n") if content else ["# 指标库定义", "", "定义全局的指标库，如果不在指标库中的指标，暂时不以与归档。", "", "### 指标库", "", "```properties", "", "```"]
    insert_pos = -1

    for i, line in enumerate(lines):
        if "```properties" in line:
            in_block = True
            continue
        if in_block and line.strip() == "```":
            insert_pos = i
            in_block = False
            break

    if insert_pos < 0:
        logger.error("  未在 indicators_dict.md 中找到 ```properties 代码块")
        return

    for ind in sorted(new_indicators):
        lines.insert(insert_pos, ind)
        insert_pos += 1

    dict_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="从 indicators 目录的 CSV 中提取指标名称，合并到指标字典",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例: %(prog)s --dir /tmp/mydata",
    )
    parser.add_argument("--dir", required=False, help="数据存储根目录路径")
    args = parser.parse_args()

    ROOT_DIR = Path(args.dir) if args.dir else Path(os.getcwd()).resolve()
    if not ROOT_DIR.exists():
        logger.warning(f"错误: 目录不存在: {ROOT_DIR}")
        sys.exit(1)

    INDICATORS_DIR = ROOT_DIR / "indicators"
    if not INDICATORS_DIR.exists():
        logger.warning(f"indicators 目录不存在: {INDICATORS_DIR}")
        sys.exit(1)

    DICT_FILE = SKILL_ROOT_DIR / "references" / "indicators_dict.md"

    csv_files = sorted(INDICATORS_DIR.glob("*.csv"))
    if not csv_files:
        logger.warning(f"未在 {INDICATORS_DIR} 中找到 .csv 文件")
        sys.exit(0)

    all_indicators = set()
    for csv_file in csv_files:
        extracted = extract_indicators_from_csv(csv_file)
        logger.info(f"  {csv_file.name}: {len(extracted)} 个指标")
        all_indicators.update(extracted)

    existing = load_existing_indicators(DICT_FILE)
    new_indicators = all_indicators - existing

    logger.info(f"\n指标统计:")
    logger.info(f"  提取总数: {len(all_indicators)}")
    logger.info(f"  已有: {len(existing)}")
    logger.info(f"  新增: {len(new_indicators)}")

    if new_indicators:
        update_dict_file(DICT_FILE, new_indicators)
        logger.info(f"  已更新: {DICT_FILE}")
        for ind in sorted(new_indicators):
            logger.info(f"    + {ind}")


if __name__ == "__main__":
    logger = setup_logger(level=logging.INFO)
    main()
