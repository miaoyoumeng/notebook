#!/usr/bin/env python3
"""
从数据存储目录读取 markdown 文件，提交给 claude_agent_sdk 识别数据指标，
输出到 indicators/indicators.csv。

目录约定（--dir 为数据存储根目录）：
    {dir}/markdowns/    — 输入的 markdown 文件
    {dir}/logs/         — 运行日志
    {dir}/indicators/       — 输出的指标数据

用法:
    uv run python scripts/markdown_2_indicators.py --dir /path/to/data
"""

import argparse
import asyncio
import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict
import logging

from config import setup_logger

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


def process_markdown_file(md_file: Path) -> Dict:
    """读取 markdown 文件，返回 {path, title, content}"""
    content = md_file.read_text(encoding="utf-8")
    title = ""
    for line in content.split("\n")[:5]:
        line_stripped = line.strip()
        if line_stripped.startswith("# "):
            title = line_stripped.lstrip("# ").strip()
            break
    if not title:
        title = md_file.stem
    return {"path": str(md_file), "title": title, "content": content}


async def extract_indicators(data: Dict, project_dir: str) -> str:
    """调用 claude_agent_sdk 识别 markdown 内容中的数据指标"""
    if not data or not data.get("content"):
        return ""

    prompt = f"""请从以下 markdown 内容中识别所有数据指标，以 TSV 格式（Tab-Separated Values）逐行输出：

时间\t区域\t指标项\t指标值\t数据来源

## 输出规则
- 不要输出表头或其他任何解释，仅输出数据行
- 如果内容中没有"区域"字段，默认填写"全国"
- 指标项命名规则："抓取文章的标题" + "指标项"，去掉标题中的`日期`、`区域`，`统计年鉴`，保留其他内容，保证可读性
- 如果markdown中的指标明显是树形的，则需要按照树层级拼接成新的指标名称，如下面情况
```
指标项| 值
---|---
就业人数       | 18034
   第一产业    | 800
   第二产业    | 500
   第三产业    | 534
```
则输出指标：第一产业就业人数， 第二产业就业人数，第三产业就业人数

- 数据来源填写 markdown 中出现的原始 URL，若无则填空

## 输出示例

```
时间,区域,指标项,指标值,来源网址
2014,北京市,从业人员,7087922,https://nj.tjj.beijing.gov.cn/nj/main/2015-tjnj/zk/e/html/ch03-20.jpg
2014,北京市,从业人员增速,101.9,https://nj.tjj.beijing.gov.cn/nj/main/2015-tjnj/zk/e/html/ch03-20.jpg
```

## 文章标题
{data['title']}

## 需要解析的内容
{data['content']}"""

    result = ""
    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                cwd=project_dir,
                system_prompt={"type": "preset", "preset": "claude_code"},
                allowed_tools=["Read", "Glob", "Grep", "WebFetch", "Bash"],
                permission_mode="bypassPermissions",
                max_turns=10,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        result += block.text
    except Exception as e:
        logger.error(f"Error: {e}", file=sys.stderr)
        return ""
    return result.strip()


def is_md5_processed(log_file: Path, md5: str) -> bool:
    """检查 md5 是否已在日志中"""
    if not log_file.exists():
        return False
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() == md5:
                return True
    return False


def append_to_log(log_file: Path, md5: str) -> None:
    """将 md5 追加到日志"""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(md5 + "\n")


def write_tsv_line(output_indicators_csv: Path, time_val: str, region: str, indicator: str, value: str, source: str) -> None:
    """追加一行到输出 CSV"""
    write_header = not output_indicators_csv.exists() or output_indicators_csv.stat().st_size == 0
    with open(output_indicators_csv, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["时间", "区域", "指标项", "指标值", "来源网址"])
        writer.writerow([time_val, region, indicator, value, source])


def main():
    parser = argparse.ArgumentParser(
        description="从数据存储目录读取 markdown 文件，识别数据指标",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例: %(prog)s --dir /tmp/mydata",
    )
    parser.add_argument("--dir", required=False, help="数据存储根目录路径")
    args = parser.parse_args()

    ROOT_DIR: str = args.dir if args.dir else str(Path(os.getcwd()).resolve())
    PROJECT_ROOT_DIR = Path(ROOT_DIR)
    if not PROJECT_ROOT_DIR.exists():
        logger.warning(f"错误: 目录不存在: {PROJECT_ROOT_DIR}")
        sys.exit(1)

    MARKDOWNS_DIR = PROJECT_ROOT_DIR / "markdowns"
    if not MARKDOWNS_DIR.exists():
        logger.warning(f"错误: markdown 目录不存在: {MARKDOWNS_DIR}")
        sys.exit(1)

    LOGS_DIR = PROJECT_ROOT_DIR / "logs"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE = LOGS_DIR / "processed_md5.log"

    OUTPUT_INDICATORS_DIR = PROJECT_ROOT_DIR / "indicators"
    OUTPUT_INDICATORS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_INDICATORS_CSV = OUTPUT_INDICATORS_DIR / "indicators.csv"

    md_files = sorted(MARKDOWNS_DIR.glob("*.md"))
    if not md_files:
        logger.warning(f"未在 {MARKDOWNS_DIR} 中找到 .md 文件")
        sys.exit(0)

    logger.info(f"找到 {len(md_files)} 个 markdown 文件")

    total = 0
    skipped = 0
    errors = 0

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        md5 = hashlib.md5(content.encode("utf-8")).hexdigest()

        if is_md5_processed(LOG_FILE, md5):
            skipped += 1
            continue

        total += 1
        logger.info(f"  [{total}] 处理: {md_file.name}")

        try:
            data = process_markdown_file(md_file)
            result = asyncio.run(extract_indicators(data, ROOT_DIR))

            if not result:
                logger.info(f"    未提取到数据")
                append_to_log(LOG_FILE, md5)
                continue

            lines = result.strip().split("\n")
            row_count = 0
            for line in lines:
                parts = line.split("\t")
                if len(parts) >= 4:
                    time_val = parts[0].strip()
                    region = parts[1].strip() if parts[1].strip() else "全国"
                    indicator = parts[2].strip()
                    value = parts[3].strip()
                    source = parts[4].strip() if len(parts) > 4 else ""
                    if time_val and indicator:
                        write_tsv_line(OUTPUT_INDICATORS_CSV, time_val, region, indicator, value, source)
                        row_count += 1
            logger.info(f"    提取 {row_count} 条记录")

        except Exception as e:
            logger.error(f"    错误: {e}", file=sys.stderr)
            errors += 1

        append_to_log(LOG_FILE, md5)
        break

    logger.info(f"\n完成: 总数{len(md_files)}个, 处理 {total} 个, 跳过 {skipped} 个, 错误 {errors} 个")
    logger.info(f"输出: {OUTPUT_INDICATORS_CSV}")


if __name__ == "__main__":
    logger = setup_logger(level = logging.INFO)
    main()
