#!/usr/bin/env python3
"""
检查 markdown 文件是否符合预期格式，统计匹配数量。

格式要求（前五行）：
  第1行: 空行
  第2行: 以 "#" 开头，以 "统计年鉴。" 结尾
  第3行: 以 "- 这是 " 开头，以 "的数据。" 结尾
  第4行: 以 "- 数据来源地址：" 开头
  第5行: 精确匹配 "- 具体数据如下显示"

用法:
    uv run python scripts/stats.py --dir /path/to/data
"""

import argparse
import os
import sys
from pathlib import Path

from config import setup_logger, logging


def transform_file(file_path: Path) -> None:
    """检查格式，匹配则将前6行变换后追加到末尾，并删除原有前6行"""
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    if len(lines) < 6:
        return

    # 检查格式
    if (
        lines[0].strip() == ""
        and lines[1].startswith("#")
        and lines[1].strip().endswith("统计年鉴。")
        and lines[2].startswith("- 这是 ")
        and lines[2].strip().endswith("的数据。")
        and lines[3].startswith("- 数据来源地址：")
        and lines[4].strip() == "- 具体数据如下显示"
        and lines[5].strip() == ""
    ):
        # 提取第2行 # 后的内容
        rest_of_line2 = lines[1].strip()[1:].strip()
        # 构造变换后的块
        transformed = [
            "",
            f"# 上面内容是 {rest_of_line2}",
            lines[2],
            lines[3],
            "",  # 删除了原第5行，第6行空行保留
        ]
        # 追加到文件末尾
        remaining = lines[6:]
        new_content = "\n".join(remaining + transformed)

        # print(new_content)
        file_path.write_text(new_content, encoding="utf-8")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="检查 markdown 文件格式，变换头部信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例: %(prog)s --dir /tmp/mydata",
    )
    parser.add_argument("--dir", required=False, help="数据存储根目录路径")
    args = parser.parse_args()

    ROOT_DIR = Path(args.dir) if args.dir else Path(os.getcwd()).resolve()
    if not ROOT_DIR.exists():
        logger.warning(f"错误: 目录不存在: {ROOT_DIR}")
        sys.exit(1)

    MARKDOWNS_DIR = ROOT_DIR / "markdowns"
    if not MARKDOWNS_DIR.exists():
        logger.warning(f"markdown 目录不存在: {MARKDOWNS_DIR}")
        sys.exit(1)

    md_files = sorted(MARKDOWNS_DIR.glob("*.md"))
    if not md_files:
        logger.warning(f"未在 {MARKDOWNS_DIR} 中找到 .md 文件")
        sys.exit(0)

    matched = 0

    for md_file in md_files:
        if transform_file(md_file):
            matched += 1
            # break

    logger.info(f"总文件数: {len(md_files)}")
    logger.info(f"已处理: {matched}")


if __name__ == "__main__":
    logger = setup_logger(level=logging.INFO)
    main()
